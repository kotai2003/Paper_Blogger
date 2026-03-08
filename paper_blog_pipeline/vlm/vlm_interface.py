"""VLM (Vision Language Model) インターフェース - Ollama経由で図の解析に使用"""

import base64
from pathlib import Path

from llm.ollama_client import call_vlm, DEFAULT_MODEL

MEDIA_TYPE_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}


class OllamaVLM:
    """Ollama VLM（OpenAI互換API経由）"""

    def __init__(self, model: str | None = None, base_url: str | None = None):
        self.model = model or DEFAULT_MODEL
        self.base_url = base_url

    def analyze_image(self, image_path: str, prompt: str) -> str:
        """画像を解析してテキスト説明を返す"""
        path = Path(image_path)
        media_type = MEDIA_TYPE_MAP.get(path.suffix.lower(), "image/png")

        with open(image_path, "rb") as f:
            image_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

        data_url = f"data:{media_type};base64,{image_b64}"
        return call_vlm(
            prompt=prompt,
            image_data_url=data_url,
            model=self.model,
            base_url=self.base_url,
        )


def get_vlm(model: str | None = None, base_url: str | None = None) -> OllamaVLM:
    """VLMインスタンスを取得"""
    return OllamaVLM(model=model, base_url=base_url)
