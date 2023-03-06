#!/usr/bin/env python
# -*- coding: utf-8 -*-

import openai

from abc import abstractmethod
from collections import namedtuple
import functools
import ast

from . import InvalidCompletionResult, SimulatedFunction

DEFAULT_PARAM = {
    "temperature": 0.0,
    "max_tokens": 2048,
    "stream": False,
}

ReadOut = namedtuple("ReadOut", ["cmd", "serialize", "deserialize"])


class SimpleOpenAISF(SimulatedFunction):
    """
    This class should emit exactly one prompt and the completion output should be serialization of the result.
    """

    default_param = {}

    def __init__(self, *args, **kwargs):
        self.param = {}
        super().__init__(*args, **kwargs)

    def invoke_read_out_method(self) -> ReadOut:
        # get return type
        sig = self.func_def.intension.signature
        return_type = sig.return_annotation
        if return_type in recommand_read_out:
            return recommand_read_out[return_type]
        return read_out_struct_eval

    def invoke_param(self) -> dict:
        return {**DEFAULT_PARAM, **type(self).default_param, **self.param}

    def invoke(self, *args, **kwargs):
        param = self.invoke_param()
        if isinstance(self, CompletionOpenAISF):
            prompt = self.invoke_prompt(*args, **kwargs)
            response = openai.Completion.create(prompt=prompt, **param)
            result_str = response["choices"][0]["text"]
        elif isinstance(self, ChatOpenAISF):
            messages = self.invoke_messages(*args, **kwargs)
            response = openai.ChatCompletion.create(messages=messages, **param)
            result_str = response["choices"][0]["message"]["content"]
        else:
            raise Exception("Unknown OpenAISF type.")
        r = {
            "param": param,
            "response": response,
            "result_str": result_str,
        }
        if isinstance(self, CompletionOpenAISF):
            r["prompt"] = prompt
        elif isinstance(self, ChatOpenAISF):
            r["messages"] = messages
        try:
            result = self.invoke_read_out_method().deserialize(result_str)
        except Exception as e:
            raise InvalidCompletionResult(
                "The completion result is not serializable.",
                {
                    **r,
                    "error": e,
                },
            )
        return {
            **r,
            "return": result,
        }


class CompletionOpenAISF(SimpleOpenAISF):
    default_param = {
        **SimpleOpenAISF.default_param,
        "model": "text-davinci-003",
        "best_of": 1,
        #  "model": "code-davinci-002",
    }

    @abstractmethod
    def invoke_prompt(self, *args, **kwargs) -> str:
        """Should return the prompt that is posted to OpenAI API"""


class ChatOpenAISF(SimpleOpenAISF):
    default_param = {
        **SimpleOpenAISF.default_param,
        "model": "gpt-3.5-turbo",
    }

    @abstractmethod
    def invoke_messages(self, *args, **kwargs) -> list[dict]:
        """Should return the messages that is posted to OpenAI API.
        Example:
        [{"role": "user", "content": "Hello world!"}]
        """


# cmd is the one line python command that could be used in python interpreter
# to let the serialized result shows up in console. It should contain a single
# positional argument that is the name of the variable that contains the result.
ReadOut = namedtuple("ReadOut", ["cmd", "serialize", "deserialize"])
recommand_read_out = {}
recommand_read_out[str] = ReadOut(
    "print({})",
    lambda x: x,
    lambda x: x,
)


# cannot be replaced with bool(x) because bool("False")==True
def _bool_parse(x: str):
    x = x.strip()
    if x in ["True", "False"]:
        return x == "True"
    else:
        raise ValueError("Invalid boolean value: {}".format(x))


recommand_read_out[bool] = ReadOut(
    "{}",
    lambda x: repr(x),
    _bool_parse,
)


def _naive_parse(t: type, x: str):
    return t(x)


for t in [int, float]:
    recommand_read_out[t] = ReadOut(
        "{}",
        lambda x: repr(x),
        functools.partial(_naive_parse, t),
    )

read_out_struct_eval = ReadOut(
    "{}",
    lambda x: repr(x),
    lambda x: ast.literal_eval(x),
)
