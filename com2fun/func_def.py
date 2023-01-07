#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
import inspect
from typing import Optional, Any


@dataclass
class FunctionIntension:
    name: Optional[str]
    comments: Optional[str]
    doc: Optional[str]
    signature: Optional[inspect.Signature]
    full_source: Optional[str]

    def clean_source(self) -> Optional[str]:
        """add comments, remove decorator"""
        if not self.full_source:
            return None
        r = []
        if self.comments:
            r.append(self.comments)

        def is_com2fun_decorator(l):
            l = l.strip()
            if l.startswith("@") and "com2fun" in l:
                return True
            return False

        r += [
            l
            for l in self.full_source.splitlines(keepends=True)
            if not is_com2fun_decorator(l)
        ]
        return "".join(r)


ExampleID = str


@dataclass
class InOutExample:
    args: Any
    kwargs: Any
    result: Any
    comments: Optional[str]

    def id(self) -> ExampleID:
        return repr((self.args, self.kwargs))


@dataclass
class FunctionExtension:
    examples: dict[ExampleID, InOutExample]


@dataclass
class FunctionDefinition:
    intension: FunctionIntension
    extension: FunctionExtension


def to_func_def(func) -> FunctionDefinition:

    func_intension = FunctionIntension(
        name=func.__name__,
        comments=inspect.getcomments(func),
        doc=inspect.getdoc(func),
        signature=inspect.signature(func),
        full_source=inspect.getsource(func),
    )

    func_extension = FunctionExtension(examples={})

    return FunctionDefinition(
        intension=func_intension,
        extension=func_extension,
    )


def template_to_func_def(
    doc, signature_ref_func=None, return_type=str
) -> FunctionDefinition:
    if signature_ref_func is None:
        signature_ref_func = lambda *args, **kwargs: None
        signature_ref_func.__annotations__["return"] = return_type
    func_intension = FunctionIntension(
        doc=doc,
        signature=inspect.Signature.from_callable(signature_ref_func),
        name=None,
        comments=None,
        full_source=None,
    )

    func_extension = FunctionExtension(examples={})

    return FunctionDefinition(
        intension=func_intension,
        extension=func_extension,
    )
