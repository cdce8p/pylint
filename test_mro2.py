"""Test file for astroid.exceptions.DuplicateBasesError (with stdlib)

Fixed: pylint 2.7.2, astroid 2.5.1
https://github.com/PyCQA/astroid/pull/916

Added as official test cases
https://github.com/PyCQA/pylint/pull/4239

Run tests with
pytest tests/test_functional.py -k generic_alias
pytest -m acceptance -k "test_libmodule[typing.py]"
pytest -m acceptance -k "test_libmodule[collections]"
"""
# pylint: disable=unused-import
import re
import typing
import collections
import collections.abc
from collections.abc import Iterator

var1: re.Match[str]
var2: collections.OrderedDict[str, int]
var: collections.defaultdict[int, str]
var2: collections.abc.Iterable[int]
var3: Iterator[int]

var2: typing.OrderedDict[int, str]
var3: typing.List[str]
var4: typing.Pattern[str]



import astroid

def printMro(klass):
    print("[")
    for item in [member.name for member in klass.mro()]:
        print(f"\t\"{item}\",")
    print("]")

# tree = astroid.parse(
#     """
# from typing import DefaultDict
# var: DefaultDict[int, str]
# """
# )
# print(tree.repr_tree())


cls = astroid.extract_node(
    """
import typing
import collections.abc
class Derived(typing.Pattern[str]):
    pass
class Derived2(typing.Iterable[int]):
    def __init__(self):
        self.var = 1
"""
)

printMro(cls)
