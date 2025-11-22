#!/usr/bin/env python3
"""
MatVerse-Copilot CLI
Command-line interface for managing the MatVerse-Copilot system
"""

import os
import sys
import signal
import psutil
import click
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Constants
PID_FILE = Path.home() / '.matverse-copilot.pid'
LOG_FILE = Path.home() / '.matverse-copilot.log'


@click.group()
@click.version_option(version='1.0.0')
def main():
    """MatVerse-Copilot - Automated deployment and NFT minting system."""
    pass


@main.command()
@click.option('--daemon', '-d', is_flag=True, help='Run in background as daemon')
def start(daemon):
    """Start the MatVerse-Copilot monitor."""
    if is_running():
        click.echo(f"{Fore.YELLOW}MatVerse-Copilot is already running (PID: {get_pid()})")
        return

    click.echo(f"{Fore.GREEN}Starting MatVerse-Copilot...")

    if daemon:
        # Start as daemon
        import subprocess
        import sys

        # Fork and run in background
        proc = subprocess.Popen(
            [sys.executable, '-m', 'src.monitor'],
            stdout=open(LOG_FILE, 'a'),
            stderr=subprocess.STDOUT,
            start_new_session=True
        )

        # Save PID
        PID_FILE.write_text(str(proc.pid))

        click.echo(f"{Fore.GREEN}✓ MatVerse-Copilot started in background (PID: {proc.pid})")
        click.echo(f"{Fore.CYAN}  Use 'matverse-copilot logs -f' to view logs")
    else:
        # Run in foreground
        from .monitor import QueueMonitor
        monitor = QueueMonitor()
        monitor.start()


@main.command()
def stop():
    """Stop the MatVerse-Copilot monitor."""
    if not is_running():
        click.echo(f"{Fore.YELLOW}MatVerse-Copilot is not running")
        return

    pid = get_pid()
    click.echo(f"{Fore.YELLOW}Stopping MatVerse-Copilot (PID: {pid})...")

    try:
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink(missing_ok=True)
        click.echo(f"{Fore.GREEN}✓ MatVerse-Copilot stopped")
    except ProcessLookupError:
        click.echo(f"{Fore.RED}Process not found. Cleaning up PID file...")
        PID_FILE.unlink(missing_ok=True)
    except Exception as e:
        click.echo(f"{Fore.RED}Error stopping process: {e}")


@main.command()
def restart():
    """Restart the MatVerse-Copilot monitor."""
    if is_running():
        stop.invoke(click.Context(stop))

    import time
    time.sleep(1)

    start.invoke(click.Context(start), daemon=True)


@main.command()
def status():
    """Show MatVerse-Copilot status."""
    click.echo(f"\n{Fore.CYAN}{'='*50}")
    click.echo(f"{Fore.CYAN}MatVerse-Copilot Status")
    click.echo(f"{Fore.CYAN}{'='*50}\n")

    if is_running():
        pid = get_pid()
        try:
            process = psutil.Process(pid)
            cpu = process.cpu_percent(interval=0.1)
            mem = process.memory_info().rss / 1024 / 1024  # MB

            click.echo(f"{Fore.GREEN}● Status: RUNNING")
            click.echo(f"{Fore.WHITE}  PID: {pid}")
            click.echo(f"{Fore.WHITE}  CPU: {cpu}%")
            click.echo(f"{Fore.WHITE}  Memory: {mem:.1f} MB")
            click.echo(f"{Fore.WHITE}  Uptime: {get_uptime(process)}")
        except psutil.NoSuchProcess:
            click.echo(f"{Fore.RED}● Status: NOT RUNNING (stale PID file)")
            PID_FILE.unlink(missing_ok=True)
    else:
        click.echo(f"{Fore.RED}● Status: NOT RUNNING")

    # Check queue directory
    from dotenv import load_dotenv
    load_dotenv()

    queue_path = Path(os.getenv('DEPLOY_QUEUE_PATH', os.path.expanduser('~/deploy-queue')))

    click.echo(f"\n{Fore.CYAN}Queue Information:")
    click.echo(f"{Fore.WHITE}  Path: {queue_path}")
    click.echo(f"{Fore.WHITE}  Exists: {Fore.GREEN if queue_path.exists() else Fore.RED}{queue_path.exists()}")

    if queue_path.exists():
        pending_files = list(queue_path.glob('*'))
        click.echo(f"{Fore.WHITE}  Pending files: {len([f for f in pending_files if f.is_file()])}")

    # Check configuration
    click.echo(f"\n{Fore.CYAN}Configuration:")
    env_file = Path('.env')
    click.echo(f"{Fore.WHITE}  .env file: {Fore.GREEN if env_file.exists() else Fore.RED}{env_file.exists()}")

    if env_file.exists():
        load_dotenv()
        click.echo(f"{Fore.WHITE}  Polygon RPC: {Fore.GREEN if os.getenv('POLYGON_RPC_URL') else Fore.RED}{'✓' if os.getenv('POLYGON_RPC_URL') else '✗'}")
        click.echo(f"{Fore.WHITE}  Wallet: {Fore.GREEN if os.getenv('WALLET_PRIVATE_KEY') else Fore.RED}{'✓' if os.getenv('WALLET_PRIVATE_KEY') else '✗'}")
        click.echo(f"{Fore.WHITE}  Twitter: {Fore.GREEN if os.getenv('TWITTER_API_KEY') else Fore.RED}{'✓' if os.getenv('TWITTER_API_KEY') else '✗'}")

    click.echo()


