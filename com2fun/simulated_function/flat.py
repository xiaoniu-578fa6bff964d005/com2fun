#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import SimpleOpenAISF
from ..func_def import InOutExample

INPUTHEADER = "###\n"
OUTPUTHEADER = "---\n"


class FlatSF(SimpleOpenAISF):
    default_param = {
        "stop": [INPUTHEADER.rstrip()],
    }

    def invoke_prompt(self, *args, **kwargs) -> str:
        prompts = []
        prompts += func_intension(self.func_def.intension)
        prompts += func_extension(
            self.func_def.extension, read_out=self.invoke_read_out_method()
        )
        prompts += input_format(args, kwargs)
        prompts.append(OUTPUTHEADER)
        prompt = "".join(prompts)
        return prompt


def func_intension(func_def):
    prompts = []
    if func_def.full_source:
        return [func_def.clean_source()]
    else:
        if func_def.name:
            prompts.append(f"{func_def.name}\n")
        if func_def.comments:
            prompts.append(f"{func_def.comments}")
        if func_def.doc:
            prompts.append(f"{func_def.doc}\n")
        if func_def.signature:
            prompts.append(f"{func_def.signature}\n")
    return prompts


def func_extension(func_def, read_out):
    prompts = []
    for i in func_def.examples:
        prompts += example(
            func_def.examples[i],
            read_out=read_out,
        )
    return prompts


def example(example: InOutExample, read_out):
    prompts = []
    if example.comments:
        raise Exception("comments not supported yet")
    prompts += input_format(example.args, example.kwargs)
    prompts += output_format(example.result, read_out)
    return prompts


def input_format(args, kwargs):
    prompts = []
    if args:
        prompts.append(INPUTHEADER)
        prompts += [repr(i) + "\n" for i in args + tuple(kwargs.values())]
    return prompts


def output_format(result, read_out):
    prompts = []
    if result:
        prompts.append(OUTPUTHEADER + read_out.serialize(result) + "\n")
    return prompts
