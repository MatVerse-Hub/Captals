#!/usr/bin/env python3
"""
Twitter Bot for MatVerse-Copilot
Posts tweets using Twitter API v2
"""

import os
import logging
from dotenv import load_dotenv

try:
    import tweepy
except ImportError:
    tweepy = None

load_dotenv()

logger = logging.getLogger('TwitterBot')


class TwitterBot:
    """Handles Twitter posting."""

    def __init__(self):
        self.enabled = False
        self.client = None

        # Load credentials
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_secret = os.getenv('TWITTER_ACCESS_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

        if not tweepy:
            logger.warning("tweepy not installed. Twitter posting disabled.")
            return

        if not all([api_key, api_secret, access_token, access_secret]):
            logger.warning("Twitter credentials not configured. Posting disabled.")
            return

        try:
            # Create Twitter client (API v2)
            self.client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret
            )

            # Verify credentials
            me = self.client.get_me()
            if me.data:
                logger.info(f"Twitter bot authenticated as: @{me.data.username}")
                self.enabled = True
            else:
                logger.warning("Twitter authentication failed")

        except Exception as e:
            logger.error(f"Failed to initialize Twitter bot: {e}")

    def post_tweet(self, text, image_path=None):
        """
        Post a tweet.

        Args:
            text: Tweet text (max 280 characters)
            image_path: Optional path to image to attach

        Returns:
            Dictionary with tweet URL and ID
        """
        if not self.enabled:
            logger.warning("Twitter bot not enabled. Skipping tweet.")
            return {'error': 'Twitter bot not enabled'}

        try:
            # Truncate text if too long
            if len(text) > 280:
                text = text[:277] + "..."

            # Post tweet
            response = self.client.create_tweet(text=text)

            if response.data:
                tweet_id = response.data['id']
                # Get authenticated user for URL
                me = self.client.get_me()
                username = me.data.username

                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

                logger.info(f"Tweet posted: {tweet_url}")

                return {
                    'success': True,
                    'tweet_id': tweet_id,
                    'tweet_url': tweet_url
                }
            else:
                return {'error': 'Failed to post tweet'}

        except Exception as e:
            logger.error(f"Failed to post tweet: {str(e)}", exc_info=True)
            return {'error': str(e)}

    def post_with_media(self, text, image_path):
        """
        Post a tweet with an image.

        Note: Twitter API v2 media upload requires additional setup.
        Using v1.1 API for media upload.
        """
        if not self.enabled:
            return {'error': 'Twitter bot not enabled'}

        try:
            # For media upload, we need API v1.1
            api_key = os.getenv('TWITTER_API_KEY')
            api_secret = os.getenv('TWITTER_API_SECRET')
            access_token = os.getenv('TWITTER_ACCESS_TOKEN')
            access_secret = os.getenv('TWITTER_ACCESS_SECRET')

            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_secret)
            api = tweepy.API(auth)

            # Upload media
            media = api.media_upload(filename=str(image_path))

            # Post tweet with media using v2 client
            response = self.client.create_tweet(
                text=text,
                media_ids=[media.media_id]
            )

            if response.data:
                tweet_id = response.data['id']
                me = self.client.get_me()
                username = me.data.username
                tweet_url = f"https://twitter.com/{username}/status/{tweet_id}"

                logger.info(f"Tweet with media posted: {tweet_url}")

                return {
                    'success': True,
                    'tweet_id': tweet_id,
                    'tweet_url': tweet_url
                }

        except Exception as e:
            logger.error(f"Failed to post tweet with media: {e}")
            return {'error': str(e)}
