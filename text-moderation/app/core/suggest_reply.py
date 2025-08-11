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
        "Cảm ơn bạn đã đánh giá tích cực! Mình rất vui khi bạn hài lòng với sản phẩm.",
        "Cảm ơn bạn đã ủng hộ! Hy vọng sẽ được phục vụ bạn trong những lần mua sắm tiếp theo.",
        "Mình rất cảm kích sự tin tưởng của bạn. Chúc bạn sử dụng sản phẩm vui vẻ!",
    ],
    "neutral": [
        "Cảm ơn bạn đã đánh giá! Mình sẽ cố gắng cải thiện chất lượng sản phẩm và dịch vụ.",
        "Mình ghi nhận ý kiến của bạn và sẽ khắc phục những điểm chưa tốt. Cảm ơn bạn!",
        "Cảm ơn phản hồi của bạn. Mình sẽ nỗ lực hơn để mang đến trải nghiệm tốt hơn.",
    ],
    "negative": [
        "Mình rất xin lỗi vì trải nghiệm chưa tốt. Vui lòng liên hệ để được hỗ trợ giải quyết.",
        "Mình chân thành xin lỗi và sẽ khắc phục vấn đề này. Vui lòng inbox để được hỗ trợ.",
        "Cảm ơn phản hồi của bạn. Mình sẽ cải thiện và bồi thường thỏa đáng cho bạn.",
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
    cache_key = (rating, review.strip() if review else "")
    if cache_key in _ai_cache:
        return _ai_cache[cache_key]

    prompt = (
        f"Bạn là một người bán hàng cá nhân trên mạng, không phải cửa hàng hay công ty. "
        f"KHÔNG được dùng từ 'shop' hoặc bất kỳ từ nào mang nghĩa cửa hàng. "
        f"Khách hàng vừa đánh giá {rating}/5 sao."
        + (f' Họ viết: \"{review}\".' if review else "")
        + " Chỉ trả về JSON dạng {\"replies\": [\"...\", \"...\", \"...\"]} "
          "với 3 câu trả lời ngắn gọn, thân thiện, tự nhiên, bằng tiếng Việt."
    )
    try:
        response = await client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            temperature=0.7,
        )

        text = (getattr(response, "output_text", None) or "").strip()
        if not text:
            raise ValueError("Empty AI response")

        import json
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{.*\}", text, re.S)
            if match:
                data = json.loads(match.group(0))
            else:
                raise
        suggestions = data.get("replies", [])
        if not isinstance(suggestions, list):
            raise ValueError("Invalid JSON format: 'replies' is not a list")

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
