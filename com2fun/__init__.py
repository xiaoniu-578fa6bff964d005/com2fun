from functools import partial
from .func_def import to_func_def
from . import simulated_function as SF
from .simulated_function.openai import OpenAIChatSF
from .composer import DefaultCompletionComposer, DefaultChatComposer


def _com2fun(func, SF=OpenAIChatSF, composer=DefaultChatComposer(), **SF_kwargs):
    func_def = to_func_def(func)
    return SF(func_def=func_def, composer=composer, **SF_kwargs)


def com2fun(func=None, **kwargs):
    if func is None:
        return partial(_com2fun, **kwargs)
    else:
        return _com2fun(func, **kwargs)
