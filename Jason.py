import osm2geojson
import json
import os
import requests
import json
import geopandas as gpd
import msvcrt
from time import sleep
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
from simplification.cutil import simplify_coords

# Initialize chosen_file as none
chosen_file = "None"

def json_to_geojson(input_file, output_file):
    with open(input_file, 'r') as f:
        osm_data = json.load(f)

    geojson_data = osm2geojson.json2geojson(osm_data)

    with open(output_file, 'w') as f:
        json.dump(geojson_data, f, indent=4)

def display_files():
    files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    json_files = [file for file in files if file.endswith(".json") or file.endswith(".geojson")]

    print("Available json/geojson files: ")
    for file in json_files:
        print(file)

def run_overpass_query(query, overpass_file):
    overpass_url = "http://overpass-api.de/api/interpreter"
    response = requests.post(overpass_url, data={'data': query})
    
    if response.status_code == 200:
        data = response.json()
        
        with open(overpass_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Query results saved to {overpass_file}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def simplify_geojson(input_file, output_file, tolerance):
    gdf = gpd.read_file(input_file)

    def simplify_geometry(geom, tolerance):
        if geom.is_empty:
            return geom
        elif geom.geom_type == 'LineString':
            simplified = simplify_coords(geom.coords, tolerance)
            return LineString(simplified)
        elif geom.geom_type == 'Polygon':
            exterior = simplify_coords(geom.exterior.coords, tolerance)
            interiors = [simplify_coords(ring.coords, tolerance) for ring in geom.interiors]
            if len(exterior) >= 4:
                return Polygon(exterior, [interior for interior in interiors if len(interior) >= 4])
            else:
                return geom
        elif geom.geom_type == 'MultiLineString':
            simplified_lines = [LineString(simplify_coords(line.coords, tolerance)) for line in geom]
            return MultiLineString(simplified_lines)
        elif geom.geom_type == 'MultiPolygon':
            simplified_polygons = []
            for poly in geom.geoms:
                exterior = simplify_coords(poly.exterior.coords, tolerance)
                interiors = [simplify_coords(ring.coords, tolerance) for ring in poly.interiors]
                if len(exterior) >= 4:
                    simplified_polygons.append(Polygon(exterior, [interior for interior in interiors if len(interior) >= 4]))
            return MultiPolygon(simplified_polygons)
        else:
            return geom

    gdf['geometry'] = gdf['geometry'].apply(lambda geom: simplify_geometry(geom, tolerance))

    simplified_geojson = json.loads(gdf.to_json())

    with open(output_file, 'w') as f:
        json.dump(simplified_geojson, f, indent=2)


def display_menu():
    # make this fella global, it makes everything easier
    global chosen_file

    print("==== MENU ====")
    print(f"Current chosen file is: {chosen_file}")
    print("1. Choose a file")
    print("2. Run an Overpass query (make a json file)")
    print("3. Convert JSON --> GeoJSON")
    print("4. Simplify GeoJSON")
    print("5. Exit")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        display_files()
        chosen_file = input("Enter the name of the file: ")
        
        if chosen_file not in os.listdir(os.path.dirname(os.path.abspath(__file__))):
            print("File not found")
            chosen_file = None
            print("Press any key to continue...")
            key = msvcrt.getch()    
    elif choice == 2:
        query = input("Paste your Overpass query: ")
        filename = str(input("Enter the name of the file: "))
        run_overpass_query(query, filename + ".json")
    elif choice == 3:
        json_to_geojson(chosen_file, chosen_file.replace(".json", ".geojson"))
        print("Everything done !")
        sleep(3)
    elif choice == 4:
        tolerance = float(input("Enter desired tolerance: "))
        simplify_geojson(chosen_file, chosen_file.replace(".geojson", "_simplified.geojson"), tolerance)
        print("Everything done !")
        sleep(3)
    elif choice == 5:
        exit()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    while True:
        display_menu()
