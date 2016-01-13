BASE_DIR = __file__.rsplit('/', 1)[0]
TEST_DIRS = ['.',
             BASE_DIR + '/example',
             BASE_DIR + '/cs1110']

def get_test_func(file):
    import os
    import imp
    mod_name = os.path.basename(file)[:-3]
    test_name = 'grade_' + mod_name
    try:
        mod_junk = imp.find_module(test_name, TEST_DIRS)
    except ImportError as e:
        print '\nERROR: No testing script found for {}\n'.format(file)
        import IPython; IPython.embed()
        return None
    test_mod = imp.load_module(test_name, *mod_junk)
    return test_mod.main

def command_line(test_func=None):
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Tests student python modules.')
    parser.add_argument('files', nargs='+', metavar='file',
                        help='paths to student modules.')

    args = parser.parse_args()
    for file in args.files:
        test = test_func or get_test_func(file)
        if test:
            test(file)
