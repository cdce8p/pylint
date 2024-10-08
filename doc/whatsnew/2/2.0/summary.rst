:Release: 2.0
:Date: 2018-07-15

Summary -- Release highlights
=============================

* Dropped support for Python 2. This release will work only on Python 3.4+.

  If you need to use ``pylint`` with Python 2, you can use Pylint 1.9+. We'll continue
  to do bug releases until 2020, when Python 2 goes officially EOL.
  ``pylint`` will gain the ability to analyze Python 2 files, but some checks might not work
  as they will assume that their running environment is Python 2.

* Given the dropping of Python 2, the Python 3 porting mode (enabled via ``--py3k``) can now
  also run with Python 3.

  The porting mode used to be a no-op on Python 3, but most of the messages can now be emitted
  when the running interpreter is Python 3. The only messages that won't be emitted are those that
  rely on a particular syntax specific to Python 2, for instance ``print`` as a statement.


New checkers
============
* A new check was added, ``useless-object-inheritance``.

  This refactoring message is emitted when pylint detects that a class inherits from object,
  which is redundant as in Python 3, every class implicitly inherits from object.

  .. code-block:: python

    class A(object):
        pass

    class A:    # better
        pass

* A new check was added, ``comparison-with-callable``.

  This refactoring message is emitted when pylint detects that a comparison with a callable was
  made, which might suggest that some parenthesis were omitted, resulting in potential unwanted
  behaviour.

  .. code-block:: python

    def foo():
        return None

    def goo():
        return None

    if foo == 786:  # bad
        pass

    if foo() == 786:    # good
        pass

* A new check was added, ``chained-comparison``.

  This refactoring message is emitted if a boolean operation can be simplified by chaining some
  of its operations. check below example:

  .. code-block:: python

    if a < b and b < c:
        pass

    if a < b < c:   # better
        pass

* A new check was added, ``useless-import-alias``.

  This refactoring message is emitted when an import alias does not rename the original package.

  .. code-block:: python

    import numpy as numpy # bad
    import numpy as np # good
    from collection import OrderedDict as OrderedDict # bad
    from collection import OrderedDict as ordered_dict # good

* A new check was added, ``comparison-with-itself``.

  This refactoring message is emitted when a variable is compared against itself.

  .. code-block:: python

    if variable == variable:  # bad
        pass

* A new check was added, ``consider-using-in``.

  This refactoring message is emitted when a variable is compared against multiple
  values concatenated by ors instead of using the faster, more idiomatic "in" check.

  .. code-block:: python

    if variable == 1 or variable == 2 or variable == 3:  # bad
        pass

    if variable in (1, 2, 3):  # good
        pass

* A new check was added, ``consider-using-get``.

  This refactoring message is emitted when manually checking if a key is in a dictionary
  and getting its value if it is (and optionally a default if not)
  instead of the more idiomatic dict.get.

  .. code-block:: python

    if 'key' in dictionary:  # bad
        variable = dictionary['key']
    else:
        variable = 'default'

    variable = dictionary.get('key', 'default')  # good

* A new check was added, ``consider-using-join``.

  This refactoring message is emitted when using a for loop over an iterable to join strings
  instead of the faster, less memory consuming and more idiomatic str.join(sequence).

  .. code-block:: python

    result = ''  # bad
    for number in ['1', '2', '3']:
        result += number

    result = ''.join(['1', '2', '3'])  # good

* New ``useless-return`` message when function or method ends with a "return" or
  "return None" statement and this is the only return statement in the body.

* New ``use-symbolic-message-instead`` message when a message is activated or
  deactivated by id instead of symbol.
  The use of symbol is more explicit and easier to remind.

* A new check was added, ``consider-swap-variables``.

  This refactoring message is emitted when using a temporary variable in order
  to swap the values of two variables instead of the shorter, more idiomatic
  approach with tuple-unpacking.

  Instead of a temporary variable, the one-line syntax with commas should be used.

  See this `style guide`_ document or the Pycon 2007 `swap values presentation` for details.

  .. code-block:: python

     temp = a  # the wrong way
     a = b
     b = temp

     a, b = b, a  # the right way

* Two new checks, ``invalid-envvar-value`` and ``invalid-envvar-default``, were added.

  The former is trigger whenever pylint detects that environment variable manipulation
  functions uses a different type than strings, while the latter is emitted whenever
  the said functions are using a default variable of different type than expected.

* A new check was added, ``subprocess-popen-preexec-fn``,

  This refactoring message is emitted when using the keyword argument preexec_fn
  when creating subprocess.Popen instances which may be unsafe when used in
  the presence of threads.

  See `subprocess.Popen <https://docs.python.org/3/library/subprocess.html#popen-constructor>`_
  for full warning details.

* New ``try-except-raise`` message when an except handler block has a bare
  ``raise`` statement as its first operator or the exception type being raised
  is the same as the one being handled.

*  New ``possibly-unused-variable`` check added.

  This is similar to ``unused-variable``, the only difference is that it is
  emitted when we detect a locals() call in the scope of the unused variable.
  The ``locals()`` call could potentially use the said variable, by consuming
  all values that are present up to the point of the call. This new check
  allows to disable this error when the user intentionally uses ``locals()``
  to consume everything.

  For instance, the following code will now trigger this new error:

  .. code-block:: python

     def func():
         some_value = some_call()
         return locals()

* New ``unhashable-dict-key`` check added to detect dict lookups using
  unhashable keys such as lists or dicts.

