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
        self.folder = "" # the folder that contains the data file
        self.file_name = None
        self.elevation_file = None # the address of the elevation file that the samples pull from
        self.flowdir_file = None # Address of the flow direction file for the samples
        self.accumulation_file = None # Address of the flow accumulation file that the samples pull from
        self.tags = [] # various tags and notes about the collection
        self.sample_list = [] # a list of samples

    def add(self, sample):
        self.sample_list.append(sample)

    def save(self):
        if self.file_name == None:
            self.file_name = "_".join([c for c in filename if c.isalpha() or c.isdigit()]).rstrip()
        outfile = "%s.data" % self.file_name
        outpath = os.path.join(self.folder, outpath)
        output = open(outpath, 'w')
        yaml.dump(self, output)
        output.close()
        archive_file = ".archive/%s_%s.data" % (self.file_name, time.strftime("%y.%m.%d-%H.%M.%S"))
        archive_path = os.path.join(self.folder, archive_file)
        archive = open(archive_path, 'w')
        yaml.dump(self, archive)
        archive.close()


def load(file_name):
    input_file = open(file_name, 'r')
    sample_list = yaml.load(input_file)
    input_file.close()
    sample_list.folder = os.path.split(file_name)[0]
    return sample_list
