import restapi
import typer

app = typer.Typer()

DATA_SOURCE = 'https://gis.mcassessor.maricopa.gov/arcgis/rest/services/MaricopaDynamicQueryService/MapServer/3'
ATTRIBUTE_FILTER = "OWNER_NAME = 'CV HARQUAHALA LLC'"
QUERY_FILENAME = 'parcels.geojson'

DIRECTORY = 'data/'


@app.command()
def query_arcgis_restapi():
  '''
  Query available arcgis restapi's with relevant filters
  '''
  # data_source for specific Map Server
  layer = restapi.MapServiceLayer(DATA_SOURCE)

  # first get the state's metadata by submitting an incorrect query
  # features = layer.query(where='OBJECTID=20',
  #                        outSR=4326,
  #                        f='geojson',
  #                        exceed_limit=True)

  # indent allows for pretty view
  # features.dump(directory + f'metadata.geojson', indent=2)

  # features = layer.query(outSR=4326, f='geojson', exceed_limit=True)
  features = layer.query(where=ATTRIBUTE_FILTER,
                         outSR=4326,
                         f='geojson',
                         exceed_limit=True)

  # count the number of features
  print(f'Found {len(features)} features with {ATTRIBUTE_FILTER}')

  # save geojson file, may save as json depending on the esri api version, needs 10.3 to saave as geojson
  # indent allows for pretty view
  features.dump(DIRECTORY + QUERY_FILENAME, indent=2)

  # OR, you can save it directly to a shapefile (does not require arcpy)
  # layer.export_layer('test.shp', where=attribute_filter)


if __name__ == "__main__":
  app()