* New ``self-cls-assignment`` warning check added.

  This is warning if the first argument of an instance/ class method gets
  assigned

  .. code-block:: python

     class Foo(object):
         def foo(self, bar):
             self = bar

* New verbose mode option ``--verbose`` to display of extra non-checker-related output. Disabled by default.

* Two new checks were added for recommending dict and set comprehensions where possible.

  These two checks are going to flag the following examples:

  .. code-block:: python

     dict([(k, v) for (k, v) in ...]) # better as {k: v for k, v in ...}
     set([k for k in ...]) # better as {k for k in ...}

Other Changes
=============

* A couple of performance improvements brought to ``astroid`` should make
  ``pylint`` should be a bit faster as well.

  We added a new flag, ``max_inferable_values`` on ``astroid.MANAGER`` for
  limiting the maximum amount of values that ``astroid`` can infer when inferring
  values. This change should improve the performance when dealing with large frameworks
  such as ``django``.
  You can also control this behaviour with ``pylint --limit-inference-results``

  We also rewrote how ``nodes_of_class`` and ``get_children`` methods operate which
  should result in a performance boost for a couple of checks.

* Fix a false positive ``inconsistent-return-statements`` message when exception is raised inside
  an else statement.

* Don't warn for ``missing-type-doc`` and/or ``missing-return-type-doc``, if type annotations
  exist on the function signature for a parameter and/or return type.

* Fix a false positive ``inconsistent-return-statements`` message when if
  statement is inside try/except.

* Fix a false positive ``inconsistent-return-statements`` message when
  ``while`` loop are used.

* Fix emission of false positive ``no-member`` message for class with
  "private" attributes whose name is mangled.

* Fix ``unused-argument`` false positives with overshadowed variable in dictionary comprehension.

* Fixing false positive ``inconsistent-return-statements`` when
  never returning functions are used (i.e such as sys.exit).

* Fix false positive ``inconsistent-return-statements`` message when a
  function is defined under an if statement.

* Fix false positive ``inconsistent-return-statements`` message by
  avoiding useless exception inference if the exception is not handled.

* Fix false positive ``undefined-variable`` for lambda argument in class definitions

* Suppress false-positive ``not-callable`` messages from certain staticmethod descriptors

* Expand ``ignored-argument-names`` include starred arguments and keyword arguments

* ``singleton-comparison`` will suggest better boolean conditions for negative conditions.

* ``undefined-loop-variable`` takes in consideration non-empty iterred objects before emitting.

  For instance, if the loop iterable is not empty, this check will no longer be emitted.

* Enum classes no longer trigger ``too-few-methods``

* Special methods now count towards ``too-few-methods``,
  and are considered part of the public API.
  They are still not counted towards the number of methods for
  ``too-many-methods``.

* ``docparams`` extension allows abstract methods to document returns
  documentation even if the default implementation does not return something.
  They also no longer need to document raising a ``NotImplementedError.``

* Skip wildcard import check for ``__init__.py``.

* Don't warn 'useless-super-delegation' if the subclass method has different type annotations.

* Don't warn that a global variable is unused if it is defined by an import

  .. code-block:: python

    def func():
        global sys
        import sys

* Added basic support for postponed evaluation of function annotations.

  If ``pylint`` detects the corresponding ``from __future__ import annotations`` import,
  it will not emit ``used-before-assignment`` and ``undefined-variable`` in the cases
  triggered by the annotations.

  More details on the postponed evaluation of annotations can be read in
  `PEP 563`_.

* A new command line option was added, ``--exit-zero``, for the use of continuous integration
  scripts which abort if a command returns a non-zero status code.  If the
  option is specified, and Pylint runs successfully, it will exit with 0
  regardless of the number of lint issues detected.

  Configuration errors, parse errors, and calling Pylint with invalid
  command-line options all still return a non-zero error code, even if
  ``--exit-zero`` is specified.

* Don't emit ``unused-import`` anymore for typing imports used in type comments. For instance,
  in the following example pylint used to complain that ``Any`` and ``List`` are not used,
  while they should be considered used by a type checker.

  .. code-block:: python

      from typing import Any, List
      a = 1 # type: List[Any]

* Fix false positive ``line-too-long`` for commented lines at the end of module

* Fix emitting ``useless-super-delegation`` when changing the default value of keyword arguments.

* Support ``typing.TYPE_CHECKING`` for *unused-import* errors

  When modules are imported under ``typing.TYPE_CHECKING`` guard, ``pylint``
  will no longer emit *unused-import*.

* Fix false positive ``unused-variable`` in lambda default arguments

* ``assignment-from-no-return`` considers methods as well as functions.

  If you have a method that doesn't return a value, but later on you assign
  a value to a function call to that method (so basically it will be ``None``),
  then ``pylint`` is going to emit an ``assignment-from-no-return`` error.

* A new flag was added, ``--ignore-none`` which controls the ``no-member``
  behaviour with respect to ``None`` values.

  Previously ``pylint`` was not emitting ``no-member`` if it inferred that
  the owner of an attribute access is a ``None`` value. In some cases,
  this might actually cause bugs, so if you want to check for ``None`` values
  as well, pass ``--ignore-none=n`` to pylint.

* Fix false-positive ``bad-continuation`` for with statements

* Fix false-positive ``bad-whitespace`` message for typing annoatations
  with ellipses in them

* Fix false-positive ``undefined-variable`` for nested lambdas


.. _PEP 563: https://peps.python.org/pep-0563/
.. _style guide: https://docs.python-guide.org/writing/style/
