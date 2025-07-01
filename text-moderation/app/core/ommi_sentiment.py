import logging
import time
import random
from os import getenv
from openai import OpenAI, APIConnectionError, APIError, RateLimitError

logger = logging.getLogger(__name__)
client = OpenAI(api_key=getenv("OPENAI_API_KEY", ""))

def sentiment_analysis(text: str, max_retries: int = 3):
    retry_count = 0
    base_delay = 1

    while retry_count < max_retries:
        try:
            response = client.moderations.create(input=text)
            break
        except APIConnectionError as e:
            retry_count += 1
            if retry_count == max_retries:
                logger.error(f"Connection error after {max_retries} retries: {str(e)}")
                raise Exception("Connection error. Please try again.") from e
            delay = base_delay * (2 ** (retry_count - 1)) + random.uniform(0, 0.5)
            logger.warning(f"Connection error, retrying in {delay:.2f}s...")
            time.sleep(delay)
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise Exception("Rate limit exceeded. Try again later.") from e
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise Exception("API error occurred.") from e
        except Exception as e:
            logger.exception("Unexpected error during sentiment analysis")
            raise Exception("Unexpected error occurred.") from e

    moderation_result = response.results[0]

    flagged_categories = {
        category: getattr(moderation_result.category_scores, category)
        for category, is_flagged in moderation_result.categories.__dict__.items()
        if is_flagged
    }

    return {
        "flagged": moderation_result.flagged,
        "flagged_categories": flagged_categories
    }
