from typing import Any
import openai

from . import InvalidCompletionResult
from ..llm_utils import LLMCompletionInput, LLMChatInput
from .simplellmsfbase import SimpleLLMSFBase


class OpenAISFBase(SimpleLLMSFBase):
    """add request to openai server"""

    def __init__(self, client=None, param={}, **kwargs):
        client = client if client is not None else openai
        super().__init__(client=client, param=param, **kwargs)

    def _request(self, method: str, **kwargs):
        if method == "complete":
            return self.client.completions.create(**kwargs)
        elif method == "chat":
            return self.client.chat.completions.create(**kwargs)
        else:
            raise ValueError("Unknown method: {}".format(method))

    async def _arequest(self, method: str, **kwargs):
        if method == "complete":
            return await self.client.completions.acreate(**kwargs)
        elif method == "chat":
            return await self.client.chat.completions.acreate(**kwargs)
        else:
            raise ValueError("Unknown method: {}".format(method))

    def get_result_str(self, llm_output: Any) -> str:
        finish_reason = llm_output.choices[0].finish_reason
        if finish_reason == "length":
            raise InvalidCompletionResult(
                "The completion result is too long.", llm_output
            )
        elif finish_reason != "stop" and finish_reason is not None:
            raise InvalidCompletionResult("Unknown finish_reson", llm_output)
        c = llm_output.choices[0]
        if hasattr(c, "text"):
            return c.text
        elif hasattr(c, "message"):
            return c.message.content


class OpenAICompletionSF(OpenAISFBase):
    default_param = {"model": "text-davinci-003", "max_tokens": 2048}

    def query_llm(self, llm_input: LLMCompletionInput, **param) -> Any:
        assert isinstance(llm_input, LLMCompletionInput)
        return self._request("complete", prompt=llm_input, **param)

    async def aquery_llm(self, llm_input: LLMCompletionInput, **param) -> Any:
        assert isinstance(llm_input, LLMCompletionInput)
        return await self._arequest("complete", prompt=llm_input, **param)


class OpenAIChatSF(OpenAISFBase):
    default_param = {"model": "gpt-4-0613"}

    def query_llm(self, llm_input: LLMChatInput, **param) -> Any:
        return self._request("chat", messages=llm_input, **param)

    async def aquery_llm(self, llm_input: LLMChatInput, **param) -> Any:
        return await self._arequest("chat", messages=llm_input, **param)
