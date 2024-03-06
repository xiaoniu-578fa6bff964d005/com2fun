from abc import abstractmethod
from typing import Any

from . import SimulatedFunction, InvalidCompletionResult
from ..composer import ReadOut
from ..llm_utils import LLMInput

DEFAULT_PARAM = {
    "temperature": 0.0,
    #  "stream": False,
}


class SimpleLLMSFBase(SimulatedFunction):
    """add param and client. Call LLM once and parse the result."""

    default_param = {}

    def __init__(self, client, param={}, **kwargs):
        self.param = param
        self.client = client
        super().__init__(**kwargs)

    def invoke_param(self, read_out: ReadOut) -> dict:
        param = {**DEFAULT_PARAM, **type(self).default_param, **self.param}
        if read_out.stop:
            param["stop"] = param.get("stop", []) + read_out.stop
        return param

    @abstractmethod
    def query_llm(self, llm_input: LLMInput, **param) -> Any:
        pass

    @abstractmethod
    async def aquery_llm(self, llm_input: LLMInput, **param) -> Any:
        pass

    @abstractmethod
    def get_result_str(self, llm_output: Any) -> str:
        """First, verify the response is valid. Then, extract the result string."""

    def parse(self, result_str: str, read_out: ReadOut) -> Any:
        try:
            return read_out.deserialize(result_str)
        except Exception as e:
            raise InvalidCompletionResult(
                "The completion result is not serializable.",
                {
                    "result_str": result_str,
                    "read_out": read_out,
                    "error": e,
                },
            )

    def invoke_llm_input(self, *args, **kwargs) -> LLMInput:
        llm_input, read_out = self.composer(self.func_def, *args, **kwargs)
        return llm_input

    def invoke(self, *args, **kwargs):
        llm_input, read_out = self.composer(self.func_def, *args, **kwargs)
        param = self.invoke_param(read_out)
        llm_output = self.query_llm(llm_input, **param)
        r = {
            "param": param,
            "llm_input": llm_input,
            "llm_output": llm_output,
            "result_str": self.get_result_str(llm_output),
        }
        r["return"] = self.parse(r["result_str"], read_out)
        return r

    async def ainvoke(self, *args, **kwargs):
        llm_input, read_out = self.composer(self.func_def, *args, **kwargs)
        param = self.invoke_param(read_out)
        llm_output = await self.aquery_llm(llm_input, **param)
        r = {
            "param": param,
            "llm_input": llm_input,
            "llm_output": llm_output,
            "result_str": self.get_result_str(llm_output),
        }
        r["return"] = self.parse(r["result_str"], read_out)
        return r
