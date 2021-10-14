# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/pylint-dev/pylint/blob/main/LICENSE
# Copyright (c) https://github.com/pylint-dev/pylint/blob/main/CONTRIBUTORS.txt

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, cast

from astroid import nodes

from pylint.checkers import BaseChecker, utils
from pylint.checkers.utils import only_required_for_messages, safe_infer
from pylint.interfaces import INFERENCE

if TYPE_CHECKING:
    from pylint.lint import PyLinter

if sys.version_info >= (3, 10):
    from typing import TypeGuard
else:
    from typing_extensions import TypeGuard


# pylint: disable-next=too-many-instance-attributes
class CodeStyleChecker(BaseChecker):
    """Checkers that can improve code consistency.

    As such they don't necessarily provide a performance benefit and
    are often times opinionated.

    Before adding another checker here, consider this:
    1. Does the checker provide a clear benefit,
       i.e. detect a common issue or improve performance
       => it should probably be part of the core checker classes
    2. Is it something that would improve code consistency,
       maybe because it's slightly better with regard to performance
       and therefore preferred => this is the right place
    3. Everything else should go into another extension
    """

    name = "code_style"
    msgs = {
        "R6101": (
            "Consider using namedtuple or dataclass for dictionary values",
            "consider-using-namedtuple-or-dataclass",
            "Emitted when dictionary values can be replaced by namedtuples or dataclass instances.",
        ),
        "R6102": (
            "Consider using an in-place tuple instead of list",
            "consider-using-tuple",
            "Only for style consistency! "
            "Emitted where an in-place defined ``list`` can be replaced by a ``tuple``. "
            "Due to optimizations by CPython, there is no performance benefit from it.",
        ),
        "R6103": (
            "Use '%s' instead",
            "consider-using-assignment-expr",
            "Emitted when an if assignment is directly followed by an if statement and "
            "both can be combined by using an assignment expression ``:=``. "
            "Requires Python 3.8 and ``py-version >= 3.8``.",
        ),
        "R6104": (
            "Use '%s' to do an augmented assign directly",
            "consider-using-augmented-assign",
            "Emitted when an assignment is referring to the object that it is assigning "
            "to. This can be changed to be an augmented assign.\n"
            "Disabled by default!",
            {
                "default_enabled": False,
            },
        ),
        "R6105": (
            "Prefer 'typing.NamedTuple' over 'collections.namedtuple'",
            "prefer-typing-namedtuple",
            "'typing.NamedTuple' uses the well-known 'class' keyword "
            "with type-hints for readability (it's also faster as it avoids "
            "an internal exec call).\n"
            "Disabled by default!",
            {
                "default_enabled": False,
            },
        ),
    }
    options = (
        (
            "max-line-length-suggestions",
            {
                "type": "int",
                "default": 0,
                "metavar": "<int>",
                "help": (
                    "Max line length for which to sill emit suggestions. "
                    "Used to prevent optional suggestions which would get split "
                    "by a code formatter (e.g., black). "
                    "Will default to the setting for ``max-line-length``."
                ),
            },
        ),
        # Settings to customize assignment expression suggestions
        (
            "assignment-expr-not",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the test contains a ``not``. Ie. for ``if not var: ...``."
                ),
            },
        ),
        (
            "assignment-expr-compare-none",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the test contains ``is None`` or ``is not None``. "
                    "Ie. for ``if var is None: ...``."
                ),
            },
        ),
        (
            "assignment-expr-compare-const",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the test contains a constant, NAME, or ATTRIBUTE. "
                    "Ie. for ``if var == 'Hello World': ...``, "
                    "``if var == CONST: ...``, ``if var == x.attribute: ...``."
                ),
            },
        ),
        (
            "assignment-expr-compare-in",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the test contains an ``in`` or ``not in`` check. "
                    "Ie. for ``if var in some_list: ...``."
                ),
            },
        ),
        (
            "assignment-expr-compare-call",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the test contains a function call. "
                    "Ie. for ``if var == some_func(): ...``."
                ),
            },
        ),
        (
            "assignment-expr-compare-call-func-names",
            {
                "default": ("get", "len"),
                "type": "csv",
                "metavar": "<function_names>",
                "help": (
                    "List of function names in tests to still suggest "
                    "assignment expressions. Leave empty to allow all names, "
                    "disable by setting ``assignment-expr-compare-call=False``."
                ),
            },
        ),
        (
            "assignment-expr-assign-not",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value begins with ``not``. "
                    "Ie. for ``var = not some_value``."
                ),
            },
        ),
        (
            "assignment-expr-assign-getitem",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value is a __getitem__ call. "
                    "Ie. for ``var = config[some_val]``."
                ),
            },
        ),
        (
            "assignment-expr-assign-annotation",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment is an annotated assignment. "
                    "Ie. for ``var: int = some_function()``."
                ),
            },
        ),
        (
            "assignment-expr-assign-await",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value begins with an ``await``. "
                    "Ie. for ``var = await some_function()``."
                ),
            },
        ),
        (
            "assignment-expr-assign-ifexp",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value is an if expressions. "
                    "Ie. for ``var = 2 if some_bool else 42``."
                ),
            },
        ),
        (
            "assignment-expr-assign-comprehension",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value is a comprehension. "
                    "Ie. for ``var = [x.attr for x in func()]``."
                ),
            },
        ),
        (
            "assignment-expr-assign-lambda",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value is a lambda expression. "
                    "Ie. for ``var = lambda: print('Hello')``."
                ),
            },
        ),
        (
            "assignment-expr-assign-compare",
            {
                "default": True,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value is a comparison. "
                    "Ie. for ``var = 42 == some_other_var``."
                ),
            },
        ),
        (
            "assignment-expr-assign-boolop",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value is a boolean operation. "
                    "Ie. for ``var = 42 and some_other_var``."
                ),
            },
        ),
        (
            "assignment-expr-assign-binop",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value is a binary operation. "
                    "Ie. for ``var = 1 | 2``."
                ),
            },
        ),
        (
            "assignment-expr-assign-call",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": (
                    "Should assignment expressions be suggested "
                    "if the assignment value is a function call. "
                    "Ie. for ``var = some_function()``."
                ),
            },
        ),
        (
            "assignment-expr-assign-call-func-names",
            {
                "default": (),
                "type": "csv",
                "metavar": "<function_names>",
                "help": (
                    "List of function names in assignment values to still suggest "
                    "assignment expressions. Leave empty to allow all names, "
                    "disable by setting ``assignment-expr-assign-call=False``."
                ),
            },
        ),
    )

    def open(self) -> None:
        py_version = self.linter.config.py_version
        self._py36_plus = py_version >= (3, 6)
        self._py38_plus = py_version >= (3, 8)
        self._max_length: int = (
            self.linter.config.max_line_length_suggestions
            or self.linter.config.max_line_length
        )

        self.conf_assignment_expr_not: bool = self.config.assignment_expr_not
        self.conf_assignment_expr_compare_none: bool = (
            self.config.assignment_expr_compare_none
        )
        self.conf_assignment_expr_compare_const: bool = (
            self.config.assignment_expr_compare_const
        )
        self.conf_assignment_expr_compare_in: bool = (
            self.config.assignment_expr_compare_in
        )
        self.conf_assignment_expr_compare_call: bool = (
            self.config.assignment_expr_compare_call
        )
        self.conf_assignment_expr_compare_call_func_names: Tuple[
            str, ...
        ] = self.config.assignment_expr_compare_call_func_names

        self.conf_assignment_expr_assign_not: bool = (
            self.config.assignment_expr_assign_not
        )
        self.conf_assignment_expr_assign_getitem: bool = (
            self.config.assignment_expr_assign_getitem
        )
        self.conf_assignment_expr_assign_annotation: bool = (
            self.config.assignment_expr_assign_annotation
        )
        self.conf_assignment_expr_assign_await: bool = (
            self.config.assignment_expr_assign_await
        )
        self.conf_assignment_expr_assign_ifexp: bool = (
            self.config.assignment_expr_assign_ifexp
        )
        self.conf_assignment_expr_assign_comprehension: bool = (
            self.config.assignment_expr_assign_comprehension
        )
        self.conf_assignment_expr_assign_lambda: bool = (
            self.config.assignment_expr_assign_lambda
        )
        self.conf_assignment_expr_assign_compare: bool = (
            self.config.assignment_expr_assign_compare
        )
        self.conf_assignment_expr_assign_boolop: bool = (
            self.config.assignment_expr_assign_boolop
        )
        self.conf_assignment_expr_assign_binop: bool = (
            self.config.assignment_expr_assign_binop
        )
        self.conf_assignment_expr_assign_call: bool = (
            self.config.assignment_expr_assign_call
        )
        self.conf_assignment_expr_assign_call_func_names: Tuple[
            str, ...
        ] = self.config.assignment_expr_assign_call_func_names

    @only_required_for_messages("prefer-typing-namedtuple")
    def visit_call(self, node: nodes.Call) -> None:
        if self._py36_plus:
            called = safe_infer(node.func)
            if called and called.qname() == "collections.namedtuple":
                self.add_message(
                    "prefer-typing-namedtuple", node=node, confidence=INFERENCE
                )

    @only_required_for_messages("consider-using-namedtuple-or-dataclass")
    def visit_dict(self, node: nodes.Dict) -> None:
        self._check_dict_consider_namedtuple_dataclass(node)

    @only_required_for_messages("consider-using-tuple")
    def visit_for(self, node: nodes.For) -> None:
        if isinstance(node.iter, nodes.List):
            self.add_message("consider-using-tuple", node=node.iter)

    @only_required_for_messages("consider-using-tuple")
    def visit_comprehension(self, node: nodes.Comprehension) -> None:
        if isinstance(node.iter, nodes.List):
            self.add_message("consider-using-tuple", node=node.iter)

    @only_required_for_messages("consider-using-assignment-expr")
    def visit_if(self, node: nodes.If) -> None:
        if self._py38_plus:
            self._check_consider_using_assignment_expr(node)

    def _check_dict_consider_namedtuple_dataclass(self, node: nodes.Dict) -> None:
        """Check if dictionary values can be replaced by Namedtuple or Dataclass."""
        if not (
            (
                isinstance(node.parent, (nodes.Assign, nodes.AnnAssign))
                and isinstance(node.parent.parent, nodes.Module)
            )
            or (
                isinstance(node.parent, nodes.AnnAssign)
                and isinstance(node.parent.target, nodes.AssignName)
                and utils.is_assign_name_annotated_with(node.parent.target, "Final")
            )
        ):
            # If dict is not part of an 'Assign' or 'AnnAssign' node in
            # a module context OR 'AnnAssign' with 'Final' annotation, skip check.
            return

        # All dict_values are itself dict nodes
        if len(node.items) > 1 and all(
            isinstance(dict_value, nodes.Dict) for _, dict_value in node.items
        ):
            KeyTupleT = tuple[type[nodes.NodeNG], str]

            # Makes sure all keys are 'Const' string nodes
            keys_checked: set[KeyTupleT] = set()
            for _, dict_value in node.items:
                dict_value = cast(nodes.Dict, dict_value)
                for key, _ in dict_value.items:
                    key_tuple = (type(key), key.as_string())
                    if key_tuple in keys_checked:
                        continue
                    inferred = safe_infer(key)
                    if not (
                        isinstance(inferred, nodes.Const)
                        and inferred.pytype() == "builtins.str"
                    ):
                        return
                    keys_checked.add(key_tuple)

            # Makes sure all subdicts have at least 1 common key
            key_tuples: list[tuple[KeyTupleT, ...]] = []
            for _, dict_value in node.items:
                dict_value = cast(nodes.Dict, dict_value)
                key_tuples.append(
                    tuple((type(key), key.as_string()) for key, _ in dict_value.items)
                )
            keys_intersection: set[KeyTupleT] = set(key_tuples[0])
            for sub_key_tuples in key_tuples[1:]:
                keys_intersection.intersection_update(sub_key_tuples)
            if not keys_intersection:
                return

            self.add_message("consider-using-namedtuple-or-dataclass", node=node)
            return

        # All dict_values are itself either list or tuple nodes
        if len(node.items) > 1 and all(
            isinstance(dict_value, (nodes.List, nodes.Tuple))
            for _, dict_value in node.items
        ):
            # Make sure all sublists have the same length > 0
            list_length = len(node.items[0][1].elts)
            if list_length == 0:
                return
            for _, dict_value in node.items[1:]:
                if len(dict_value.elts) != list_length:
                    return

            # Make sure at least one list entry isn't a dict
            for _, dict_value in node.items:
                if all(isinstance(entry, nodes.Dict) for entry in dict_value.elts):
                    return

            self.add_message("consider-using-namedtuple-or-dataclass", node=node)
            return

    def _check_consider_using_assignment_expr(self, node: nodes.If) -> None:
        """Check if an assignment expression (walrus operator) can be used.

        For example if an assignment is directly followed by an if statement:
        >>> x = 2
        >>> if x:
        >>>     ...

        Can be replaced by:
        >>> if (x := 2):
        >>>     ...

        Note: Assignment expressions were added in Python 3.8
        """
        # Check if `node.test` contains a `Name` node
        node_name: nodes.Name | None = None
        if isinstance(node.test, nodes.Name):
            node_name = node.test
        elif (
            isinstance(node.test, nodes.UnaryOp)
            and node.test.op == "not"
            and isinstance(node.test.operand, nodes.Name)
            and self.conf_assignment_expr_not
        ):
            node_name = node.test.operand
        elif (
            # pylint: disable=too-many-boolean-expressions
            isinstance(node.test, nodes.Compare)
            and isinstance(node.test.left, nodes.Name)
            and len(node.test.ops) == 1
            and (
                # is None OR is not None
                self.conf_assignment_expr_compare_none
                and node.test.ops[0][0] in {"is", "is not"}
                and isinstance(node.test.ops[0][1], nodes.Const)
                and node.test.ops[0][1].value is None
                # Constants and calls
                or (
                    self.conf_assignment_expr_compare_const
                    and isinstance(
                        node.test.ops[0][1], (nodes.Const, nodes.Name, nodes.Attribute)
                    )
                    # For calls check name / attrname is in allow list
                    or self.conf_assignment_expr_compare_call
                    and (
                        len(self.conf_assignment_expr_compare_call_func_names) == 0
                        or isinstance(node.test.ops[0][1], nodes.Call)
                        and (
                            isinstance(node.test.ops[0][1].func, nodes.Attribute)
                            and node.test.ops[0][1].func.attrname
                            in self.conf_assignment_expr_compare_call_func_names
                            or isinstance(node.test.ops[0][1].func, nodes.Name)
                            and node.test.ops[0][1].func.name
                            in self.conf_assignment_expr_compare_call_func_names
                        )
                    )
                )
                and (
                    node.test.ops[0][0] not in {"in", "not in"}
                    or self.conf_assignment_expr_compare_in
                )
            )
        ):
            node_name = node.test.left
        else:
            return

        # Make sure the previous node is an assignment to the same name
        # used in `node.test`. Furthermore, ignore if assignment spans multiple lines.
        prev_sibling = node.previous_sibling()
        if self._check_prev_sibling_to_if_stmt(prev_sibling, node_name.name):
            if not self._check_assignment_value(prev_sibling.value):
                return

            # Check if match statement would be a better fit.
            # I.e. multiple ifs that test the same name.
            if CodeStyleChecker._check_ignore_assignment_expr_suggestion(
                node, node_name.name
            ):
                return

            # Build suggestion string. Check length of suggestion
            # does not exceed max-line-length-suggestions
            test_str = node.test.as_string().replace(
                node_name.name,
                f"({node_name.name} := {prev_sibling.value.as_string()})",
                1,
            )
            suggestion = f"if {test_str}:"
            if (
                node.col_offset is not None
                and len(suggestion) + node.col_offset > self._max_length
            ) or len(suggestion) > self._max_length:
                return

            self.add_message(
                "consider-using-assignment-expr",
                node=node_name,
                args=(suggestion,),
            )

    def _check_prev_sibling_to_if_stmt(
        self, prev_sibling: nodes.NodeNG | None, name: str | None
    ) -> TypeGuard[nodes.Assign | nodes.AnnAssign]:
        """Check if previous sibling is an assignment with the same name.

        Ignore statements which span multiple lines.
        """
        if prev_sibling is None or prev_sibling.tolineno - prev_sibling.fromlineno != 0:
            return False

        if (
            isinstance(prev_sibling, nodes.Assign)
            and len(prev_sibling.targets) == 1
            and isinstance(prev_sibling.targets[0], nodes.AssignName)
            and prev_sibling.targets[0].name == name
        ):
            return True
        if (
            isinstance(prev_sibling, nodes.AnnAssign)
            and isinstance(prev_sibling.target, nodes.AssignName)
            and prev_sibling.target.name == name
            and prev_sibling.value is not None
            and self.conf_assignment_expr_assign_annotation
        ):
            return True
        return False

    # pylint: disable-next=too-many-return-statements
    def _check_assignment_value(
        self, assign_value: Optional[nodes.NodeNG]
    ) -> TypeGuard[nodes.NodeNG]:
        if isinstance(assign_value, (nodes.Const, nodes.Name, nodes.Attribute)):
            return True
        if isinstance(assign_value, nodes.UnaryOp):
            return self.conf_assignment_expr_assign_not
        if isinstance(assign_value, nodes.Subscript):
            return self.conf_assignment_expr_assign_getitem
        if isinstance(assign_value, nodes.Await):
            return self.conf_assignment_expr_assign_await
        if isinstance(assign_value, nodes.IfExp):
            return self.conf_assignment_expr_assign_ifexp
        if isinstance(assign_value, nodes.ComprehensionScope):
            return self.conf_assignment_expr_assign_comprehension
        if isinstance(assign_value, nodes.Lambda):
            return self.conf_assignment_expr_assign_lambda
        if isinstance(assign_value, nodes.Compare):
            return (
                len(assign_value.ops) == 1 and self.conf_assignment_expr_assign_compare
            )
        if isinstance(assign_value, nodes.BoolOp):
            return self.conf_assignment_expr_assign_boolop
        if isinstance(assign_value, nodes.BinOp):
            return self.conf_assignment_expr_assign_binop
        if isinstance(assign_value, nodes.Call):
            return len(self.conf_assignment_expr_assign_call_func_names) == 0 or (
                isinstance(assign_value.func, nodes.Attribute)
                and assign_value.func.attrname
                in self.conf_assignment_expr_assign_call_func_names
                or isinstance(assign_value.func, nodes.Name)
                and assign_value.func.name
                in self.conf_assignment_expr_assign_call_func_names
            )
        return True

    @staticmethod
    def _check_ignore_assignment_expr_suggestion(
        node: nodes.If, name: str | None
    ) -> bool:
        """Return True if suggestion for assignment expr should be ignored.

        E.g., in cases where a match statement would be a better fit
        (multiple conditions).
        """
        if isinstance(node.test, nodes.Compare):
            next_if_node: nodes.If | None = None
            next_sibling = node.next_sibling()
            if len(node.orelse) == 1 and isinstance(node.orelse[0], nodes.If):
                # elif block
                next_if_node = node.orelse[0]
            elif isinstance(next_sibling, nodes.If):
                # separate if block
                next_if_node = next_sibling

            if (  # pylint: disable=too-many-boolean-expressions
                next_if_node is not None
                and (
                    (
                        isinstance(next_if_node.test, nodes.Compare)
                        and isinstance(next_if_node.test.left, nodes.Name)
                        and next_if_node.test.left.name == name
                    )
                    or (
                        isinstance(next_if_node.test, nodes.Name)
                        and next_if_node.test.name == name
                    )
                )
            ):
                return True
        return False

    @only_required_for_messages("consider-using-augmented-assign")
    def visit_assign(self, node: nodes.Assign) -> None:
        is_aug, op = utils.is_augmented_assign(node)
        if is_aug:
            self.add_message(
                "consider-using-augmented-assign",
                args=f"{op}=",
                node=node,
                line=node.lineno,
                col_offset=node.col_offset,
                confidence=INFERENCE,
            )


def register(linter: PyLinter) -> None:
    linter.register_checker(CodeStyleChecker(linter))
