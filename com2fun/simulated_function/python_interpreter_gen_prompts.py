#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from ..func_def import InOutExample

INPUT_PREFIX = ">>> "
INDENT_REGEX = re.compile(r"^\s*")


def intepreter_header():
    return [
        "Python 3.10.8 (main, Nov 24 2022, 14:13:03) [GCC 11.2.0] on linux\n"
        'Type "help", "copyright", "credits" or "license" for more information.\n'
    ]


def func_query_format():
    return [INPUT_PREFIX + "1\n", "1\n"]


def func_definition(func_def, input_prefix=INPUT_PREFIX):
    prompts = [
        input_prefix + l
        for l in func_def.intension.clean_source().splitlines(keepends=True)
    ]
    prompts.append(
        input_prefix
        + INDENT_REGEX.match(prompts[-1][len(input_prefix) :]).group()
        #  + "[...Implementation Omitted...]\n"
        + f"_{func_def.intension.name}(*locals())\n"  # TODO
    )
    prompts.append(input_prefix + "\n")
    return prompts


def invoke(func_def, args, kwargs):
    return (
        func_def.intension.name
        + "("
        + ", ".join(
            [repr(arg) for arg in args]
            + [repr(k) + "=" + repr(v) for k, v in kwargs.items()]
        )
        + ")"
    )


def query(func_def, args, kwargs, read_out):
    return [INPUT_PREFIX + read_out.cmd.format(invoke(func_def, args, kwargs)) + "\n"]


def example(func_def, example: InOutExample, read_out):
    prompts = []
    if example.comments is not None:
        prompts += [
            INPUT_PREFIX + "# " + l for l in example.comments.splitlines(keepends=True)
        ]
        if prompts[-1][-1] != "\n":
            prompts[-1] += "\n"
    prompts += [
        INPUT_PREFIX
        + read_out.cmd.format(invoke(func_def, example.args, example.kwargs))
        + "\n"
    ]
    prompts.append(
        read_out.serialize(example.result) + "\n",
    )
    return prompts
