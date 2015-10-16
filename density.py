import csv, re

class Sample():
    def __init__(self):
        self.project = None # a string ("CH, V, TRR, etc)
        self.number = None # like 144
        self.gs_range = None # a touple with low and high end
        self.density = None
        self.materials = {}

def csv_to_list(fname):
    f = open(fname, 'r')
    r = csv.DictReader(f)
    rows = []
    for row in r:
        rows.append(row)
    f.close
    return rows

def parse_name(name):
    exp = "([a-zA-Z]+)[-_ ]([0-9]+)(.*)"
    pattern = re.compile(exp)
    match = pattern.match(name)
    project = match.group(1)
    number = match.group(2)
    other = match.group(3)
    return (project, number, other)


def parse_additional_info(project, other):
    if project = 'CH':
        exp = "[-_]*([0-9]+)[-_ ]([0-9]+)"
        pattern = re.compile(exp)
        match = pattern.match(
