#!/usr/bin/env python
# -*- coding: utf-8 -*-

from . import SimpleOpenAISF, CompletionOpenAISF, ChatOpenAISF
from . import python_interpreter_gen_prompts as gen_prompts


class PythonInterpreterSF(CompletionOpenAISF):
    default_param = {
        **CompletionOpenAISF.default_param,
        "stop": [gen_prompts.INPUT_PREFIX.rstrip()],
    }

    def invoke_prompt(self, *args, **kwargs) -> str:
        prompts = []
        #  prompts += gen_prompts.intepreter_header()
        prompts += gen_prompts.func_query_format()
        prompts += gen_prompts.func_definition(self.func_def)
        for i in self.func_def.extension.examples:
            prompts += gen_prompts.example(
                self.func_def,
                self.func_def.extension.examples[i],
                read_out=self.invoke_read_out_method(),
            )
        prompts += gen_prompts.query(
            self.func_def, args, kwargs, read_out=self.invoke_read_out_method()
        )
        prompt = "".join(prompts)
        return prompt


class ChatBasedPythonInterpreterSF(ChatOpenAISF):
    default_param = {
        **ChatOpenAISF.default_param,
    }

    def invoke_messages(self, *args, **kwargs) -> list[dict]:
        prompt = PythonInterpreterSF.invoke_prompt(self, *args, **kwargs)

        messages = [
            {"role": "user", "content": prompt},
        ]
        return messages
