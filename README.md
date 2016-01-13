# grade.py
A package for grading python assignments.

This module differs from standard testing strategies in two major ways. First, it relies on a correct implementation of the module, making the creation of test cases very easy. Second, it is designed to identify graded quality of performance, rather than giving binary PASS/FAIL judgements. It also provides Error Carried Forward functionality.

## Usage

As an end user, usage is very simple. Use the command line interface: `grade.py path/to/student/module.py`. It should behave like a typical Unix utility. For example, one could test all the python modules in a directory of student submissions with the command: `grade.py students/*/*.py`. 

## Writing test scripts

This package is unusual among testing packages in that it requires a correct implementation of the module being tested. Thus writing a test script comes in two phases: 

1. Correctly implement the assigned module specification.
2. Write a script that generates output using that module.

In lieu of extensive documentation, we provide a detailed example with commentary. See `example/`, which includes two "student submisions" along with an example grading package.

To create a new test, first copy the boilerplate from `test/grade_template/`. A package in the `tests/` directory that follows the naming convention `grade_MODULE/` will be used to grade any module with the name `MODULE`. Putting the module in this directory makes it visible to the `grade.py` command line tool. Alternatively one can place the package wherever one likes, and directly execute the package, e.g. `python2 grade_foo flc37/foo.py`. 
