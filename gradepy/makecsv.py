import csv
import re
from collections import defaultdict

class ParseError(Exception): pass
    
BAR_RE = re.compile(r'={50,}')
HEADER_RE = re.compile(r'Automated testing for [\w/]*?(\w+)/(\w+).py')
MAX_POINTS_RE = re.compile(r'Maximum points: (\d+)')
TEST_FUNC_RE = re.compile(r'-{3,}\( (\w+) \)-{3,}')
POINT_RE = re.compile(r'\(\([ ]*-([.\d]+)[ ]*\)\)')  # (( -2.5 ))


def main(files):
    """Creates a csv from a sequence of feedback files."""
    scores = parse_files(files)
    write_csv(scores)


def parse_files(files):
    for fname in files:
        with open(fname) as f:
            feedback = f.read()
            try:
                netid, module, points = parse_feedback(feedback)
                yield netid, module, points, feedback
            except ParseError:
                print("ERROR: could not parse file: '{}'".format(fname))


def write_csv(scores):
    all_scores = defaultdict(dict)
    all_feedback = defaultdict(list)
    all_modules = set()
    for netid, module, points, feedback in scores:
        all_scores[netid][module] = points
        all_feedback[netid].append(feedback)
        all_modules.add(module)

    with open('grades.csv', 'w+') as csvfile:
        fieldnames = ['netid'] + list(all_modules) + ['feedback']
        writer = csv.DictWriter(csvfile, fieldnames, escapechar='"')
        writer.writeheader()

        for netid, mod_scores in all_scores.items():
            row = mod_scores
            row['netid'] = netid
            feedback = '\n\n'.join(all_feedback[netid])
            row['feedback'] = '<pre>' + feedback + '</pre>'

            writer.writerow(row)


def parse_feedback(feedback):
    """Returns netid, module, and earned points based on a feedback string."""
    lines = iter(feedback.split('\n'))
    
    _scan(lines, BAR_RE)
    netid, module = HEADER_RE.match(next(lines)).groups()
    BAR_RE.match(next(lines))

    max_points = int(_scan(lines, MAX_POINTS_RE).group(1))
    deductions = POINT_RE.finditer(''.join(feedback))
    lost_points = sum(float(d.group(1)) for d in deductions)
    earned_points = max_points - lost_points

    return netid, module, earned_points

def _scan(lines, regex):
    for line in lines:
        match = regex.match(line)
        if match:
            return match
    raise ParseError('regex not found: ' + regex.pattern)


# We may use these down the line if we want to split points
# by function.
def _lost_points(lines):
    next_func = _scan(lines, TEST_FUNC_RE).group(1)
    while next_func:
        func = next_func
        points, next_func = _parse_test_func(lines)
        yield func, points

def _parse_test_func(lines):
    feedback, match = _take_until(lines, TEST_FUNC_RE)
    next_func = match and match.group(1)
    deductions = POINT_RE.finditer(''.join(feedback))
    lost_points = sum(float(d.group(1)) for d in deductions)
    return lost_points, next_func


def _take_until(lines, regex):
    taken = []
    for line in lines:
        match = regex.match(line)
        if match:
            return taken, match
        taken.append(line)
    return taken, None
    #raise ParseError('regex not found: ' + regex.pattern)


if __name__ == '__main__':
    main(['tests/example/submissions/flc37/foo_feedback.txt',
          'tests/example/submissions/flc38/foo_feedback.txt'])
