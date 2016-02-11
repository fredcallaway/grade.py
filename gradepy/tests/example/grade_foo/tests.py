"""Example test script using grade.py

Test functions are written as methods which take a module as an
argument. Behind the scenes this method will be run using both
the student and master modules. Then the output will be compared.

Test methods are generator functions, using the yield syntax. Any
expression that is yielded is considered to be a sub-test-case. If
the value is different using the student and master modules, this
will be recorded in the report, which is meant to be used directly
as feedback to students, along with human-written comments.

Test functions must be marked with the TESTER.register decorator.
You can optioally provide information about what function(s) the
function tests for error carried forward.
"""
from gradepy import Tester, Check, utils

from master import foo

TESTER = Tester(foo, points=1865, note='An example grading program.')

@TESTER.setup(every_time=False)
def setup(student_file):
    # This function will run on the student file the first time
    # grade.py is run on a file in that directory.
    return


@TESTER.register(tests=['add_one'])
def test_add_one(module):
    """Introduces the Check class and basic testing patterns."""

    # The statement below can be read as:
    # assert student.add_one(1) == master.add_one(1).
    yield Check('add_one(1)')

    # The first argument to Check is an expression, which will be evaluated
    # with the tested module and this function's locals in scope.
    big = 100
    yield Check('add_one(big)')

    # The above statement will generate the feedback:
    # add_one(big) should return 101, but it returns '!?!?!'

    # If we want the value of big to be included in the feedback,
    # we wrap it with {curly braces}
    quip = 'takes one to know'
    yield Check('add_one({quip})')

    # Note that {quip} will be replaced by 'takes one to know'
    # with quotations preserved.

    # We can supply a note, which will be printed along with the
    # standard feedback for a mistake.
    yield Check('add_one(101)', note='This is not an edge case.')


@TESTER.register()
def test_divide(module):
    """Demonstrates how exceptions are handled.

    Also demonstrates the inferiority of python 2.

    By the way, this doc string will be included in the feedback. You
    could include a grading guide here.
    """

    # If an exception is raised in a Check expression, it will be 
    # caught and recorded in the feedback. But the test will go on!
    yield Check('divide(1, divide(1, 2))')  # 1 / (1/2)

    # However, if an exception is raised outside a Check statement,
    # the test function will not be completed.
    zero = module.divide(1, 0)
    
    yield Check('zero', note='This test will not be run.')


@TESTER.register()
def test_foo(module):
    """Demonstrates testing a stateful class."""
    foo = module.Foo('2')
    yield Check('foo.arg')

    # Anything that you execute inside of outside of Checks will
    # have the expected side effects.
    foo.bar()
    yield Check('foo.arg', note='after calling foo.bar()')

    yield Check('foo.bar()')
    yield Check('foo.arg', note='after calling foo.bar() twice')

    # Generally, you should use bare code (not in Check) when you
    # only care about the side effect, because you don't want
    # the test case to go on if the setup code fails.


# A very nice feature of grade.py is automated error carried forward. The
# `tests` parameter to the register decorator indicates the tested function(s).
# If the test finds errors, those functions will be added to a list of faulty
# functions to be replaced by the solution function for ECF. The `depends`
# parameter indicates which functions the currently tested functions depend on.
#
# If the test method below finds errors, and `add_one` has previously been
# found to have errors, then the test will be reexecuted using `ecf_mod`, a
# module based on the student module but with `add_one` replaced with the
# master implementation.
#
# Implementation Note: At present, we make no promises about exactly
# which functions may be changed during ECF. The current implementation
# never removes a correct solution function from the ECF module after it
# is added. It is not clear to me what the best way to handle this is.

@TESTER.register(depends=['add_one'])
def test_add_two(module):
    """Demonstrates error carried forward."""
    yield Check('add_two(1)')

    # This will fail the first time, but will be corrected with ECF.
    # Both facts will be included in the feedback
    yield Check('add_two(99)')


@TESTER.register()
def test_raw_input(module):
    """Demonstrates testing with stdin and stdout."""
    
    # We simulate stdin as a queue. Push to the queue like so:
    #TESTER.stdin.put('pig')
    # The next time the module calls raw_input(), it will get 'pig'

    # We also capture all stdout of code exectude in a Check. If
    # the student and master module print different things while
    # executing cook_stdin(), this will be noted in the feedback.


    yield Check('cook_stdin()', stdin='pig')


'''
OUTPUT:

======================================================================
Automated testing for submissions/flc37/foo.py
======================================================================

An example grading program.

Maximum points: 1865

-----------------( test_add_one )-----------------
"""Introduces the Check class and basic testing patterns."""

add_one(big) should be 101, but it is '!?!?!'

add_one('takes one to know') should be 'takes one to know one', but it is 'takes one to know two'

add_one(101) should be 102, but it is '!?!?!'
 Note: This is not an edge case.

-----------------( test_divide )------------------
"""Demonstrates how exceptions are handled.

    Also demonstrates the inferiority of python 2.

    By the way, this doc string will be included in the feedback. You
    could include a grading guide here."""

divide(1, divide(1, 2)) should be 2.0, but student code raised an exception:
  File "submissions/flc37/foo.py", line 23, in divide
    return x / y
ZeroDivisionError: integer division or modulo by zero

Fatal exception in student code. Cannot finish test.
  File "/Users/fred/grade.py.git/gradepy/tests/example/grade_foo/tests.py", line 68, in test_divide
    zero = module.divide(1, 0)
  File "submissions/flc37/foo.py", line 23, in divide
    return x / y
ZeroDivisionError: integer division or modulo by zero

-------------------( test_foo )-------------------
"""Demonstrates testing a stateful class."""

foo.arg should be '222', but it is '22'
 Note: after calling foo.bar()

foo.arg should be '222222222', but it is '2222'
 Note: after calling foo.bar() twice

-----------------( test_add_two )-----------------
"""Demonstrates error carried forward."""

add_two(99) should be 101, but it is '!?!?!'
Trying again with helper functions corrected.
Problem solved!

----------------( test_raw_input )----------------
"""Demonstrates testing with stdin and stdout"""

cook_stdin() should be 'bacon', but it is None

cook_stdin() should print None, but it prints 'pork\n'

'''
