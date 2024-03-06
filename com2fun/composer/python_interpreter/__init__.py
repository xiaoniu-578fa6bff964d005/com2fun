import itertools
from .. import Composer
from ...llm_utils import LLMCompletionInput, LLMChatInput
from .. import ReadOut, recommend_read_out
from . import python_interpreter_gen_prompts as gen_prompts
from ...func_def import FunctionDefinition


class CompletionComposer(Composer):
    def __call__(
        self, func_def: FunctionDefinition, *args, **kwargs
    ) -> (LLMCompletionInput, ReadOut):
        read_out = recommend_read_out[func_def.intension.signature.return_annotation]
        read_out = read_out._replace(stop=[gen_prompts.INPUT_PREFIX.rstrip()])
        prompts = []
        #  prompts += gen_prompts.interpreter_header()
        prompts += gen_prompts.func_query_format()
        prompts += gen_prompts.func_definition(func_def)
        for i in func_def.extension.examples:
            prompts += gen_prompts.example(
                func_def,
                func_def.extension.examples[i],
                read_out=read_out,
            )
        prompts += gen_prompts.query(func_def, args, kwargs, read_out=read_out)
        return "".join(prompts), read_out


class ChatComposer(Composer):
    def __call__(
        self, func_def: FunctionDefinition, *args, **kwargs
    ) -> (LLMChatInput, ReadOut):
        read_out = recommend_read_out[func_def.intension.signature.return_annotation]
        messages = []
        messages.append(
            {
                "role": "system",
                "content": "Simulate a python interpreter. Fill in the job of strongai module. Generate the output of functions like strongai._top\nReturn the result according to the query. If there is a print(...), print accordingly. Don't show other boilerplate.",
            }
        )
        #  messages += gen_prompts.interpreter_header()
        messages += [
            {"role": r, "content": m}
            for r, m in zip(
                itertools.cycle(["user", "assistant"]),
                gen_prompts.func_query_format(input_prefix=""),
            )
        ]
        messages.append(
            {
                "role": "user",
                "content": gen_prompts.func_definition(func_def, input_prefix=""),
            }
        )
        for i in func_def.extension.examples:
            messages += [
                {"role": r, "content": m}
                for r, m in zip(
                    itertools.cycle(["user", "assistant"]),
                    gen_prompts.example(
                        func_def,
                        func_def.extension.examples[i],
                        read_out=read_out,
                        input_prefix="",
                    ),
                )
            ]
        messages.append(
            {
                "role": "user",
                "content": gen_prompts.query(
                    func_def, args, kwargs, read_out=read_out, input_prefix=""
                )[0],
            }
        )
        # merge consecutive messages of the same role
        messages = [
            {"role": role, "content": "".join([m["content"] for m in msgs])}
            for role, msgs in itertools.groupby(messages, key=lambda x: x["role"])
        ]
        # remove tailing newline
        messages = [
            {"role": m["role"], "content": m["content"].rstrip("\n")} for m in messages
        ]
        return messages, read_out
