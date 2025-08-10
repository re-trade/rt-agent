import logging
import random
from typing import List, Dict, Tuple
from openai import AsyncOpenAI
from app.config import settings
from app.core.models import FeedbackRequest

logger = logging.getLogger(__name__)
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

REPLIES = {
    "positive": [
        "Cảm ơn bạn đã đánh giá tích cực! Shop rất vui khi bạn hài lòng với sản phẩm.",
        "Cảm ơn bạn đã ủng hộ seller! Hy vọng sẽ được phục vụ bạn trong những lần mua sắm tiếp theo.",
        "Shop rất cảm kích sự tin tưởng của bạn. Chúc bạn sử dụng sản phẩm vui vẻ!",
    ],
    "neutral": [
        "Cảm ơn bạn đã đánh giá! Shop sẽ cố gắng cải thiện chất lượng sản phẩm và dịch vụ.",
        "Shop ghi nhận ý kiến của bạn và sẽ khắc phục những điểm chưa tốt. Cảm ơn bạn!",
        "Cảm ơn phản hồi của bạn. Shop sẽ nỗ lực hơn để mang đến trải nghiệm tốt hơn.",
    ],
    "negative": [
        "Shop rất xin lỗi vì trải nghiệm chưa tốt. Vui lòng liên hệ seller để được hỗ trợ giải quyết.",
        "Shop chân thành xin lỗi và sẽ khắc phục vấn đề này. Vui lòng inbox để seller hỗ trợ bạn.",
        "Cảm ơn phản hồi của bạn. Shop sẽ cải thiện và bồi thường thỏa đáng cho bạn.",
    ],
}

def get_hardcoded_replies(rating: float) -> List[str]:
    if rating >= 4:
        return REPLIES["positive"]
    elif rating >= 3:
        return REPLIES["neutral"]
    return REPLIES["negative"]

_ai_cache: Dict[Tuple[float, str], List[str]] = {}
async def get_ai_generated_replies(rating: float, review: str) -> List[str]:
    cache_key = (rating, review.strip())
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]
    prompt = (
        f"Bạn là người bán hàng online. Khách hàng vừa đánh giá {rating}/5 sao."
        + (f' Họ viết: "{review}".' if review else "")
        + " Hãy trả về JSON dạng {\"replies\": [\"...\", \"...\", \"...\"]} "
          "với 3 câu trả lời lịch sự, ngắn gọn, thân thiện, bằng tiếng Việt."
    )
    try:
        response = await client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
        )
        import json
        suggestions_text = response.output_text.strip()
        data = json.loads(suggestions_text)
        suggestions = data.get("replies", [])
        _ai_cache[cache_key] = suggestions
        return suggestions
    except Exception as e:
        logger.error(f"AI reply generation failed: {e}")
        return get_hardcoded_replies(rating)


async def get_suggestions(data: FeedbackRequest) -> List[str]:
    if data.review and data.review.strip():
        return await get_ai_generated_replies(data.rating, data.review)
    return get_hardcoded_replies(data.rating)

def get_random_suggestion(suggestions: List[str]) -> str:
    return random.choice(suggestions)
