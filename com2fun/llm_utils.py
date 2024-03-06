from typing import Union

LLMCompletionInput = str
LLMChatInput = list[dict]
LLMInput = Union[LLMCompletionInput, LLMChatInput]
