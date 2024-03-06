from typing import Any
import openai

from . import InvalidCompletionResult
from ..llm_utils import LLMCompletionInput, LLMChatInput
from .simplellmsfbase import SimpleLLMSFBase


class AnthropicChatSF(SimpleLLMSFBase):
    """add request to Anthropic server"""

    default_param = {"model": "claude-3-sonnet-20240229", "max_tokens": 2048}

    def __init__(self, client, param={}, **kwargs):
        client = client
        super().__init__(client=client, param=param, **kwargs)

    def _request(self, **kwargs):
        assert (
            "async" not in str(self.client).lower()
        ), "This client is async, use acall instead."
        return self.client.messages.create(**kwargs)

    async def _arequest(self, **kwargs):
        assert (
            "async" in str(self.client).lower()
        ), "This client is not async, use __call__ instead."
        return await self.client.messages.create(**kwargs)

    def get_result_str(self, llm_output: Any) -> str:
        stop_reason = llm_output.stop_reason
        if stop_reason == "max_tokens":
            raise InvalidCompletionResult(
                "The completion result is too long.", llm_output
            )
        elif stop_reason not in ["end_turn", "stop_sequence"]:
            raise InvalidCompletionResult("Unknown stop_reason", llm_output)
        return llm_output.content[0].text

    def adjust_anthropic_llm_input(self, llm_input: LLMChatInput) -> dict:
        if len(llm_input) >= 1 and llm_input[0]["role"] == "system":
            return {"messages": llm_input[1:], "system": llm_input[0]["content"]}
        else:
            return {"messages": llm_input}

    def adjust_anthropic_param(self, param: dict) -> dict:
        if "stop" in param:
            param["stop_sequences"] = param.pop("stop")
        return param

    def query_llm(self, llm_input: LLMChatInput, **param) -> Any:
        return self._request(
            **self.adjust_anthropic_llm_input(llm_input),
            **self.adjust_anthropic_param(param)
        )

    async def aquery_llm(self, llm_input: LLMChatInput, **param) -> Any:
        return await self._arequest(
            **self.adjust_anthropic_llm_input(llm_input),
            **self.adjust_anthropic_param(param)
        )
