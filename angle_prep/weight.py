import csv, re

#this code is a mess, apologies

DENSITY_FILE = "densities.csv" # a csv file of the samples and the densities.
# the sample column should be named "Sample"
# and the density column should be named "Density"

COMPOSITION_FILE = "weighted_xrf_better_names.csv" # a csv file of the compositions from xrf data
# the sample column should be named "Name"

OUTPUT_FILE = "proper_comps_and_dens.csv" # a file to be created that has all the composition and density information

# this code also creates a file "unmatched.txt" that lists all the samples in the xrf data that were not matched to density information

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

def dicts_to_csv(dicts, out_file, keys):
    f = open(out_file, 'w')
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    for d in dicts:
        w.writerow(d)
    f.close()

# the field of the name in the new materials output
MAT_NAME_FIELD = "Sample Name"

# this function creates a "mat_dict", essentially a dictionary containing
#   the name of the sample (to make into the .mat file name)
#   the elemental percentages from the xrf
#   and the density of the sample
def make_mat_dict(density_row, xrf_row, density_name_field, density_field, xrf_name_field):
    elements = xrf_row.keys()
    elements.remove(xrf_name_field)
# creates a new dictionary containing the element key and values from the xrf data
    mat_dict = { el : xrf_row[el] for el in elements }
# copies over the new info from the density information
    mat_dict[MAT_NAME_FIELD] = density_row[density_name_field]
    mat_dict[density_field] = density_row[density_field]
    return mat_dict

def match_dens_row_with_xrf(dens_row, xrf_list, density_name_field, density_field, xrf_name_field):
    dens_name = dens_row[density_name_field]
    xrf_names = [xrf_row['Name'] for xrf_row in xrf_list]
    if dens_name in xrf_names:
        xrf_row = next(row for row in xrf_list if row['Name'] == dens_name)
        return make_mat_dict(dens_row, xrf_row, density_name_field, density_field, xrf_name_field)
    else:
        return None

def merge_all_dens_with_xrf(dens_list, xrf_list, density_name_field, density_field, xrf_name_field):
    merged = []
    for dens in dens_list:
        m = match_dens_row_with_xrf(dens, xrf_list, density_name_field, density_field, xrf_name_field)
        if m is not None:
            merged.append(m)
    return merged

def merge_dens_and_xrf_csv(dens_file, xrf_file, output_file, density_name_field="Sample", density_field="Density", xrf_name_field="Name"):
    dens_l = load_csv(dens_file)
    density_list = dens_l[0]
    xrf_l = load_csv(xrf_file)
    xrf_list = xrf_l[0]
    merged = merge_all_dens_with_xrf(density_list, xrf_list, density_name_field, density_field, xrf_name_field)
    keys = xrf_l[1]
    keys.remove(xrf_name_field)
    keys.insert(0, MAT_NAME_FIELD)
    keys.append(density_field)
    dicts_to_csv(merged, output_file, keys)
    generate_error_report(xrf_list, merged, xrf_name_field)

def generate_error_report(xrf_list, merged_list, xrf_name_field):
    xrf_names = [row[xrf_name_field] for row in xrf_list]
    merged_names = [row[MAT_NAME_FIELD] for row in merged_list]
    out = open("unmatched.txt", 'w')
    for name in xrf_names:
        if name not in merged_names:
            nline = "%s\n" % name
            out.write(nline)
    out.close()

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

def rename_weights(in_weight_file, out_weight_file):
    woo = load_csv(in_weight_file)
    weights = woo[0]
    weight_fields = woo[1]
    for weight in weights:
        weight['Name'] = xrf_name_to_name(weight['Name'])
    dicts_to_csv(weights, out_weight_file, weight_fields)

# mat file creation functions:
def mat_sci_str(num):
    base = "%.14E" % num
    return "%s00%s" % (base[:-2], base[-2:])

def create_element_output(el, ammount):
    if el == "Bal":
        el = "O"
    fel_string = mat_sci_str(float(ammount))
    outstring = "%s\r\n %s\r\n" % (el.upper(), fel_string)
    return outstring

def create_materials_file(sample):
    fname = "%s_XRF_ppm.mat" % sample['Sample Name']
    els = sample.keys()
    els.remove('Sample Name')
    els.remove('Density')
    materials = [(el, sample[el]) for el in els]
    dim = len(materials)
    mat_file = open(fname, 'w')
    dim_line = "%s\r\n" % dim
    mat_file.write(dim_line)
    for material in materials:
        mat_file.write(create_element_output(material[0], material[1]))
    dens_line = " %s\r\n" % mat_sci_str(float(sample['Density']))
    mat_file.write(dens_line)
    mat_file.close()

def create_materials_files(mat_csv):
    mats = load_csv(mat_csv)
    mats_rows = mats[0]
    for row in mats_rows:
        create_materials_file(row)

merge_dens_and_xrf_csv(DENSITY_FILE, COMPOSITION_FILE, OUTPUT_FILE)
create_materials_files(OUTPUT_FILE)

