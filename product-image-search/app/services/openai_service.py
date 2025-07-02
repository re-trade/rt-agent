# app/services/openai_service.py
import base64
from fastapi import HTTPException, UploadFile
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam
from app.config import settings

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.vision_model = "gpt-4o"

        self.system_message: ChatCompletionSystemMessageParam = {
            "role": "system",
            "content": (
                "Bạn là trợ lý AI nhận diện sản phẩm qua hình ảnh. "
                "Chỉ trả lời bằng tiếng Việt, ngắn gọn theo định dạng: '<Loại sản phẩm> <Thương hiệu>'. "
                "Ví dụ: 'Máy ảnh Canon', 'Điện thoại Samsung'. "
                "Nếu không rõ, trả lời: 'Không xác định'. "
                "Không giải thích thêm. Không viết hoa toàn bộ. Không có dấu chấm câu."
            )
        }

    async def analyze_image(self, image_file: UploadFile) -> str:
        try:
            image_bytes = await image_file.read()
            base64_image = base64.b64encode(image_bytes).decode("utf-8")

            messages: list[ChatCompletionMessageParam] = [
                self.system_message,
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Hình ảnh này là sản phẩm gì? "
                                "Hãy trả lời ngắn gọn theo định dạng '<Loại sản phẩm> <Thương hiệu>'. "
                                "Nếu không nhận ra thì ghi 'Không xác định'."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_file.content_type};base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=messages,
                max_tokens=50
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi phân tích hình ảnh: {str(e)}"
            )

openai_service = OpenAIService()
