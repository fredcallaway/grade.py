from __future__ import print_function

from contextlib import contextmanager
import os
import imp
import re
import sys

def command_line(tester=None, grade_package=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Tests student python modules.')
    parser.add_argument('files', nargs='+', metavar='file',
                        help='paths to student modules')
    parser.add_argument('-csv', dest='csv', const=True, action='store_const',
                        help='create csv from feedback files')
    parser.add_argument('-test', metavar='regex', type=re.compile,
                        help='regex query to select test functions')
    parser.add_argument('-', dest='stdout', const=True, action='store_const', 
                        help='write to stdout')

    args = parser.parse_args()
    if args.csv:
        import makecsv
        makecsv.main(args.files)
    else:
        run_tests(args, tester, grade_package)


def run_tests(args, tester=None, grade_package=None):
    for file in args.files:
        tester = tester or get_tester(file, grade_package=grade_package)
        if tester:
            if args.stdout:
                tester(file, func_re=args.test)
            else:
                with logger(file) as log_func:
                    tester(file, log_func=log_func, func_re=args.test)
                    print('Wrote feedback to ' + log_func.file)


def get_tester(file, grade_package=None):
    mod_name = os.path.basename(file)[:-3]
    test_name = 'grade_' + mod_name

    try:
        test_mod = getattr(grade_package, test_name)
    except AttributeError:
        try:
            mod_junk = imp.find_module(test_name, '.')
        except ImportError:
            print('ERROR: No testing script found for {}'
                  .format(file), file=sys.stderr)
            return None
        test_mod = imp.load_module(test_name, *mod_junk)
    return test_mod.TESTER


@contextmanager
def logger(file):
    template = file[:-3] + '_feedback{}.txt'
    logfile = template.format('')

    # Ensure unique by appending an int.
    i = 0
    while os.path.exists(logfile):
        i += 1
        logfile = template.format(i)

    log = open(logfile, 'w+')
    def writer(msg):
        log.write(msg + '\n')

    writer.__dict__['file'] = logfile
    yield writer

    log.close()
