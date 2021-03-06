import time, yaml, os, sys, csv

try:
    import arcpy
except ImportError:
    print "no arcpy module, so certain functions will not work"
try:
    from scipy import stats
except ImportError:
    print "no scipy module so certain functions will not work"


PLOT_STRING = (
"\\documentclass{standalone}\n\n" +
"\\usepackage{amsmath}\n" +
"\\usepackage{pgfplots}\n" +
"\\pgfplotsset{compat=%(version)s}\n\n" +
"\\begin{document}\n\n" +
"\\pgfplotstableread[col sep=%(seperator)s] {%(data_file)s}\data\n\n" +
"\\begin{tikzpicture}\n" +
"\\begin{%(axis)s}[\n" +
"    name=s,\n" +
"    title=%(title)s,\n" +
"    axis lines=left,\n" +
"    xlabel=%(xlabel)s,\n" +
"    ylabel=%(ylabel)s,\n" +
"    ]\n" +
"\\addplot+[\n" +
"    only marks,\n" +
"    mark options={\n" +
"        color=black,\n" +
"        },\n" +
"    mark size=1pt,\n" +
"    ] table[\n" +
"        x=%(xfield)s,\n" +
"        y=%(yfield)s,\n" +
"    ] {\\data};\n" +
"\\end{axis}\n" +
"%(rfilter)s\\draw (s.right of north east) node[above right] {$r^2=%(rr).3f$};\n" +
"%(pfilter)s\\draw (s.right of north east) node[below right] {$p$-value$=%(pvalue).3f$};\n" +
"\\end{tikzpicture}\n\n" +
"\\end{document}\n" )




class Coordinate:
    def __init__(self):
        self.latitude = None
        self.longitude = None

class StatsNugget:
    def __init__(self):
        self.minimum = None # a float representing the minimum of the parameter
        self.maximum = None
        self.mean = None

class Sample:
    def __init__(self, name):
        self.name = name # a string
        self.latitude = None
        self.longitude = None
        self.isotopes = {}
        self.files = {}
        self.geography = {}
        self.administrative = {} # for stuff like resample, in/over, station number
        self.spatial_reference = None
        #administrative stuff
        self.flow_snapped = None #snapped to a point in the flow accumulation
        self.sheded = None
        self.counted = None # ran through harbin
        self.efficiency_calculated = None # run through angle
        self.tags = [] # various tags and notes about the sample
    def load_prj_file(prj_file):
        self.spatial_reference = arcpy.SpatialReference(prj_file)

    def create_watershed(self, flow_dir, shp_dir):
        if not self.flow_snapped:
            print "this point has not yet been snapped to flow direction"
            return None
        point_info = arcpy.Point(self.longitude, self.latitude)
        point = arcpy.PointGeometry(point_info, self.spatial_reference)
        arcpy.CheckOutExtension("Spatial")
        watershed_raster = arcpy.sa.Watershed(flow_dir, point)
        shp_name = self.name.replace(" ", "_")
        shp_path = os.path.join(shp_dir, shp_name)
        arcpy.RasterToPolygon_conversion(watershed_raster, shp_path)
        self.files['watershed'] = shp_path
        self.sheded = True
        return shp_path

    def get_area(self):
        meter_file = "%s_UTM.shp" % self.watershed[:-4]
        sc = arcpy.da.SearchCursor(meter_file, "SHAPE@AREA")
        self.geography['area'] = sc.next()[0]

    def get_statistics(self, raster_file, output=None):
        if not self.sheded:
            print "Cannot get statistics, no watershed exists"
            return None
        # load raster as a raster object
        raster = arcpy.Raster(raster_file)
        if output is None:
            outpath = "in_memory/clipped"
        else:
            outpath = output
        # clip raster to watershed
        print ("attempting arcpy.Clip_management(%s, out_raster=%s, ",
               "in_template_dataset=%s, clipping_geometry=\"ClippingGeometry\")"
               % (raster, output, self.watershed))
        clipped = arcpy.Raster(
                    arcpy.Clip_management(raster, out_raster=outpath,
                                          in_template_dataset=self.watershed,
                                          clipping_geometry="ClippingGeometry"))
        # extract statistics
        stats = {}
        stats['maximum'] = clipped.maximum
        stats['minimum'] = clipped.minimum
        stats['mean'] = clipped.mean
        if output is None:
            arcpy.Delete_management(outpath)
        return stats

    def set_stats(self, stats, name):
        maxs = "max %s" % name
        mins = "min %s" % name
        means = "mean %s" % name
        self.geography[maxs] = stats["maximum"]
        self.geography[mins] = stats["minimum"]
        self.geography[means] = stats["mean"]

    def get_stats(self, attribute, raster):
        stats = self.get_statistics(raster)
        if stats is not None:
            self.set_stats(stats, attribute)



