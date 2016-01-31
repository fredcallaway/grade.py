
# grade.py
grade.py is a testing framework that aids in grading python assignments. grade.py gracefully handles exceptions and offers error carried forward support.

This package differs from standard testing frameworks in two major ways. First, it relies on a correct implementation of the module, making test scripts quick to write and enabling error carried forward. Second, it is designed to identify graded quality of performance, rather than giving binary PASS/FAIL judgements.

## Usage

As an end user (i.e. a grader), usage is simple:

    $ grade.py path/to/student/module.py

For example, one could test all the python modules in a directory of student submissions with the command: `grade.py students/*/*.py`. Of course, this will only work if testing scripts have been appropriately registered by the lead grader.

## Writing test scripts

Writing a test script comes in two phases: 

1. Correctly implement the assigned module specification.
2. Write a test suite with functions that generate output using the module.

### Example test function

```python
def test_foo(module):
    for i in range(10):
        yield Check('foo({i})', note='good effort')
```

This function might generate the following output:

```
foo(0) should be 0, but student code raised an exception:
  File "flc37/foo.py", line 15, in foo
    return 1.0 / x
ZeroDivisionError: integer division or modulo by zero
 Note: good effort

foo(5) should be 5, but it is 5.0
  Note: good effort
```


You can find a more complete example in `example/`, which includes two "student submisions" along with an example grading package and detailed commentary.

To create a new test, first copy the boilerplate from `test/grade_template/`. A package in the `tests/` directory that follows the naming convention `grade_MODULE/` will be used to grade any module with the name `MODULE`. Putting the module in this directory makes it visible to the grade.py command line tool.

## Distributing test scripts

We are still in the process of developing a generalized distribution strategy. At present, the best option is fork this repository and add scripts directly into the repository. Then update the name of the package and upload it to PyPI so that graders can easily download and update the package using e.g. `$ pip install cs1110grading`