@main.command()
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
@click.option('--lines', '-n', default=50, help='Number of lines to show')
def logs(follow, lines):
    """Show MatVerse-Copilot logs."""
    if not LOG_FILE.exists():
        click.echo(f"{Fore.YELLOW}No log file found at {LOG_FILE}")
        return

    if follow:
        # Follow logs in real-time
        import subprocess
        subprocess.run(['tail', '-f', str(LOG_FILE)])
    else:
        # Show last N lines
        import subprocess
        result = subprocess.run(
            ['tail', '-n', str(lines), str(LOG_FILE)],
            capture_output=True,
            text=True
        )
        click.echo(result.stdout)


@main.command()
def queue():
    """Show current deployment queue."""
    from dotenv import load_dotenv
    load_dotenv()

    queue_path = Path(os.getenv('DEPLOY_QUEUE_PATH', os.path.expanduser('~/deploy-queue')))

    if not queue_path.exists():
        click.echo(f"{Fore.YELLOW}Queue directory does not exist: {queue_path}")
        return

    click.echo(f"\n{Fore.CYAN}Deployment Queue ({queue_path}):\n")

    files = sorted(queue_path.glob('*'), key=lambda f: f.stat().st_mtime)

    if not files:
        click.echo(f"{Fore.YELLOW}  (empty)")
    else:
        for i, file in enumerate(files, 1):
            if file.is_file():
                size = file.stat().st_size / 1024  # KB
                click.echo(f"{Fore.WHITE}{i}. {Fore.GREEN}{file.name}{Fore.WHITE} ({size:.1f} KB)")

    click.echo()


@main.command()
@click.argument('test_type', type=click.Choice(['nft', 'twitter', 'all']))
def test(test_type):
    """Run system tests."""
    click.echo(f"\n{Fore.CYAN}Running {test_type} test...\n")

    if test_type in ['nft', 'all']:
        click.echo(f"{Fore.YELLOW}Testing NFT minting...")
        from .nft_minter import NFTMinter
        minter = NFTMinter()
        if minter.check_connection():
            click.echo(f"{Fore.GREEN}✓ NFT system OK")
        else:
            click.echo(f"{Fore.RED}✗ NFT system failed")

    if test_type in ['twitter', 'all']:
        click.echo(f"{Fore.YELLOW}Testing Twitter bot...")
        from .twitter_bot import TwitterBot
        bot = TwitterBot()
        if bot.enabled:
            click.echo(f"{Fore.GREEN}✓ Twitter bot OK")
        else:
            click.echo(f"{Fore.RED}✗ Twitter bot not configured")

    click.echo()


# Helper functions

def is_running():
    """Check if MatVerse-Copilot is running."""
    if not PID_FILE.exists():
        return False

    try:
        pid = int(PID_FILE.read_text().strip())
        return psutil.pid_exists(pid)
    except (ValueError, ProcessLookupError):
        return False


def get_pid():
    """Get the PID of the running process."""
    if PID_FILE.exists():
        try:
            return int(PID_FILE.read_text().strip())
        except ValueError:
            return None
    return None


def get_uptime(process):
    """Get process uptime as a human-readable string."""
    import time
    uptime_seconds = time.time() - process.create_time()

    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)

    if days > 0:
        return f"{days}d {hours}h {minutes}m"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


if __name__ == '__main__':
    main()
