#!/usr/bin/env python2

import argparse
import os
import imp

from gradepy import TEST_DIRS

def main():
    #details = ('Each argument should be the')
    parser = argparse.ArgumentParser(description='Tests student python modules.')
    parser.add_argument('files', nargs='+', metavar='file',
                        help='paths to student modules.')



    args = parser.parse_args()
    for f in args.files:
        Test = get_test_class(f)
        Test(os.path.dirname(f)).run()


def get_test_class(file):
    mod_name = os.path.basename(file)[:-3]
    test_name = 'grade_' + mod_name
    mod_junk = imp.find_module(test_name, TEST_DIRS)
    test_mod = imp.load_module(test_name, *mod_junk)
    return test_mod.Test

if __name__ == '__main__':
    main()