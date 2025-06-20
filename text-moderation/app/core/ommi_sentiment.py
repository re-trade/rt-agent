import logging
import time
from os import getenv

from openai import APIConnectionError, APIError, OpenAI, RateLimitError

# Initialize logger
logger = logging.getLogger(__name__)

client = OpenAI(api_key=getenv('OPENAI_API_KEY', ''))

def sentiment_analysis(text: str, max_retries: int = 3):
    retry_count = 0
    base_delay = 1
    
    while retry_count < max_retries:
        try:
            response = client.moderations.create(
                input=text,
            )
            break
            
        except APIConnectionError as e:
            retry_count += 1
            if retry_count == max_retries:
                logger.error(f"Connection error after {max_retries} retries: {str(e)}")
                raise Exception("Connection error during sentiment analysis. Please try again later.") from e
            
            # Exponential backoff
            delay = base_delay * (2 ** (retry_count - 1))
            logger.warning(f"Connection error, retrying in {delay} seconds...")
            time.sleep(delay)
            
        except RateLimitError as e:
            logger.error(f"Rate limit exceeded: {str(e)}")
            raise Exception("Rate limit exceeded. Please try again later.") from e
            
        except APIError as e:
            logger.error(f"API error: {str(e)}")
            raise Exception("An error occurred during sentiment analysis.") from e
            
        except Exception as e:
            logger.error(f"Unexpected error during sentiment analysis: {str(e)}")
            raise Exception("An unexpected error occurred during sentiment analysis.") from e
    
    moderation_result = response.results[0]
    
    print(moderation_result)

    # Check if flagged
    flagged = moderation_result.flagged
    
    # Get flagged categories with confidence scores
    flagged_categories = {
        category: getattr(moderation_result.category_scores, category)
        for category, is_flagged in moderation_result.categories.__dict__.items()
        if is_flagged
    }

    return {
        "flagged": flagged,
        "flagged_categories": flagged_categories
    }

