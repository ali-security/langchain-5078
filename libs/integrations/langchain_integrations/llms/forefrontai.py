from typing import Any, Dict, List, Mapping, Optional

import requests
from langchain_core.pydantic_v1 import Extra, SecretStr, root_validator

from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_integrations.llms.base import LLM
from langchain_integrations.llms.utils import enforce_stop_tokens
from langchain_core.utils import convert_to_secret_str, get_from_dict_or_env


class ForefrontAI(LLM):
    """ForefrontAI large language models.

    To use, you should have the environment variable ``FOREFRONTAI_API_KEY``
    set with your API key.

    Example:
        .. code-block:: python

            from langchain_integrations.llms import ForefrontAI
            forefrontai = ForefrontAI(endpoint_url="")
    """

    endpoint_url: str = ""
    """Model name to use."""

    temperature: float = 0.7
    """What sampling temperature to use."""

    length: int = 256
    """The maximum number of tokens to generate in the completion."""

    top_p: float = 1.0
    """Total probability mass of tokens to consider at each step."""

    top_k: int = 40
    """The number of highest probability vocabulary tokens to
    keep for top-k-filtering."""

    repetition_penalty: int = 1
    """Penalizes repeated tokens according to frequency."""

    forefrontai_api_key: SecretStr = None

    base_url: Optional[str] = None
    """Base url to use, if None decides based on model name."""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that api key exists in environment."""
        values["forefrontai_api_key"] = convert_to_secret_str(
            get_from_dict_or_env(values, "forefrontai_api_key", "FOREFRONTAI_API_KEY")
        )
        return values

    @property
    def _default_params(self) -> Mapping[str, Any]:
        """Get the default parameters for calling ForefrontAI API."""
        return {
            "temperature": self.temperature,
            "length": self.length,
            "top_p": self.top_p,
            "top_k": self.top_k,
            "repetition_penalty": self.repetition_penalty,
        }

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {**{"endpoint_url": self.endpoint_url}, **self._default_params}

    @property
    def _llm_type(self) -> str:
        """Return type of llm."""
        return "forefrontai"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call out to ForefrontAI's complete endpoint.

        Args:
            prompt: The prompt to pass into the model.
            stop: Optional list of stop words to use when generating.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                response = ForefrontAI("Tell me a joke.")
        """
        auth_value = f"Bearer {self.forefrontai_api_key.get_secret_value()}"
        response = requests.post(
            url=self.endpoint_url,
            headers={
                "Authorization": auth_value,
                "Content-Type": "application/json",
            },
            json={"text": prompt, **self._default_params, **kwargs},
        )
        response_json = response.json()
        text = response_json["result"][0]["completion"]
        if stop is not None:
            # I believe this is required since the stop tokens
            # are not enforced by the model parameters
            text = enforce_stop_tokens(text, stop)
        return text
