#!/usr/bin/env python3
"""
MatVerse-Copilot Queue Monitor
Watches ~/deploy-queue/ for new files and triggers deployments
"""

import os
import time
import logging
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

from .nft_minter import NFTMinter
from .twitter_bot import TwitterBot
from .deployer import Deployer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MatVerse-Monitor')


class DeployQueueHandler(FileSystemEventHandler):
    """Handles file events in the deploy queue directory."""

    def __init__(self, queue_path):
        self.queue_path = Path(queue_path)
        self.nft_minter = NFTMinter()
        self.twitter_bot = TwitterBot()
        self.deployer = Deployer()
        self.processed_files = set()

    def on_created(self, event):
        """Called when a file or directory is created."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Avoid processing the same file multiple times
        if file_path in self.processed_files:
            return

        self.processed_files.add(file_path)

        # Wait a bit to ensure file is fully written
        time.sleep(0.5)

        logger.info(f"New file detected: {file_path.name}")
        self.process_file(file_path)

    def process_file(self, file_path):
        """Process a file based on its naming convention."""
        filename = file_path.name

        try:
            # Check if it's an immediate deployment (now_)
            if filename.startswith('now_'):
                self._process_immediate(file_path)

            # Check if it's a scheduled deployment (YYYY-MM-DD_HHhMM_)
            elif self._is_scheduled(filename):
                self._process_scheduled(file_path)

            else:
                logger.warning(f"Unknown file pattern: {filename}")

        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}", exc_info=True)

    def _process_immediate(self, file_path):
        """Process files with 'now_' prefix immediately."""
        filename = file_path.name

        # Extract action from filename
        # Examples: now_tweet.txt, now_test_nft.png, now_evidence-1_nft.png

        if '_tweet' in filename and filename.endswith('.txt'):
            # Twitter post
            with open(file_path, 'r') as f:
                content = f.read()
            result = self.twitter_bot.post_tweet(content)
            logger.info(f"Tweet posted: {result}")

        elif '_nft' in filename and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # NFT minting
            # Extract metadata from filename
            metadata = self._extract_nft_metadata(filename)
            result = self.nft_minter.mint_nft(file_path, metadata)
            logger.info(f"NFT minted: {result}")

        elif filename.endswith('.pdf'):
            # Paper deployment (arXiv, GitHub)
            result = self.deployer.deploy_paper(file_path)
            logger.info(f"Paper deployed: {result}")

        else:
            logger.warning(f"Unknown immediate action for: {filename}")

        # Archive processed file
        self._archive_file(file_path)

    def _process_scheduled(self, file_path):
        """Process scheduled deployments."""
        # Extract scheduled time from filename
        # Format: YYYY-MM-DD_HHhMM_name
        parts = file_path.name.split('_')

        try:
            date_str = parts[0]
            time_str = parts[1]
            scheduled_time = datetime.strptime(
                f"{date_str} {time_str.replace('h', ':')}",
                "%Y-%m-%d %H:%M"
            )

            # Check if it's time to deploy
            if datetime.now() >= scheduled_time:
                logger.info(f"Executing scheduled deployment: {file_path.name}")
                self._process_immediate(file_path)
            else:
                logger.info(f"Scheduled for {scheduled_time}: {file_path.name}")
                # TODO: Add to scheduler

        except (ValueError, IndexError) as e:
            logger.error(f"Invalid scheduled filename format: {file_path.name}")

    def _is_scheduled(self, filename):
        """Check if filename matches scheduled format."""
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}_\d{2}h\d{2}_'
        return bool(re.match(pattern, filename))

    def _extract_nft_metadata(self, filename):
        """Extract NFT metadata from filename."""
        # Example: now_evidence-001_nft.png
        metadata = {
            'name': 'MatVerse Evidence Note',
            'description': 'Auto-generated evidence note from MatVerse-Copilot',
            'collection': 'MatVerse Evidence Notes'
        }

        # Extract ID if present
        if 'evidence-' in filename:
            try:
                id_part = filename.split('evidence-')[1].split('_')[0]
                metadata['name'] = f"MatVerse Evidence Note #{id_part}"
                metadata['token_id'] = id_part
            except IndexError:
                pass

        return metadata

    def _archive_file(self, file_path):
        """Move processed file to archive."""
        archive_dir = self.queue_path / 'processed' / datetime.now().strftime('%Y-%m-%d')
        archive_dir.mkdir(parents=True, exist_ok=True)

        archive_path = archive_dir / file_path.name
        try:
            file_path.rename(archive_path)
            logger.info(f"Archived: {archive_path}")
        except Exception as e:
            logger.error(f"Failed to archive {file_path}: {e}")


class QueueMonitor:
    """Main queue monitor class."""

    def __init__(self, queue_path=None):
        self.queue_path = Path(queue_path or os.getenv('DEPLOY_QUEUE_PATH',
                                                        os.path.expanduser('~/deploy-queue')))
        self.queue_path.mkdir(parents=True, exist_ok=True)

        self.observer = Observer()
        self.handler = DeployQueueHandler(self.queue_path)

    def start(self):
        """Start monitoring the queue."""
        logger.info(f"Starting MatVerse-Copilot Monitor on {self.queue_path}")

        self.observer.schedule(self.handler, str(self.queue_path), recursive=False)
        self.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop monitoring."""
        logger.info("Stopping MatVerse-Copilot Monitor")
        self.observer.stop()
        self.observer.join()


if __name__ == '__main__':
    monitor = QueueMonitor()
    monitor.start()
