import re, csv

def xrf_name_from_name(name):
    if name[0] == 'C':
        pattern = re.compile("CH-([0-9]{3})\.(.*)")
        match = pattern.match(name)
        switcher = {'u' : 'a',
                    '6' : 'b',
                    '1' : 'c',
                    '2' : 'd',
                    '5' : 'e'}
        size = switcher[match.group(2)[0]]
        return "%s-%s" % (match.group(1), size)
    elif name[0] == 'V':
        pattern = re.compile("V([0-9]{3})\.(.*)")
        match = pattern.match(name)
        if match.group(2)[0] == 'u':
            size = "0-63"
        else:
            pattern = re.compile("([0-9]+)\.([0-9]+)")
            smatch = pattern.match(match.group(2))
            size = "%s-%s" % (smatch.group(1), smatch.group(2))
        return "v%s-%s" % (match.group(1), size)
    elif name[3] == 'R':
        pattern = re.compile("([0-9]{2})-RS\.(.*)")
        match = pattern.match(name)
        switcher = {'11' : "0-63",
                    '12' : '63-125',
                    '13' : '125-250',
                    '14' : '250-500',
                    '15' : '500-850'}
        size = switcher[match.group(1)]
        return "rs-%s" % size

def merge_dens_and_xrf(dens_row, xrf_list):
    match_name = xrf_name_from_name(dens_row['Sample'])
    xrf_names = [xrf_row['Name'] for xrf_row in xrf_list]
    if match_name in xrf_names:
        xrf_row = next(row for row in xrf_list if row['Name'] == match_name)
        els = xrf_row.keys()
        els.remove('Name')
        merged = { el : xrf_row[el] for el in els }
        merged['Name'] = dens_row['Sample']
        merged['Density'] = dens_row['Density']
        return merged
    else:
        print "could not find match for %s with %s" % (dens_row['Sample'], match_name)
        return None

def merge_all_dens_with_xrf(dens_list, xrf_list):
    merged = []
    for dens in dens_list:
        m = merge_dens_and_xrf(dens, xrf_list)
        if m is not None:
            merged.append(m)
    return merged


def load_csv_as_dicts(file_name):
    f = open(file_name, 'r')
    r = csv.DictReader(f)
    rows = []
    for row in r:
        rows.append(row)
    f.close()
    return rows

def merge(dens_file, xrf_file):
    dens_list = load_csv_as_dicts(dens_file)
    xrf_list = load_csv_as_dicts(xrf_file)
    return merge_all_dens_with_xrf(dens_list, xrf_list)

def sci(num, exp):
    if num < 1:
            return sci((num*10.0), (exp - 1))
    elif not num < 10:
            return sci((num/10,0), (exp + 1))
    else:
        return (num, exp)

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
    if sample['Name'][0] == "V":
        fname = "%s-%s_XRF_ppm.mat" % (sample['Name'][:1], sample['Name'][1:])
    else:
        fname = "%s_XRF_ppm.mat" % sample['Name']
    els = sample.keys()
    els.remove('Name')
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


