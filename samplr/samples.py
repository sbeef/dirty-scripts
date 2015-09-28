import samples, csv, yaml

shed_codes = []
with open('TRR_watersheds.txt') as shedfile:
    reader = csv.DictReader(shedfile)
    for row in reader:
        shed_codes.append(int(float(row['GRIDCODE_1'])))

sample_list = samples.SampleCollection()
sample_list.name = "Land Use"

with open('TRR_samples.txt') as samplefile:
    reader = csv.DictReader(samplefile)
    for row in reader:
        name = "TRR-%s"%(row['NAME'])
        g_lat = float(row['gis_lat'])
        g_long = float(row['gis_long'])
        basin = row['RiverBasin']
        code = int(float(row['grid_value']))
        sample = samples.Sample(name)
        sample.location = (g_lat, g_long)
        sample.basin = basin
        if code in shed_codes:
            sample.flow_snapped = True
        else:
            sample.flow_snapped = False
        sample_list.add(sample)


sample_list.save()
#output = open('samples.object', 'w')
#yaml.dump(sample_list, output)
#output.close
