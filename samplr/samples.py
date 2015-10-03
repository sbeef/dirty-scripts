import json

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
        self.elevation_file = None # the address of the elevation file that the samples pull from
        self.flowdir_file = None # Address of the flow direction file for the samples
        self.accumulation_file = None # Address of the flow accumulation file that the samples pull from
        self.tags = [] # various tags and notes about the collection
        self.sample_list = [] # a list of samples

    def add(self, sample):
        self.sample_list.append(sample)


class SampleEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Coordinate):
            return {'latitude'  : o.latitude,
                    'longitude' : o.longitude}
        elif isinstance(o, StatsNugget):
            return {'mimimum' : o.minimum,
                    'maximum' : o.maximum,
                    'mean'    : o.mean}

        elif isinstance(o, Sample):
            return {'name'         : o.name,
                    'location'     : json.dumps(o.elevation, cls=SampleEncoder, indent=4),
                    'area'         : o.area,
                    'basin'        : o.basin,
                    'files'        : {'watershed'   : o.watershed,
                                      'angle file'  : o.angle_file,
                                      'harbin file' : o.harbin_file},
                    'isotope data' : {'137Cs' : o.cs,
                                      '210Pb' : o.pb},
                    'statistics'   : {'elevation' : json.dumps(o.elevation, cls=SampleEncoder, indent=4),
                                      'slope'     : json.dumps(o.slope, cls=SampleEncoder, indent=4),
                                      'rain'      : json.dumps(o.rain, cls=SampleEncoder, indent=4),
                                      'relief'    : json.dumps(o.relief, cls=SampleEncoder, indent=4),
                                      'land use'  : {'% cultivated' : o.cultivated,
                                                     '% artifical'  : o.artificial}},
                    'flow snapped'          : o.flow_snapped,
                    'counted'               : o.counted,
                    'efficiency calculated' : o.efficiency_calculated,
                    'tags'                  : o.tags}
        elif isinstance(o, SampleCollection):
            return {'name' : o.name,
                    'files' : {'DEM' : o.elevation_file,
                               'flow direction' : o.flowdir_file,
                               'flow accumulation' : o.accumulation_file},
                    'tags' : o.tags,
                    'samples' : map(lambda i: json.dumps(i, cls=SampleEncoder, indent=4), o.sample_list)}
        else:
             return super(CustomEncoder, self).default(0)

