#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import SimpleOpenAISF
from ..func_def import InOutExample


class TemplateSF(SimpleOpenAISF):
    default_param = {
        "stop": ["\n"],
    }

    def invoke_prompt(self, *args, **kwargs) -> str:
        if self.func_def.intension.name or self.func_def.intension.comments:
            raise Exception("name and comments not supported yet")
        prompts = []
        try:
            stop = self.invoke_param()["stop"][0]
        except IndexError as e:
            raise Exception("stop must be a list of strings when example is provided")
        prompts += func_extension(
            self.func_def,
            stop,
            read_out=self.invoke_read_out_method(),
        )
        prompts.append(self.func_def.intension.doc.format(*args, **kwargs))
        prompt = "".join(prompts)
        return prompt


def func_extension(func_def, stop, read_out):
    prompts = []
    for i in func_def.extension.examples:
        prompts += example(
            func_def.intension.doc,
            stop,
            func_def.extension.examples[i],
            read_out=read_out,
        )
    return prompts


def example(doc, stop, example: InOutExample, read_out):
    prompts = []
    if example.comments:
        raise Exception("comments not supported yet")
    prompts.append(doc.format(*example.args, **example.kwargs))
    prompts.append(read_out.serialize(example.result) + stop)
    return prompts