# gets valyues from obj like dict, but allows for values of objects that are values of objects
# SO get_value(sample, name) --> sample.name
# AND get_value(sample, ('relief', 'mean')) --> sample.relief.mean
def get_value(obj, field):
    if isinstance(field, basestring):
        return obj.__dict__[field]
    else:
        return get_value(obj.__dict__[field[0]], field[1])

class SampleCollection: # a collection of samples to be treated similarly
    def __init__(self):
        self.name = None # the name of the collection
        #files
        self.containing_folder = "" # the folder that contains the data file
        self.aux_folder = None # the folder that contains the auxiliary data (angle, shapefiles, etc)
        self.archive_folder = None # the folder for the old sample.data files
        self.angle_folder = None
        self.harbin_folder = None
        self.gis_folder = None
        self.file_name = None # the filename for the datafile
        self.elevation_file = None # the address of the elevation file that the samples pull from
        self.flowdir_file = None # Address of the flow direction file for the samples
        self.accumulation_file = None # Address of the flow accumulation file that the samples pull from
        self.tags = [] # various tags and notes about the collection
        self.sample_list = [] # a list of samples

    # this function just returns the sample list, so that you can iterate
    def __iter__(self):
        return iter(self.sample_list)

    # fields is a list of touples which are (name of output column, name of object field)
    #[('Name', 'name'), ('mean_relief', ('relief', 'mean')
    def create_csv(self, fields, output, ffunction=None):
        of = open(output, 'w')
        writer = csv.DictWriter(of, fieldnames = [field[0] for field in fields])
        writer.writeheader()
        out_samples = filter(ffunction, self.sample_list)
        for sample in out_samples:
            sdict = {}
            for field in fields:
                sdict[field[0]] = get_value(sample, field[1])
            writer.writerow(sdict)
        of.close()

    def add(self, sample):
        self.sample_list.append(sample)

    # this function sets an archive folder path if it is not already set
    # and creates an archive folder if it does not already exist
    def setup_archive(self):
        if self.archive_folder == None:
            self.archive_folder = os.path.join(self.containing_folder, ".archive")
        if not os.path.exists(self.archive_folder):
            os.makedirs(self.archive_folder)

    #this function works like setup_archive() but for the auxilary folder
    def setup_auxiliary(self):
        if self.aux_folder == None:
            self.aux_folder = os.path.join(self.containing_folder, ".auxiliary")
        if not os.path.exists(self.aux_folder):
            os.makedirs(self.aux_folder)

    def setup_angle_folder(self):
        self.setup_auxiliary()
        if self.angle_folder == None:
            self.angle_folder = os.path.join(self.aux_folder, "angle")
        if not os.path.exists(self.angle_folder):
            os.makedirs(self.angle_folder)

    def setup_harbin_folder(self):
        self.setup_auxiliary()
        if self.harbin_folder == None:
            self.harbin_folder = os.path.join(self.aux_folder, "harbin")
        if not os.path.exists(self.harbin_folder):
            os.makedirs(self.harbin_folder)

    def setup_gis_folder(self):
        self.setup_auxiliary()
        if self.gis_folder == None:
            self.gis_folder = os.path.join(self.aux_folder, "gis")
        if not os.path.exists(self.gis_folder):
            os.makedirs(self.gis_folder)

    def save(self):
        if self.file_name == None:
            self.file_name = self.name
            #self.file_name = self.name.replace(" ", "_")
        outfile = "%s.data" % self.file_name
        outpath = os.path.join(self.containing_folder, outfile)
        output = open(outpath, 'w')
        yaml.dump(self, output)
        output.close()
        self.setup_archive()
        archive_file = "%s_%s.data" % (self.file_name, time.strftime("%y.%m.%d-%H.%M.%S"))
        archive_path = os.path.join(self.archive_folder, archive_file)
        archive = open(archive_path, 'w')
        yaml.dump(self, archive)
        archive.close()

def load(file_name):
    if os.path.isdir(file_name):
        file_name = "%s/%s.data" % (file_name, file_name)
    input_file = open(file_name, 'r')
    sample_list = yaml.load(input_file)
    input_file.close()
    sample_list.containing_folder = os.path.split(file_name)[0]
    return sample_list

def sync_file(sample, path, fname, field, copy):
    source_file = os.path.join(path, fname)
    if copy:
        file_backup = os.path.join(field[1], fname)
        shutil.copyfile(source_file, file_backup)
        source_file = file_backup
    if field[0] == "angle":
        sample.angle_file == source_file
        sample.efficiency_calculated == True
    elif field[0] == "harbin":
        sample.harbin_file == source_file
        sample.counted == True
    #else throw error?

