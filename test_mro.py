"""Test file for astroid.exceptions.DuplicateBasesError

    https://github.com/PyCQA/astroid/issues/905
    https://github.com/PyCQA/pylint/issues/4093 (OrderedSet)
    https://github.com/PyCQA/pylint/issues/4131 (aiohttp)
    https://github.com/PyCQA/pylint/issues/4145 (Red-DiscordBot)

Fixed: pylint 2.7.2, astroid 2.5.1
https://github.com/PyCQA/astroid/pull/916

Added as official test cases
https://github.com/PyCQA/pylint/pull/4239

Run tests with
pytest tests/test_functional.py -k generic_alias
pytest -m acceptance -k "test_libmodule[typing.py]"
pytest -m acceptance -k "test_libmodule[collections]"
"""
# pylint: disable=missing-class-docstring,inherit-non-class,too-few-public-methods
# pylint: disable=no-value-for-parameter,unused-import,missing-module-docstring
# pylint: disable=super-init-not-called,ungrouped-imports,wrong-import-position
# pylint: disable=wrong-import-order,reimported
from astroid.builder import extract_node

from typing import Sized, Hashable
class Derived(Sized, Hashable):
    def __init__(self):
        self.var = 1


import abc
from typing import Sized, Iterable
class AbstractRoute(abc.ABC):
    pass
class AbstractResource(Sized, Iterable["AbstractRoute"]):
    pass
class IndexView(AbstractResource):
    def __init__(self):
        self.var = 1


# pip install ordered-set
from ordered_set import OrderedSet


# pip install Red-DiscordBot
from redbot.core.utils import AsyncFilter

cls0 = extract_node(
    """
from typing import Sized, Hashable
class Derived(Sized, Hashable):
    def __init__(self):
        self.var = 1
"""
)


cls1 = extract_node(
    """
import abc
from typing import Sized, Iterable
class AbstractRoute(abc.ABC):
    pass
class AbstractResource(Sized, Iterable["AbstractRoute"]):
    pass
class IndexView(AbstractResource):
    def __init__(self):
        self.var = 1
"""
)

cls3 = extract_node(
    """
from ordered_set import OrderedSet
class Derived(OrderedSet):
    pass
"""
)

cls4 = extract_node(
    """
from redbot.core.utils import AsyncFilter
class Derived(AsyncFilter):
    pass
"""
)

def printMro(klass):
    lst = [member.name for member in klass.mro()]
    print("[")
    for item in lst:
        print(f"\t\"{item}\",")
    print("]")


printMro(cls0)
printMro(cls1)
printMro(cls3)
printMro(cls4)
