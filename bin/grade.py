#!/usr/bin/env python

import argparse
import imp

parser = argparse.ArgumentParser(description='Grade python modules.')
parser.add_argument('test_file', help='testing script')
parser.add_argument('students', nargs='+', 
                    help='directories containing student submissions')


def get_tester(file):
    mod = file
    if file.endswith('.py'):
        mod = mod[:-3]
    try:
        mod_junk = imp.find_module(mod)
    except ImportError:
        mod = 'grade_' + mod
        try:
            mod_junk = imp.find_module(mod)
        except ValueError:
            print("Couldn't find module: {}".format(file) )
            exit(1)
    mod = imp.load_module(mod, *mod_junk)
    import IPython; IPython.embed()


args = parser.parse_args()
get_tester(args.test_file)
for s in args.students:
    pass
