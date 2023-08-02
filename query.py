import os

import restapi
import typer
import geopandas as gpd
import pandas as pd

os.environ['RESTAPI_USE_ARCPY'] = 'FALSE'

app = typer.Typer()

# data querying details
DATA_SOURCE = 'https://gis.mcassessor.maricopa.gov/arcgis/rest/services/MaricopaDynamicQueryService/MapServer/3'

# owner name to sql map
OWNER_NAME_TO_SQL_QUERY_MAP = {
    'harquahala': "OWNER_NAME = 'CV HARQUAHALA LLC'",
    'courthouse-ag': "OWNER_NAME = 'COURTHOUSE AG HOLDINGS LLC'",
    'verma': "OWNER_NAME LIKE '% VERMA%' or OWNER_NAME LIKE 'VERMA%'",
    'vidler': "OWNER_NAME LIKE '%VIDLER%'",
    'wpi': "OWNER_NAME LIKE '%WPI%'",
}
# ATTRIBUTE_FILTER = "OWNER_NAME = 'CV HARQUAHALA LLC'"
# ATTRIBUTE_FILTER = "OWNER_NAME = 'COURTHOUSE AG HOLDINGS LLC'"
# ATTRIBUTE_FILTER = "OWNER_NAME LIKE '% VERMA%' or OWNER_NAME LIKE 'VERMA%'"
# ATTRIBUTE_FILTER = "OWNER_NAME LIKE '%VIDLER%'"
# ATTRIBUTE_FILTER = "OWNER_NAME LIKE '%WPI%'"

# where to save data
DIRECTORY = 'data/'
MERGED_FILENAME = 'all-parcels'
QUERY_FILE_EXTENSION = '.json'
GEOJSON_FILE_EXTENSION = '.geojson'
CSV_FILE_EXTENSION = '.csv'

# unit conversions
ACRES_TO_SQUARE_METERS = 4046.8564224

# map projection
ALBERS_EQUAL_AREA = 'EPSG:5070'

# columns names
GIS_ACRES = 'gis_acres'


@app.command()
def query_rest_server(owner_name: str, attribute_filter: str):
  '''
  Query available arcgis restapi's with relevant filters
  '''
  # data_source for specific Map Server
  layer = restapi.MapServiceLayer(DATA_SOURCE)
  features = layer.query(where=attribute_filter,
                         outSR=4326,
                         f='json',
                         exceed_limit=True)

  # count the number of features
  print(f'Found {len(features)} features with {attribute_filter}')

  # save geojson file, may save as json depending on the esri api version, needs 10.3 to save as geojson
  # indent allows for pretty view
  features.dump(DIRECTORY + owner_name + QUERY_FILE_EXTENSION, indent=2)

  # OR, you can save it directly to a shapefile (does not require arcpy)
  # layer.export_layer('test.shp', where=attribute_filter)


@app.command()
def format_and_save(owner_name: str):
  '''
  Format json file, clean data, and save as geojson and csv
  '''
  gdf = gpd.read_file(DIRECTORY + owner_name + QUERY_FILE_EXTENSION)

  # compute gis calculated areas, rounded to 2 decimals
  gdf[GIS_ACRES] = (gdf.to_crs(ALBERS_EQUAL_AREA).area /
                    ACRES_TO_SQUARE_METERS).round(2)

  # save files
  gdf.to_file(DIRECTORY + owner_name + GEOJSON_FILE_EXTENSION, driver='GeoJSON')
  gdf.to_csv(DIRECTORY + owner_name + CSV_FILE_EXTENSION)

  return gdf


@app.command()
def single_query_and_save(owner_name: str, attribute_filter: str):
  query_rest_server(owner_name, attribute_filter)
  gdf = format_and_save(owner_name)
  return gdf


@app.command()
def query_and_save_all():

  #get list of gdfs for each owner
  gdfs = []
  for owner_name, attribute_filter in OWNER_NAME_TO_SQL_QUERY_MAP.items():
    gdfs.append(single_query_and_save(owner_name, attribute_filter))

  # merge and save as single file
  gdf = pd.concat(gdfs, ignore_index=True)
  gdf.to_file(DIRECTORY + MERGED_FILENAME + GEOJSON_FILE_EXTENSION,
              driver='GeoJSON')
  gdf.to_csv(DIRECTORY + MERGED_FILENAME + CSV_FILE_EXTENSION)

  return gdf


if __name__ == "__main__":
  app()