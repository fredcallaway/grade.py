# -*- coding: utf-8 -*-

"""Object oriented grading of python modules.

Defines an abstract base class, Tester, to be used for grading
python modules. This module differs from standard testing
strategies in two major ways. First, it relies on a correct
implementation of the module, making the creation of test
cases very easy. Second, it is designed to identify graded
quality of performance, rather than a binary PASS/FAIL
judgement. It also provides Error Carried Forward functionality.

See show_grade.py for example usage.
"""
from __future__ import print_function
import traceback
import inspect
import imp
import os
import re
import string
import sys

import utils

class Check(object):
    """Provides an interface for testing with Tester.

    Args:
        expr (str): a python expression, the value of which will be verified.
        note (str): a note to provide in the feedback if `expr` does not
          evalueate to the same value under the student and master mdoules.

    See show_grade.py for example usage. Key things to note are that side
    effects occur just as if you executed expr in the calling scope, and that
    exceptions raised while evaluating will be caught and recordede. Both expr
    and note will be formatted with the calling scope's name space, thus they
    can include {variable_name}s.
    """
    def __init__(self, expr, note='', stdin=(), check=None, stdout_check=None):
        # Yes, python allows us to access the local name space of the
        # calling function (or module). This prevents us from requiring
        # the user to supply locals() as an argument.
        if not isinstance(expr, str):
            raise TypeError('Check expr must be a string.')

        self.env = inspect.stack()[1][0].f_locals
        self.expr = literal_format(expr, **self.env)
        self._check = check
        self._stdout_check = stdout_check

        # Set note.
        if note:
            self.note = '\n Note: ' + literal_format(note, **self.env)
        else:
            self.note = ''

        # Write supplied stdin.
        if isinstance(stdin, str):
            sys.stdin.put(stdin)
        else:
            for x in stdin:
                sys.stdin.put(x)

        # Evaluate expr within env.
        module_env = self.env['module'].__dict__
        with utils.capture_stdout() as out:
            try:
                self.val = eval(self.expr, module_env, self.env)
            except Exception as e:
                self.val = StudentException(e, skip=4)
        if out.captured:
            self.stdout = '----begin stdout----\n' + out.captured + '\n-----end stdout-----'
        else:
            self.stdout = None

    def check(self, student_val):
        """Returns True if student_val is correct."""
        master = self  # This function should only ever be called as master.check()
        if not self.env['module'].__name__.startswith('master'):
            raise TestError('Attempted to call check() from the student Check.')

        if self._check:
            # Use the check function provided, which may be
            # more lenient than 100% match to master.val
            return self._check(master.val, student_val)
        else:
            return master.val == student_val and type(master.val) == type(student_val)

    def stdout_check(self, student_stdout):
        """Returns True if student stdout is correct."""
        master = self
        if not self.env['module'].__name__.startswith('master'):
            raise TestError('Attempted to call stdout_check() from the student Check.')

        if self._stdout_check:
            return self._stdout_check(master.stdout, student_stdout)
        else:
            return master.stdout == student_stdout


