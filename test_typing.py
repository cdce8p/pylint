# pylint: disable=blacklisted-name,wrong-import-position,unused-argument,unused-variable,misplaced-future,reimported,ungrouped-imports
# fmt: off
# type: ignore
# isort:skip

# Issue 1 - PEP 585
# False positive (unsubscriptable-object) -> valid 3.7+
from __future__ import annotations
from typing import Dict
var3: dict[str, list[int]]
var4: Dict[str, list[int]]
var5: dict[tuple[int, int], str]
var6: Dict[tuple[int, int], str]
var7: list[list[int]]


# Issue 4 - Combination
# False positive (unsubscriptable-object) -> valid 3.7+
from __future__ import annotations
var1: int | list[str | int]

# -> Issue with nested PEP 585 syntax



# Issue 2 - PEP 604
# Missing error in 3.7 - 3.9
var2: int | str | None  # [unsupported-binary-operation]



# Issue 3 - PEP 604
# False positive (unsupported-binary-operation) -> valid 3.7+
from __future__ import annotations
import typing
var1: typing.Dict[str, int | None]






# Final
# Missing error in 3.7
var3: int | list[str | int]  # [unsupported-binary-operation,unsubscriptable-object]



from dataclasses import dataclass
@dataclass
class MyCls:
    arg: dict[str, tuple[int | None, str]]  # false-positive



from __future__ import annotations
import typing
x = 1 | 2
var0: int | None
var1: typing.Dict[str, int | None]
var2: int | str | None
