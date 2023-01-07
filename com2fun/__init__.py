#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .func_def import *
from .simulated_function import *


def com2fun(func, SF=PythonInterpreterSF):
    func_def = to_func_def(func)
    return SF(func_def)


def prompt(*args, stop="\n", SF=TemplateSF, **kwargs):
    func_def = template_to_func_def(*args, **kwargs)
    sf = SF(func_def)
    if stop is not None:
        if isinstance(stop, list):
            sf.param["stop"] = stop
        else:
            sf.param["stop"] = [stop]
    return sf