class Tester(object):
    """A class for grading modules."""
    def __init__(self, master_mod, points=0, note=None):
        self.master_mod = master_mod
        self._adjust_modules(master_mod)
        self.log_correct = False
        self.setup_func = None
        self.test_funcs = []
        self.points = points
        self.note = note
        self.stdin = FakeStdin()
        sys.stdin = self.stdin

    def __call__(self, student_file, log_func=print, func_re=None):
        """Runs the tests on one student submission."""

        # This state is student specific, and is thus reset upon every call.
        self.log = log_func
        self.bad_funcs = set()

        if self.setup_func:
            self.setup_func(student_file)
        self.student_mod, self.ecf_mod = self._get_modules(student_file)
        self._adjust_modules(self.student_mod, self.ecf_mod)

        # Banner.
        self.log('\n\n' + '=' * 70)
        self.log('Automated testing for ' + student_file)
        self.log('=' * 70)
        if self.note:
            self.log('\n' + self.note + '\n')
        if self.points:
            self.log('Maximum points: {}'.format(self.points))

        if func_re:
            self.log("Filtering test functions by regex: '{}'".format(func_re.pattern))
            tests = (f for f in self.test_funcs if func_re.search(f.__name__))
        else:
            tests= self.test_funcs

        self._run_tests(tests)

    def setup(self, every_time):
        def decorator(setup_func):
            def full_setup_func(student_file):
                path = os.path.dirname(student_file)
                file = os.path.join(path, '.gradepy')
                # Check if setup has already been run.
                if not every_time and os.path.exists(file):
                    return

                # Run the setup function from test script.
                setup_func(student_file)
                # Mark the directory as having been setup.
                with open(file, 'a+') as f:
                    f.write('DEBUG')

            self.setup_func = full_setup_func
        return decorator


    def register(self, tests=[], depends=[], manual=False):
        """Decorator to mark a function as a test function of this Tester.

        Optionally, specifies the student functions that the function
        with the function names as strings."""
        def decorator(test_func):
            self.test_funcs.append(test_func)
            setattr(test_func, 'tests', set(tests))
            setattr(test_func, 'depends', set(depends))
            setattr(test_func, 'manual', manual)
        return decorator

    def _get_modules(self, student_file):
        """Returns the student module and a copy for error carried forward."""
        path = os.path.dirname(student_file)
        mod_name = os.path.basename(student_file)[:-3]
        sys.path.append(path)
        try:
            mod_junk = imp.find_module(mod_name, [path])
        except ImportError as e:
            if not os.path.isfile(student_file):
                raise IOError("No such file: '{}'"
                              .format(student_file))
            else:
                raise e
        else:
            student_mod = imp.load_module('student_mod', *mod_junk)
            ecf_mod = imp.load_module('ecf_mod', *mod_junk)
            assert student_mod is not ecf_mod
            return student_mod, ecf_mod

    def _adjust_modules(self, *modules):
        for mod in modules:
            # Don't print the message for raw_input
            #mod.raw_input = lambda msg=None: raw_input()
            pass

    def _run_tests(self, test_funcs):
        """Runs all test methods of the instance as given by self.tests."""

        #methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for tm in test_funcs:
            self._run_test(tm)
        return self

    def _run_test(self, test, ecf=False):
        """Runs a single test method.

        Args:
            test (callable): a test method of self
        """
        if not ecf:  # only write header for the first try
            self.log('\n{:-^50}'.format('( ' + test.__name__ + ' )'))
            if test.__doc__:
                self.log('"""' + test.__doc__.strip() + '"""')

        if test.manual:
            self.log('')
            self._run_manual_test(test)
            return

        student_mod = self.ecf_mod if ecf else self.student_mod
        student_out = test(student_mod)
        master_out = test(self.master_mod)

        mistakes = self._compare(master_out, student_out)
        if any(mistakes):
            self._handle_ecf(test, ecf)
        else:
            self.log('All tests passed!')
        return mistakes

    def _run_manual_test(self, test):
        self.stdin.clear()
        try:
            test(self.master_mod, self.student_mod)
        except Exception as e:
            err = StudentException(e)
            self.log('\nFatal exception in manual testing function. '
                     'Cannot finish test.\n' + str(err))

    def _compare(self, master_out, student_out):
        # Compute all of master_out first so that stdin/stdout doesn't get mixed
        # between student and master.
        master_out = list(master_out)

        self.stdin.clear()  # don't let unused stdin bleed into this test func
        mistakes = []
        for master in master_out:
            try:
                student = next(student_out)
            except StopIteration:
                # Test function is done with student, but wasn't done with master.
                raise TestError('Test function yielded not enough Checks for student')

            except Exception as e:
                err = StudentException(e, skip=3)
                self.log('\nFatal exception in student code. '
                         'Cannot finish test.\n' + str(err))
                break
            else:  # no exception
                if isinstance(master.val, StudentException):
                    # The test function should never raise exceptions when using
                    # the master module. The test function must be broken.
                    raise TestError('Exception raised when running test function '
                                    'using master module:\n' + master.val.full_tb)
                mistakes.append(self._compare_one(master, student))

        # Test function is done with master, confirm that it is done with student.
        foo = next(student_out, None)
        if foo is not None:
            raise TestError('Test function yielded too many Checks for student.')

        return mistakes


    def _compare_one(self, master, student):
        if isinstance(student.val, StudentException):
            self.log(literal_format('\n{master.expr:q} should be {master.val}, '
                     'but student code raised an exception:\n'
                     '{student.val}{student.note:q}', **locals()))
            return True

        mistake = False

        if not master.check(student.val):
            self.log(literal_format('\n✘  {master.expr:q} should be {master.val}, '
                     'but it is {student.val}{student.note:q}', **locals()))
            mistake = True

        if not master.stdout_check(student.stdout):
            self.log(literal_format('\n✘  {master.expr:q} should print:\n{master.stdout:q}'
                     '\n\nbut it actually prints:\n{student.stdout:q}{student.note:q}', **locals()))
            mistake = True

        if self.log_correct and not mistake:
            if student.val:
                self.log(literal_format('\n✓  {master.expr:q} is {student.val}', **locals()))
            if student.stdout:
                self.log(literal_format('\n✓  {master.expr:q} prints:\n{student.stdout:q}', **locals()))

        return mistake




    def _handle_ecf(self, test, ecf):
        # See if this test benefits from ECF.
        if hasattr(test, 'depends') and not ecf:
            bad_helpers = [f for f in test.depends if f in self.bad_funcs]
            if bad_helpers:
                self.log('Trying again with helper functions corrected.')
                mistakes = self._run_test(test, ecf=True)
                if not any(mistakes):
                    self.log('Problem solved!')

        # Fix self.ecf_mod for later tested functions.
        if hasattr(test, 'tests'):
            self.bad_funcs |= test.tests
            for func_name in test.tests:
                # Update ecf module with master version of function
                master_func = getattr(self.master_mod, func_name)
                setattr(self.ecf_mod, func_name, master_func)



