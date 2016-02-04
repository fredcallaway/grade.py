from grade_foo import TESTER
import os

def main():
    this_dir = os.path.dirname(__file__)
    submission = os.path.join(this_dir, 'submissions/flc37/foo.py')
    TESTER(submission)

if __name__ == '__main__':
    main()