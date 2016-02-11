import sys
from contextlib import contextmanager
from cStringIO import StringIO

def wrap_script_with_main(student_file):
    """Wraps a script with a main() function."""
    with open(student_file, 'r') as f:
        indented = ['    ' + line for line in f]
    with open(student_file, 'w+') as f:
        if indented[0].startswith('    #'):
            del indented[0]  # keep line numbers the same
        else:
            print indented[0]
            print ("WARNING: No comment on first line. We couldn't fix the line numbers\n"
                   "which will all be one higher due to the def main(): line.")
        f.write('def main():\n')
        f.write(''.join(indented))
        f.write("if __name__ == '__main__':\n    main()")


@contextmanager
def capture_stdout():
    oldout = sys.stdout
    newout = StringIO()
    sys.stdout = newout

    class Out:
        @property
        def captured(self):
            try:
                val = newout.getvalue()
                self._captured = val
                return self._captured
            except ValueError:
                # After closing context manager.
                return self._captured

    result = Out()
    yield result

    result.captured  # set result._captured before closing newout
    newout.close()
    sys.stdout = oldout
