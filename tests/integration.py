from __future__ import print_function
import sys
sys.path.append('..')
sys.path.append('../example')

def main():
    from grade_foo import TESTER
    TESTER('../example/flc37/foo.py')

if __name__ == '__main__':
    main()
