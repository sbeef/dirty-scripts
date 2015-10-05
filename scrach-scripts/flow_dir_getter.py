import urllib, zipfilem, arcpy

LAT_RANGE = ()
LONG RANGE = ()
LAT_INC = 5
LONG_INC = 5

LAT_QUAD = "n" # the quadrant of latitude "n" or "s"
LONG_QUAD = "e" # the quadrant of longitude "e" or "w"

TILE_DIR = ""
KEEP_TILES = False

URL_PREFIX = "http://earlywarning.usgs.gov/hydrodata/sa_dir_3s_zip_grid/AS/"

min_lat = LAT_RANGE[0]
max_lat = LAT_RANGE[1]

min_long = LONG_RANGE[0]
max_long = LONG_RANGE[1]

def lat_long_to_filename(lat, long):
        return "%s%02d%s%02d_dir_grid" % (LAT_QUAD, lat, LONG_QUAD, long)

cur_lat = min_lat
cur_long = min_long

def download_file(base_url, file_name):
    url = "%s%s" % (URL_PREFIX, file_name)
    remote_file = urllib.URLopener()
    download_path = (TILE_DIR, filename)
    remote_file.retrive(url, file_name)

def extract_tile(file_name):
    zfile = zipfile.ZipFile(file_name)
    zfile.extractall(TILE_DIR)
    zfile.close()

def get_tiles():
    while cur_lat <= max_lat:
        while cur_long <= min_long:
            folder_name = lat_long_to_filename(cur_lat, cur_long)
            zip_fname = "%.zip" % folder_name
            if not os.path.exists(fname):
                download_file(URL_PREFIX, fname)
            elif verbose:
                print "%s already exists, skipping download" % fname
            if not os.path.isdir(folder_name):
                extract_tile(fname)
            elif verbose:
                print "%s already extracted to %s" % (zip_fname, folder_name)
        cur_long += LONG_INC
    cur_lat += LAT_INC

def generate_tile_file_list(tile_folder):


def mosaic_tiles(tile_folder)

