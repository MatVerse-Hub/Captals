#!/usr/bin/env python3
"""
Deployer for MatVerse-Copilot
Handles automated deployments to various platforms
"""

import os
import logging
import subprocess
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()

logger = logging.getLogger('Deployer')


class Deployer:
    """Handles deployments to multiple platforms."""

    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.github_username = os.getenv('GITHUB_USERNAME', 'MatVerse-Hub')
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN')
        self.hf_username = os.getenv('HUGGINGFACE_USERNAME', 'MatVerse')
        self.vercel_token = os.getenv('VERCEL_TOKEN')

    def deploy_paper(self, pdf_path):
        """
        Deploy a paper to GitHub and arXiv.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Dictionary with deployment results
        """
        results = {}

        # Deploy to GitHub
        github_result = self._deploy_to_github(pdf_path)
        results['github'] = github_result

        # Deploy to arXiv (if configured)
        if os.getenv('ARXIV_USERNAME'):
            arxiv_result = self._deploy_to_arxiv(pdf_path)
            results['arxiv'] = arxiv_result

        return results

    def _deploy_to_github(self, file_path):
        """Deploy file to GitHub repository."""
        if not self.github_token:
            return {'error': 'GitHub token not configured'}

        try:
            # Use git commands to commit and push
            file_name = Path(file_path).name

            # Copy file to repo (assuming we're in a git repo)
            import shutil
            dest_path = Path.cwd() / 'papers' / file_name
            dest_path.parent.mkdir(exist_ok=True)
            shutil.copy(file_path, dest_path)

            # Git add, commit, push
            subprocess.run(['git', 'add', str(dest_path)], check=True)
            subprocess.run(
                ['git', 'commit', '-m', f'Add paper: {file_name}'],
                check=True
            )
            subprocess.run(['git', 'push'], check=True)

            logger.info(f"Deployed to GitHub: {file_name}")

            return {
                'success': True,
                'path': str(dest_path),
                'message': 'Deployed to GitHub'
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"GitHub deployment failed: {e}")
            return {'error': str(e)}

    def _deploy_to_arxiv(self, pdf_path):
        """
        Submit to arXiv via FTP.

        Note: arXiv requires specific formatting and metadata.
        This is a simplified version.
        """
        username = os.getenv('ARXIV_USERNAME')
        password = os.getenv('ARXIV_PASSWORD')

        if not username or not password:
            return {'error': 'arXiv credentials not configured'}

        # In production, use ftplib to upload to arXiv
        logger.info(f"arXiv submission simulated for {pdf_path}")

        return {
            'success': True,
            'message': 'arXiv submission simulated (requires manual submission in production)'
        }

    def deploy_to_huggingface(self, model_path, repo_name):
        """
        Deploy a model to HuggingFace Hub.

        Args:
            model_path: Path to model directory
            repo_name: Name of the HuggingFace repository

        Returns:
            Dictionary with deployment result
        """
        if not self.hf_token:
            return {'error': 'HuggingFace token not configured'}

        try:
            from huggingface_hub import HfApi, create_repo

            api = HfApi(token=self.hf_token)

            # Create repo if it doesn't exist
            repo_id = f"{self.hf_username}/{repo_name}"

            try:
                create_repo(repo_id, token=self.hf_token, exist_ok=True)
            except Exception as e:
                logger.warning(f"Repo creation: {e}")

            # Upload files
            api.upload_folder(
                folder_path=model_path,
                repo_id=repo_id,
                token=self.hf_token
            )

            logger.info(f"Deployed to HuggingFace: {repo_id}")

            return {
                'success': True,
                'repo_id': repo_id,
                'url': f"https://huggingface.co/{repo_id}"
            }

        except ImportError:
            return {'error': 'huggingface_hub not installed'}
        except Exception as e:
            logger.error(f"HuggingFace deployment failed: {e}")
            return {'error': str(e)}

    def deploy_to_vercel(self, project_path):
        """
        Deploy a project to Vercel.

        Args:
            project_path: Path to project directory

        Returns:
            Dictionary with deployment result
        """
        if not self.vercel_token:
            return {'error': 'Vercel token not configured'}

        try:
            # Use Vercel CLI
            result = subprocess.run(
                ['vercel', '--token', self.vercel_token, '--prod'],
                cwd=project_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                url = result.stdout.strip().split('\n')[-1]

                logger.info(f"Deployed to Vercel: {url}")

                return {
                    'success': True,
                    'url': url
                }
            else:
                return {'error': result.stderr}

        except FileNotFoundError:
            return {'error': 'Vercel CLI not installed'}
        except Exception as e:
            logger.error(f"Vercel deployment failed: {e}")
            return {'error': str(e)}

    def deploy_to_opensea(self, nft_data):
        """
        Update NFT metadata on OpenSea.

        Args:
            nft_data: Dictionary with NFT contract and token ID

        Returns:
            Dictionary with result
        """
        api_key = os.getenv('OPENSEA_API_KEY')

        if not api_key:
            return {'error': 'OpenSea API key not configured'}

        try:
            # Use OpenSea API to refresh metadata
            url = "https://testnets-api.opensea.io/api/v2/chain/amoy/contract/{}/nfts/{}/refresh".format(
                nft_data['contract'],
                nft_data['token_id']
            )

            headers = {
                'X-API-KEY': api_key
            }

            response = requests.post(url, headers=headers)

            if response.status_code == 200:
                logger.info(f"OpenSea metadata refreshed for token {nft_data['token_id']}")

                return {
                    'success': True,
                    'message': 'Metadata refresh requested'
                }
            else:
                return {'error': f'HTTP {response.status_code}'}

        except Exception as e:
            logger.error(f"OpenSea update failed: {e}")
            return {'error': str(e)}