# takes in a sample collection and a directory to search and finds all the files of a certain extension and copies them over
def link_files(collection, root_dir, field, copy):
    collection.setup_angle_folder()
    walk = os.walk(root_dir)
    for step in walk:
        for file in step[2]:
            fname = os.splitext(file)[0]
            ext = os.splitext(file)[1]
            if ext == field[3]:
                    sample_match = next((x for x in collection.sample_list if x.name == fname), None)
                    if sample_match is not None:
                        sync_file(sample_match, step[0], file, field, copy)

def link_angle_files(collection, root_dir, copy=True):
    collection.setup_angle_folder()
    field = ("angle", collection.angle_folder, ".eft")
    link_files(collection, root_dir, field, copy)

def link_harbin_files(collection, root_dir, copy=True):
    collection.setup_harbin_folder()
    field = ("harbin", collection.harbin_folder, ".RPT")
    link_files(collection, root_dir, field, copy)


def sample_to_PointGeometry(sample):
    pt = arcpy.Point(sample.location.longitude, sample.location.latitude)
    return (arcpy.PointGeometry(pt), sample.name)


def create_pointfile_from_list(sample_list, outfile):
    arcpy.CreateFeatureclass_management(os.path.split(outfile)[0], os.path.split(outfile)[1], "POINT")
    arcpy.AddField_management(outfile, "name", "TEXT")
    cursor = arcpy.da.InsertCursor(outfile, ("SHAPE@", "name"))
    point_geoms = [sample_to_PointGeometry(sample) for sample in sample_list]
    for point in point_geoms:
        cursor.insertRow(point)

#temp_output needs to be the default geodatabase
# NOT GENERIC, SPECIFIC TO GLC!!
def get_class_area(raster, cids, clip, nodata=255, clean=True):
    temp_output = "/Users/geomorph/Documents/ArcGIS/Default.gdb/clipped"
    clipr = arcpy.Clip_management(raster, out_raster=temp_output, in_template_dataset=clip, nodata_value = nodata, clipping_geometry="ClippingGeometry")
    c = arcpy.Raster(clipr)
    #convert raster to array
    a = arcpy.RasterToNumPyArray(c)
    # get size of array
    sel = (a >= 1)
    tp = a[sel]
    sel = (tp <= 10)
    total = len(tp[sel])
    output = {}
    # sum number of elements equal to a certain value
    for value in cids:
        sel = (a == value)
        count = len(a[sel])
        perc = float(count)/float(total)
        output[value] = perc
    # return sum/size
    if clean:
        arcpy.Delete_management(temp_output)
    return output

def make_dat_file(columns, l1, l2, output):
        of = open(output, 'w')
        outl = "%s\t%s\n" % (columns[0], columns[1])
        of.write(outl)
        for i in range(0, len(l1)):
            outl = "%s\t%s\n" % (l1[i], l2[i])
            of.write(outl)
        of.close()



def plot_dat_file(x, y, data, out_tex, title="", sep="comma", axis="axis", rr=None, pvalue=None, version='1.12'):
    output_file = open(out_tex, 'w')
    inputs = {
        'title':title,
        'version':version,
        'seperator':sep,
        'data_file':data,
        'axis':axis,
        'xlabel':x[0],
        'ylabel':y[0],
        'xfield':x[1],
        'yfield':y[1],
        'rfilter':'%',
        'pfilter':'%',
        'rr':0.0,
        'pvalue':0.0,}
    if rr is not None:
        inputs['rfilter'] = ''
        inputs['rr'] = rr
    if pvalue is not None:
        inputs['pfilter'] = ''
        inputs['pvalue'] = pvalue
    output = PLOT_STRING % inputs
    output_file.write(output)
    output_file.close()

# x and y are touples containing the list of data to graph,
#   a string represnting the axis label of the graph
#   and another string representing a nice label for the tex file
def plot(x, y, out_name, title="", axis="axis", rr=True, pvalue=True):
    x_vals = x[0]
    y_vals = y[0]
    x_keys = x[1:]
    y_keys = y[1:]
    slope, intercept, r_value, p_value, std_rr = stats.linregress(x_vals, y_vals)
    if rr:
        rr = r_value**2
    else:
        rr = None
    if pvalue:
        pvalue = p_value
    else:
        pvalue = None
    dat_file = "%s.dat" % out_name
    tex_file = "%s.tex" % out_name
    make_dat_file((x_keys[1], y_keys[1]), x_vals, y_vals, dat_file)
    dat_name = os.path.split(dat_file)[1]
    plot_dat_file(x_keys, y_keys, dat_name, tex_file, title=title, sep='space', axis=axis, rr=rr, pvalue=pvalue)
