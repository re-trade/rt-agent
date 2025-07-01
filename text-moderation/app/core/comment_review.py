import asyncio
from pathlib import Path
from .offfensive_detect import OffensiveDetect
from .ommi_sentiment import sentiment_analysis
from .models import Review

current_dir = Path(__file__).parent
data_dir = current_dir / "data" 

offensive_filter = OffensiveDetect(data_dir / "vn_offensive_words.txt")

async def review_comment(comment: str) -> Review:
    """
    Asynchronously reviews a comment for offensive content and sentiment.
    Args:
        comment (str): The comment text to be reviewed.
    Returns:
        Review: An object containing the review status and message.
    Raises:
        Exception: If there is an error during sentiment analysis.
    The function performs the following checks:
    1. Checks for offensive words using a cached filter.
    2. Performs sentiment analysis on the comment.
    3. Flags the comment for moderation if it has an invalid attitude.
    """

    if offensive_filter.contains_prohibited_words(comment):
        return Review(status=False, message="Comment contains offensive words.")

    try:
        sentiment = await asyncio.to_thread(sentiment_analysis, comment)
    except Exception as e:
        raise Exception(f"Error during sentiment analysis: {str(e)}")
    
    if sentiment.get("flagged", False):
        return Review(status=False, message="Comment has some categories not valid: " + str(sentiment["flagged_categories"]))

    return Review(status=True, message="Comment is valid.")