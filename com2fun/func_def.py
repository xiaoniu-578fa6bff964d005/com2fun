from dataclasses import dataclass
import inspect
from typing import Optional, Any


def _remove_com2fun_decorator(full_source: str) -> list[str]:
    lines = full_source.splitlines(keepends=True)
    outs = []
    i = 0
    indent = lambda l: len(l) - len(l.lstrip())
    while i < len(lines):
        l = lines[i]
        l_indent = indent(l)
        if l[l_indent] == "@" and "com2fun" in l:
            # encounter com2fun decorator
            i += 1
            while indent(lines[i]) > l_indent:
                i += 1
            if lines[i].strip() == ")":
                i += 1
            continue
        outs.append(l)
        i += 1
    return outs


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

        r += _remove_com2fun_decorator(self.full_source)

        def remove_common_prefix(r):
            prefix = min([len(l) - len(l.lstrip()) for l in r])
            return [l[prefix:] for l in r]

        r = remove_common_prefix(r)

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
