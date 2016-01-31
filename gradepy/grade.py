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
import traceback
import inspect
import imp
import os
import string
import sys



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
    def __init__(self, expr, note=''):
        # Yes, python allows us to access the local name space of the
        # calling function (or module). This prevents us from requiring
        # the user to supply locals() as an argument.
        self.env = inspect.stack()[1][0].f_locals
        self.expr = literal_format(expr, **self.env)
        if note:
            self.note = '\n Note: ' + literal_format(note, **self.env)
        else:
            self.note = ''

        # Evaluate expr within env
        try:
            module_env = self.env['module'].__dict__
            self.val = eval(self.expr, module_env, self.env)
        except Exception as e:
            self.val = StudentException(e, skip=4)



class Tester(object):
    """A class for grading modules.

    This class is an abstract base class which must be subclassed.
    See show_grade.py for example usage.
    """
    def __init__(self, master_mod, student_file):
        self.master_mod = master_mod
        self._bad_funcs = set()

        # Set up modules.
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
            self.student_mod = imp.load_module('student_mod', *mod_junk)
            self.ecf_mod = imp.load_module('ecf_mod', *mod_junk)
            assert self.ecf_mod is not self.student_mod

        self.log('\n\n' + '=' * 70)
        self.log('Automated testing for ' + student_file)
        self.log('=' * 70)

    def run_tests(self, *test_funcs):
        """Runs all test methods of the instance as given by self.tests."""

        #methods = inspect.getmembers(self, predicate=inspect.ismethod)
        for tm in test_funcs:
            self._run_test(tm)
        return self

    def log(self, msg):
        print(msg)

    def _run_test(self, test, ecf=False):
        """Runs a single test method.

        Args:
            test (callable): a test method of self
        """
        if not ecf:  # only write header for the first try
            self.log('\n{:-^30}'.format(' ' + test.__name__ + ' '))

        student_mod = self.ecf_mod if ecf else self.student_mod
        student_out = test(student_mod)
        master_out = test(self.master_mod)

        mistakes = self._compare(master_out, student_out)
        if any(mistakes):
            self._handle_ecf(test, ecf)

        return mistakes

    def _compare(self, master_out, student_out):
        mistakes = []
        # We could catch errors arising from student code being executed in test
        # methods here.
        while True:
            try:
                master = next(master_out)
            except StopIteration:
                foo = next(student_out, None)
                if foo is not None:
                    raise TestError('Test method yielded too many elements for student.')
                return mistakes

            try:
                student = next(student_out)
            except StopIteration:
                raise TestError('Test method yielded too few elements for student.')
            except ArithmeticError as e:
                err = StudentException(e, skip=3)
                self.log('\nFatal exception in student code. '
                         'Cannot finish test.\n' + str(err))
            else:
                if isinstance(master, Check):
                    if isinstance(master.val, StudentException):
                        # The test method should never raise exceptions when using
                        # the master method. The test method must be broken.
                        raise TestError('Exception raised when running test method '
                                        'using master module:\n' + str(master.val))
                    mistakes.append(self._check_new(master,student))
                else:
                    mistakes.append(self._check_simple(master, student))
        return mistakes

    def _check_new(self, master, student):
        if isinstance(student.val, StudentException):
            self.log(literal_format('\n{master.expr:q} should be {master.val}, but student code raised '
                     'an exception:\n{student.val}{student.note:q}', **locals()))
            return 'exception'
        elif master.val != student.val or type(master.val) != type(student.val):
            self.log(literal_format('\n{master.expr:q} should be {master.val}, but it is {student.val}'
                     '{student.note:q}', **locals()))
            #self.log('\n{master.expr} should be {master.val}, but it is {student.val}'
            #         '{student.note}'.format(**locals()))
            return 'incorrect'

    def _check_simple(self, master, student):
        master, name = master
        student, name2 = student
        assert name == name2

        if master != student or type(master) != type(student):
            self.log('\n{name} should be {master}, but it is {student}'
                     .format(**locals()))

    def _handle_ecf(self, test, ecf):
        # See if this test benefits from ECF.
        if hasattr(test, 'depends') and not ecf:
            bad_helpers = [f for f in test.depends if f in self._bad_funcs]
            if bad_helpers:
                self.log('Trying again with helper functions corrected.')
                mistakes = self._run_test(test, ecf=True)
                if not any(mistakes):
                    self.log('Problem solved!')

        # Fix self.ecf_mod for later tested functions.
        if hasattr(test, 'tests'):
            self._bad_funcs |= test.tests
            for func_name in test.tests:
                # Update ecf module with master version of function
                master_func = getattr(self.master_mod, func_name)
                setattr(self.ecf_mod, func_name, master_func)


class ECF(object):
    """A wrapper to record ECF-related metadata in the wrapped function."""
    def __init__(self, tests=[], depends=[]):
        self.tests = set(tests)
        self.depends = set(depends)
    
    def __call__(self, func):
        func.__dict__['tests'] = self.tests
        func.__dict__['depends'] = self.depends
        return func


class StudentException(Exception):
    """Represents an exception that occurred in student code.

    This class should always be instantiated in an except block:
    """
    def __init__(self, exception, skip=1):
        self.exception = exception
        
        tb = traceback.format_exc()
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