class StudentException(Exception):
    """Represents an exception that occurred in student code.

    This class should always be instantiated in an except block:
    """
    def __init__(self, exception, skip=1):
        self.exception = exception

        tb = traceback.format_exc()
        self.full_tb = tb
        self.tb = tb.split('\n', skip)[-1].rstrip()

    def __str__(self):
        return self.tb

class TestError(Exception):
    """Indicates that something is wrong with the test script."""


def literal_format(fmt_string, **kwargs):
    """Formats strings, keeping quotations in string values.

    >>> literal_format('string: {foo}', foo='bar')
    "string: 'bar'"

    Using the q spec will remove quotations, as in standard formatting.

    >>> literal_format('string: {foo:q}', foo='bar')
    "string: bar"
    """
    class Template(string.Formatter):
        def format_field(self, value, spec):
            if spec.endswith('q'):
                spec = spec[:-1] + 's'
            elif isinstance(value, str):
                value = value.encode('string-escape')
                value = "'" + value + "'"
            return super(Template, self).format_field(value, spec)

    result =  Template().format(fmt_string, **kwargs)

    return result


from collections import deque
class FakeStdin:
    def __init__(self):
        self._queue = deque()

    def put(self, line):
        self._queue.append(line)

    def readline(self):
        try:
            line = self._queue.popleft()
            if callable(line):
                # This allows something like (lambda: time.sleep(1) or 'foo').
                line = line()
            # We write the line to make it look like someone typed it.
            sys.stdout.write(line + '\n')
            return line
        except IndexError:
            raise IOError('No stdin available.')

    def clear(self):
        self._queue.clear()

