"""Tests for fixme and its disabling and enabling."""
# pylint: disable=missing-function-docstring, unused-variable, pointless-string-statement

# +1: [fixme]
# FIXME: beep
# +1: [fixme]
    # TODO: don't forget indented ones should trigger
# +1: [fixme]
# TODO: that precedes another TODO: is treated as one and the message starts after the first
# +1: [fixme]
#           TODO: large indentations after hash are okay

# but things cannot precede the TODO: do this

def function():
    variable = "FIXME: Ignore me!"
    # +1: [fixme]
    test = "text"  # FIXME: Valid test

    # +1: [fixme]
    # TODO: Do something with the variables
    # +1: [fixme]
    xxx = "n/a"  # XXX: Fix this later
    # +1: [fixme]
    #FIXME: no space after hash
    # +1: [fixme]
    #todo: no space after hash

    # +1: [fixme]
	# FIXME: this is broken
    # +1: [fixme]
    # ./TODO: find with notes
	# +1: [fixme]
    # TO make something DO: find with regex
	# FIXME: this is broken (ISSUE-1234)

    #FIXME: in fact nothing to fix #pylint: disable=fixme
    #TODO: in fact nothing to do #pylint: disable=fixme
    #TODO: in fact nothing to do #pylint: disable=line-too-long, fixme, useless-suppression
    # Todoist API mentioned should not result in a message.

# pylint: disable-next=fixme
# FIXME: Don't raise when the message is disabled

"""TODO: Don't raise when docstring fixmes are disabled"""

# This line needs to be at the end of the file to make sure it doesn't end with a comment
# Pragma's compare against the 'lineno' attribute of the respective nodes which
# would stop too soon otherwise.
print()
