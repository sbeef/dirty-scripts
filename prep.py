import samples

LABELS = {
    'pb':'$^{210}$Pb$_{\\text{ex}}$ (Bq/kg)',
    'cs':'$^{137}$Cs (Bq/kg)',
    'cult':'Cultivated land (\% of upstream area)',
    'art':'Artifical land (\% of upstream area)',
    'rain':'Mean annual precipitation (mm/yr)',
    'relief':'Mean annual relief (meters)',
    'elevation':'Mean annual elevation (m)',
    'slope':'Mean slope ($\\circ$)',
    'area':'Total upstream area (km$^2$)'}

def fix(num):
    if num > 0:
        return num
    else:
        return 0.0

def gogographit(neg='nothing'):
    gsamps = samples.load('gsa_samples/GSA_Samples.data')
    good_samps = [sample for sample in gsamps if sample.pb is not None]
    if neg == 'remove':
        good_samps = [sample for sample in good_samps if sample.pb >= 0]
    if neg == 'zero':
        pb_vals = [fix(sample.pb) for sample in good_samps]
    else:
        pb_vals = [sample.pb for sample in good_samps]
    cs_vals = [sample.cs for sample in good_samps]
    cult_vals = [sample.cultivated for sample in good_samps]
    art_vals = [sample.artificial for sample in good_samps]
    rain_vals = [sample.rain.mean for sample in good_samps]
    relief_vals = [sample.relief.mean for sample in good_samps]
    elevation_vals = [sample.elevation.mean for sample in good_samps]
    slope_vals = [sample.slope.mean for sample in good_samps]
    area_vals = [sample.area/1000000 for sample in good_samps]
    pb = (pb_vals, LABELS['pb'], 'pb')
    cs = (cs_vals, LABELS['cs'], 'cs')
    cult = (cult_vals, LABELS['cult'], 'cult')
    art = (art_vals, LABELS['art'], 'art')
    rain = (rain_vals, LABELS['rain'], 'rain')
    relief = (relief_vals, LABELS['relief'], 'relief')
    elevation = (elevation_vals, LABELS['elevation'], 'elev')
    slope = (slope_vals, LABELS['slope'], 'slope')
    area = (area_vals, LABELS['area'], 'area')
    indvars = (cult, art, rain, relief, elevation, slope, area)
    plot_folder = 'gsa_samples/plots'
    if neg == 'zero':
        extra = "_zero"
    elif neg == 'remove':
        extra = "no-neg"
    else:
        extra = ""
    for var in indvars:
        print "plotting %s against %s" % (var[2], 'pb')
        fname = "%s/%s_pb%s" % (plot_folder, var[2], extra)
        samples.plot(var, pb, fname)

def plot(p1, p2, name):
    gsamps = samples.load('gsa_samples/GSA_Samples.data')
    good_samps = [sample for sample in gsamps if sample.pb is not None]
    pb_vals = [fix(sample.pb) for sample in good_samps]
    cs_vals = [sample.cs for sample in good_samps]
    cult_vals = [sample.cultivated for sample in good_samps]
    art_vals = [sample.artificial for sample in good_samps]
    rain_vals = [sample.rain.mean for sample in good_samps]
    relief_vals = [sample.relief.mean for sample in good_samps]
    elevation_vals = [sample.elevation.mean for sample in good_samps]
    slope_vals = [sample.slope.mean for sample in good_samps]
    area_vals = [sample.area/1000000 for sample in good_samps]
    pb = (pb_vals, LABELS['pb'], 'pb')
    cs = (cs_vals, LABELS['cs'], 'cs')
    cult = (cult_vals, LABELS['cult'], 'cult')
    art = (art_vals, LABELS['art'], 'art')
    rain = (rain_vals, LABELS['rain'], 'rain')
    relief = (relief_vals, LABELS['relief'], 'relief')
    elevation = (elevation_vals, LABELS['elevation'], 'elev')
    slope = (slope_vals, LABELS['slope'], 'slope')
    area = (area_vals, LABELS['area'], 'area')
    mapper = {
        'pb':pb,
        'cs':cs,
        'cult':cult,
        'cultivated':cult,
        'cultivation':cult,
        'art':art,
        'artificial':art,
        'rain':rain,
        'precip':rain,
        'precipitation':rain,
        'relief':relief,
        'elevation':elevation,
        'elev':elevation,
        'slope':slope,
        'area':area,
    }
    oname = "gsa_samples/plots/%s" % name
    samples.plot(mapper[p1], mapper[p2], oname)

