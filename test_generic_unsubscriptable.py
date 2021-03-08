"""Current error: Base unsubscriptable if Generic and metaclass=ABCMeta

    https://github.com/PyCQA/pylint/issues/2822

TODO
- Don't emit `unsubscriptable-object` error

Fixed in: https://github.com/PyCQA/astroid/pull/931
Added as test cases: https://github.com/PyCQA/pylint/pull/4334
"""
# pylint: disable=missing-docstring,invalid-name,too-few-public-methods
from abc import ABCMeta, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

class Base(Generic[T], metaclass=ABCMeta):
    """Base"""

    @classmethod
    @abstractmethod
    def do_something(cls):
        """Do something"""


class Impl(Base):
    """Impl"""

    def do_something(self):
        assert self


class ImplStr(Base[str]):  # Current error
    """Impl"""

    @classmethod
    def do_something(cls):
        assert cls


ImplStr.do_something()
