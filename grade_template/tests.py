"""Template test file"""
from gradepy import Tester, Check, ECF

# test functions ..

TESTS = []

def main(student_file):
    from master import BLANK as master_mod
    return Tester(master_mod, student_file).run_tests(*TESTS)
