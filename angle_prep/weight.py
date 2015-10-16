import csv, re

def make_sample_dict(row_list):
    samples = {}
    for row in row_list:
        name = row['SAMPLE']
        if name[-2] in ('.', '-', ' '):
            name = name[:-2]
        if name not in samples:
            samples[name] = []
        samples[name].append(row)
    return samples

def string_to_float(string):
    try:
        number = float(string)
    except ValueError:
        number = 0
    return number

def get_weight(row, element):
    error_key = "%s Error" % element
    error = string_to_float(row[error_key])
    if error == 0:
        print "error of %s is 0?" % row['SAMPLE']
        return 0
    else:
        return (1/(error ** 2))

def get_weighted_sum_term(row, element):
    weight = get_weight(row, element)
    count = string_to_float(row[element])
    numer = (count*weight)
    denom = weight
    return (numer, denom)

def get_weighted_average(runs, element):
    numer = 0.0
    denom = 0.0
    for run in runs:
        term = get_weighted_sum_term(run, element)
        numer += term[0]
        denom += term[1]
    return numer/denom

def weighted_average(sample, samples, elements, modif=1):
    avgs = {}
    avgs['Name'] = sample
    runs = samples[sample]
    for element in elements:
        avgs[element] = get_weighted_average(runs, element)/modif
    return avgs

def percent_from_runs(runs, els):
    samples = make_sample_dict(runs)
    avgs = []
    for key in samples.keys():
        avgs.append(weighted_average(key, samples, els, modif=10000))
    return avgs

def load_csv(file_name):
    f = open(file_name, 'r')
    r = csv.DictReader(f)
    fields = r.fieldnames
    rows = []
    for row in r:
        rows.append(row)
    f.close()
    return(rows, fields)

# this function creates a "mat_dict", essentially a dictionary containing
#   the name of the sample (to make into the .mat file name)
#   the elemental percentages from the xrf
#   and the density of the sample
def make_mat_dict(density_row, xrf_row, density_name_field, density_field, xrf_name_field):
    elements = xrf_row.keys()
    elements.remove(xrf_name_field)
# creates a new dictionary containing the element key and values from the xrf data
    mat_dict = { el : xrf_rows[el] for el in elements }
# copies over the new info from the density information
    mat_dict[MAT_NAME_FIELD] = density_row[density_name_field]
    mat_dict[density_field] = density_row[density_field]
    return mat_dict

def fix_id(id_str):
    if not id_str[-1].isdigit():
        pattern = re.compile("([0-9]+)([a-zA-Z]+)")
        match = pattern.match(id_str)
        num_comp = int(match.group(1))
        alph_comp = match.group(2)
        return "%03d%s" % (num_comp, alph_comp)
    else:
        return "%03d" % float(id_str)

def parse_range(range_string):
    pattern = re.compile("([0-9]+)-([0-9]+)")
    match = pattern.match(range_string)
    return "%s-%s" % (match.group(1), match.group(2))

def parse_other(other):
    if other[0] in (' ', '.'):
        return "%scm" % parse_range(other[1:])
    elif other[0] == '-':
        return parse_range(other[1:])
    else:
        return other


def xrf_name_to_name(xname):
    if xname[0] == 'r' or xname[0].isdigit():
        return xname
    else:
        exp = "([a-zA-Z]+)[- ]?([0-9]+[a-zA-Z]*)(.*)"
        pattern = re.compile(exp)
        match = pattern.match(xname)
        project = match.group(1).upper()
        sampleid = fix_id(match.group(2))
        other = match.group(3)
        if other:
            end_str = parse_other(other)
            return "%s-%s_%s" % (project, sampleid, end_str)
        else:
            return "%s-%s" % (project, sampleid)

def dicts_to_csv(dicts, out_file, keys):
    f = open(out_file, 'w')
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for d in dicts:
        w.writerow(d)
    f.close()

def rename_weights(in_weight_file, out_weight_file):
    woo = load_csv(in_weight_file)
    weights = woo[0]
    weight_fields = woo[1]
    for weight in weights:
        weight['Name'] = xrf_name_to_name(weight['Name'])
    dicts_to_csv(weights, out_weight_file, weight_fields)
