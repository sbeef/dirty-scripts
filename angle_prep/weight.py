import csv

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
