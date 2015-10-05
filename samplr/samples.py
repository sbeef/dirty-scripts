import time, yaml, os

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
        self.location = Coordinate() #a coordinate object
        self.area = None # the upstream area of the sample
        self.basin = None # the name of the river basin
        #files
        self.watershed = None # a string representing the adress of the shapefile of the watershed
        self.angle_file = None # a string representing the adress of the output file from angle
        self.harbin_file = None # a string represninting the address of the output file from harbin
        #isotope data
        self.cs = None # a float representing the amount of Cs in Bq/kg
        self.pb = None # a float representing the amount of Pb in Bq/kg
        #spatial satistics
        # each statistic is a StatsNugget Object
        self.elevation = StatsNugget()
        self.slope = StatsNugget()
        self.rain = StatsNugget()
        self.relief = StatsNugget()
        # land use - each is a float representing the percentage of each type
        self.cultivated = None
        self.artificial = None
        #administrative stuff
        self.flow_snapped = None #snapped to a point in the flow accumulation
        self.counted = None # ran through harbin
        self.efficiency_calculated = None # run through angle
        self.tags = [] # various tags and notes about the sample

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
        return self.sample_list

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
            self.file_name = "_".join([c for c in filename if c.isalpha() or c.isdigit()]).rstrip()
        outfile = "%s.data" % self.file_name
        outpath = os.path.join(self.containing_folder, outpath)
        output = open(outpath, 'w')
        yaml.dump(self, output)
        output.close()
        self.setup_archive()
        archive_file = "%s_%s.data" % (self.file_name, time.strftime("%y.%m.%d-%H.%M.%S"))
        archive_path = os.path.join(self.archive_file, archive_file)
        archive = open(archive_path, 'w')
        yaml.dump(self, archive)
        archive.close()

def load(file_name):
    input_file = open(file_name, 'r')
    sample_list = yaml.load(input_file)
    input_file.close()
    sample_list.containing_folder = os.path.split(file_name)[0]
    return sample_list

# takes in a sample collection and a directory to search and finds all the .eft files and copies them over
def link_angle_files(collection, root_dir, copy=True):
    collection.setup_angle_folder()
    walk = os.walk(root_dir)
    for step in walk:
        for file in step[2]:
            fname = os.splitext(file)[0]
            ext = os.splitext(file)[1]
            if ext = ".eft":
                    sample_match = next((x for x in collection.sample_list if x.name == fname), None)
                    if sample_match not None:
                        angle_file == os.path.join(step[0], file)
                        if copy = True:
                            angle_backup = os.path.join(collection.angle_folder, file)
                            shutil.copyfile(angle_file, angle_backup)
                            angle_file = angle_backup
                        sample_match.angle_file == angle_file
                        sample_match.efficiency_calculated == True

