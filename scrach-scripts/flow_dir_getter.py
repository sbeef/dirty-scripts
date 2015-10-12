import urllib, zipfile, arcpy, os

VERBOSE = True

LAT_RANGE = (15, 36)
LONG_RANGE = (90, 106)
LAT_INC = 5
LONG_INC = 5

LAT_QUAD = "n" # the quadrant of latitude "n" or "s"
LONG_QUAD = "e" # the quadrant of longitude "e" or "w"

TILE_DIR = "/cygwin64/home/geomorph/flow_dir/tiles"
REMOVE_TILES = False

OUTPATH = "/cygwin64/home/geomorph/flow_dir"
OUTNAME = "ch_flow_dir.tif"

URL_PREFIX = "http://earlywarning.usgs.gov/hydrodata/sa_dir_3s_zip_grid/AS/"

min_lat = LAT_RANGE[0]
max_lat = LAT_RANGE[1]

min_long = LONG_RANGE[0]
max_long = LONG_RANGE[1]

def lat_long_to_filename(lat, long):
        return "%s%02d%s%03d_dir_grid" % (LAT_QUAD, lat, LONG_QUAD, long)

#cur_lat = min_lat
#cur_long = min_long

def download_file(base_url, file_name):
    url = "%s%s" % (URL_PREFIX, file_name)
    #remote_file = urllib.URLopener()
    download_path = os.path.join(os.path.abspath(TILE_DIR), file_name)
    if VERBOSE:
        print "downloading %s to %s" % (url, download_path)
    urllib.urlretrieve(url, download_path)
    #remote_file.retrive(url, file_name)

def extract_tile(file_name):
    zfname = os.path.join(os.path.abspath(TILE_DIR), file_name)
    if VERBOSE:
        print "attempting to extract %s" % zfname
    zfile = zipfile.ZipFile(zfname)
    zfile.extractall(TILE_DIR)
    zfile.close()

def get_tiles():
    cur_lat = min_lat
    while cur_lat <= max_lat:
        cur_long = min_long
        while cur_long <= max_long:
            folder_name = lat_long_to_filename(cur_lat, cur_long)
            zip_fname = "%s.zip" % folder_name
            zip_path = "%s/%s" % (TILE_DIR, zip_fname)
            if not os.path.exists(zip_path):
                download_file(URL_PREFIX, zip_fname)
            elif VERBOSE:
                print "%s already exists, skipping download" % zip_fname
            folder_path = zip_path[:-9]
            if not os.path.isdir(folder_path):
                extract_tile(zip_fname)
            elif VERBOSE:
                print "%s already extracted to %s" % (zip_fname, folder_name)
            cur_long += LONG_INC
        cur_lat += LAT_INC

def generate_tile_file_list(tile_folder):
    tiles = []
    walk = os.walk(tile_folder)
    for step in walk:
        arcpy.env.workspace = step[0].replace("\\", "/")
        print "looking for rasters in %s" % arcpy.env.workspace
        for raster in arcpy.ListRasters():
            print "found %s" % raster
            tiles.append(os.path.join(arcpy.env.workspace, raster).replace("\\", "/"))
    return tiles


def mosaic_tiles(tile_folder):
    tile_list = generate_tile_file_list(tile_folder)
    arcpy.MosaicToNewRaster_management(tile_list, OUTPATH, OUTNAME, number_of_bands=1)


get_tiles()
mosaic_tiles(TILE_DIR)
