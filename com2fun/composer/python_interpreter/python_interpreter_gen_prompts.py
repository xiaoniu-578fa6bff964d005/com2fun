#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

from ...func_def import InOutExample

INPUT_PREFIX = ">>> "
INDENT_REGEX = re.compile(r"^\s*")


def interpreter_header():
    return [
        'Python 3.10.8 (main, Nov 24 2022, 14:13:03) [GCC 11.2.0] on linux\nType "help", "copyright", "credits" or "license" for more information.\n'
    ]


def func_query_format(input_prefix=INPUT_PREFIX):
    return [
        input_prefix + "1+1\n",
        "2\n",
        input_prefix
        + "import strongai\n"
        + input_prefix
        + 'strongai._top("university", 3)\n',
        "['MIT', 'Stanford', 'Harvard']\n",
    ]


def func_definition(func_def, input_prefix=INPUT_PREFIX):
    #  prompts = [
    #      input_prefix + "import strongai\n",
    #  ]
    prompts = [
        input_prefix + l
        for l in func_def.intension.clean_source().splitlines(keepends=True)
    ]
    prompts.append(
        input_prefix
        + INDENT_REGEX.match(prompts[-1][len(input_prefix) :]).group()
        #  + "[...Implementation Omitted...]\n"
        #  + f"_{func_def.intension.name}(*locals())\n"
        + f"strongai._{func_def.intension.name}(*locals())\n"
    )
    prompts.append(input_prefix + "\n")
    return "".join(prompts)


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


def query(func_def, args, kwargs, read_out, input_prefix=INPUT_PREFIX):
    return [input_prefix + read_out.cmd.format(invoke(func_def, args, kwargs)) + "\n"]


def example(func_def, example: InOutExample, read_out, input_prefix=INPUT_PREFIX):
    prompts = []
    if example.comments is not None:
        prompts += [
            input_prefix + "# " + l for l in example.comments.splitlines(keepends=True)
        ]
        if prompts[-1][-1] != "\n":
            prompts[-1] += "\n"
    prompts += [
        input_prefix
        + read_out.cmd.format(invoke(func_def, example.args, example.kwargs))
        + "\n"
    ]
    prompts = ["".join(prompts)]
    prompts.append(
        read_out.serialize(example.result) + "\n",
    )
    return prompts
