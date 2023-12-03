"""Utility that calls OpenAI's Dall-E Image Generator."""
from typing import Any, Dict, Optional

from langchain_core.pydantic_v1 import BaseModel, Extra, root_validator

from langchain_core.utils import get_from_dict_or_env


class DallEAPIWrapper(BaseModel):
    """Wrapper for OpenAI's DALL-E Image Generator.

    https://platform.openai.com/docs/guides/images/generations?context=node

    Usage instructions:

    1. `pip install openai`
    2. save your OPENAI_API_KEY in an environment variable
    """

    client: Any  #: :meta private:
    openai_api_key: Optional[str] = None
    n: int = 1
    """Number of images to generate"""
    size: str = "1024x1024"
    """Size of image to generate"""
    separator: str = "\n"
    """Separator to use when multiple URLs are returned."""
    model: Optional[str] = "dall-e-2"
    """Model to use for image generation"""
    quality: Optional[str] = "standard"
    """Quality of the image that will be generated"""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key and python package exists in environment."""
        openai_api_key = get_from_dict_or_env(
            values, "openai_api_key", "OPENAI_API_KEY"
        )
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=openai_api_key,  # this is also the default, it can be omitted
            )

            values["client"] = client
        except ImportError as e:
            raise ImportError(
                "Could not import openai python package. "
                "Please it install it with `pip install openai`."
            ) from e
        return values

    def run(self, query: str) -> str:
        """Run query through OpenAI and parse result."""
        response = self.client.images.generate(
            prompt=query,
            n=self.n,
            size=self.size,
            model=self.model,
            quality=self.quality,
        )
        image_urls = self.separator.join([item.url for item in response.data])
        return image_urls if image_urls else "No image was generated"
