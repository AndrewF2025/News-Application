"""
Twitter integration service for the Commerce App.

This module handles tweeting about new stores and products.
"""
import logging
import os
from typing import Optional

import tweepy
from django.conf import settings

logger = logging.getLogger(__name__)


class TwitterService:
    """Service class for Twitter API integration."""

    def __init__(self):
        """Initialize the Twitter service with API credentials."""
        self.enabled = getattr(settings, 'TWITTER_ENABLED', False)

        if not self.enabled:
            logger.info("Twitter integration is disabled")
            return

        # Initialize Twitter API client
        try:
            self.client = tweepy.Client(
                bearer_token=getattr(settings, 'TWITTER_BEARER_TOKEN', ''),
                consumer_key=getattr(settings, 'TWITTER_API_KEY', ''),
                consumer_secret=getattr(settings, 'TWITTER_API_SECRET', ''),
                access_token=getattr(settings, 'TWITTER_ACCESS_TOKEN', ''),
                access_token_secret=getattr(
                    settings, 'TWITTER_ACCESS_TOKEN_SECRET', ''
                )
            )

            # Initialize API v1.1 client for media upload
            auth = tweepy.OAuth1UserHandler(
                getattr(settings, 'TWITTER_API_KEY', ''),
                getattr(settings, 'TWITTER_API_SECRET', ''),
                getattr(settings, 'TWITTER_ACCESS_TOKEN', ''),
                getattr(settings, 'TWITTER_ACCESS_TOKEN_SECRET', '')
            )
            self.api_v1 = tweepy.API(auth)

            logger.info("Twitter API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter API client: {e}")
            self.enabled = False
            self.client = None
            self.api_v1 = None

    def tweet_new_article(
        self, title: str, description: str, author_name: str
    ) -> bool:
        """
        Tweet about a new article being published.

        :param title: Title of the article
        :param description: Description or summary of the article
        :param author_name: Name of the author
        :return: True if tweet was successful, False otherwise
        """
        if not self.enabled or not self.client:
            logger.warning("Twitter integration is not available")
            return False

        try:
            hashtags = getattr(
                settings, 'TWITTER_HASHTAGS', '#news #article'
            )
            desc_short = description[:100]
            desc_ellipsis = '...' if len(description) > 100 else ''
            tweet_text = (
                f"📰 New article published: '{title}'\n\n"
                f"📝 {desc_short}{desc_ellipsis}\n"
                f"👤 Author: {author_name}\n\n"
                f"Read now! {hashtags}"
            )

            if len(tweet_text) > 280:
                available_chars = (
                    280 - len(tweet_text) + len(desc_short)
                )
                if available_chars > 10:
                    truncated_desc = description[:available_chars-10] + '...'
                    tweet_text = (
                        f"📰 New article published: '{title}'\n\n"
                        f"📝 {truncated_desc}\n"
                        f"👤 Author: {author_name}\n\n"
                        f"Read now! {hashtags}"
                    )
                else:
                    tweet_text = (
                        f"📰 Article '{title}' by {author_name}. "
                        f"{hashtags}"
                    )

            self.client.create_tweet(text=tweet_text)
            logger.info(f"Successfully tweeted about new article: {title}")
            return True

        except Exception as e:
            logger.error(f"Failed to tweet about new article '{title}': {e}")
            return False

    def tweet_new_newsletter(
        self, title: str, description: str, author_name: str,
        image_path: Optional[str] = None
    ) -> bool:
        """
        Tweet about a new newsletter being published.

        :param title: Title of the newsletter
        :param description: Description or summary of the newsletter
        :param author_name: Name of the author
        :param image_path: Path to the newsletter image (optional)
        :return: True if tweet was successful, False otherwise
        """
        if not self.enabled or not self.client:
            logger.warning("Twitter integration is not available")
            return False

        try:
            hashtags = getattr(
                settings, 'TWITTER_HASHTAGS', '#news #newsletter'
            )
            desc_short = description[:100]
            desc_ellipsis = '...' if len(description) > 100 else ''
            tweet_text = (
                f"📢 New newsletter: '{title}'\n\n"
                f"📝 {desc_short}{desc_ellipsis}\n"
                f"👤 Author: {author_name}\n\n"
                f"Subscribe now! {hashtags}"
            )

            if len(tweet_text) > 280:
                available_chars = (
                    280 - len(tweet_text) + len(desc_short)
                )
                if available_chars > 10:
                    truncated_desc = description[:available_chars-10] + '...'
                    tweet_text = (
                        f"📢 New newsletter: '{title}'\n\n"
                        f"📝 {truncated_desc}\n"
                        f"👤 Author: {author_name}\n\n"
                        f"Subscribe now! {hashtags}"
                    )
                else:
                    tweet_text = (
                        f"📢 Newsletter '{title}' by {author_name}. "
                        f"{hashtags}"
                    )

            media_ids = []
            if image_path and self.api_v1:
                try:
                    if hasattr(settings, 'MEDIA_ROOT'):
                        full_image_path = os.path.join(
                            settings.MEDIA_ROOT, image_path
                        )
                    else:
                        full_image_path = image_path
                    if os.path.exists(full_image_path):
                        media = self.api_v1.media_upload(full_image_path)
                        media_ids.append(media.media_id)
                        logger.info(
                            f"Successfully uploaded image for newsletter: "
                            f"{title}"
                        )
                    else:
                        logger.warning(
                            f"Image file not found: {full_image_path}"
                        )
                except Exception as e:
                    logger.error(
                        f"Failed to upload image for newsletter '{title}': "
                        f"{e}"
                    )
            if media_ids:
                self.client.create_tweet(
                    text=tweet_text, media_ids=media_ids
                )
                logger.info(
                    f"Successfully tweeted about new newsletter with image: "
                    f"{title}"
                )
            else:
                self.client.create_tweet(text=tweet_text)
                logger.info(
                    f"Successfully tweeted about new newsletter: {title}"
                )
            return True
        except Exception as e:
            logger.error(
                f"Failed to tweet about new newsletter '{title}': {e}"
            )
            return False


# Global instance of the Twitter service
twitter_service = TwitterService()
