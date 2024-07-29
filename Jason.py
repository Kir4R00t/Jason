from collections import defaultdict
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

# Initialize chosen_file & data as none
chosen_file = None
data = None

def json_to_geojson(input_file, output_file):
    with open(input_file, 'r') as f:
        osm_data = json.load(f)

    geojson_data = osm2geojson.json2geojson(osm_data)

    with open(output_file, 'w') as f:
        json.dump(geojson_data, f, indent=4)

# Displays files only located in the same dir as python file
def display_files():
    files = os.listdir(os.path.dirname(os.path.abspath(__file__)))
    json_files = [file for file in files if file.endswith(".json") or file.endswith(".geojson")]

    print("Available json/geojson files: ")
    for file in json_files:
        print(file)


# TODO: make a function to run an overpass query 
def run_overpass_query(query, overpass_file):
    pass

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

# TODO: Finish this
def count_tags(data):
    tag_counts = defaultdict(int)

    for element in data["elements"]:
        if "tags" in element:
            for tag in element["tags"]:
                tag_counts[tag] += 1

    
    tag_counts = count_tags(data)
    record_count = len(data["elements"])

    # Sortowanie malejąco & wyswietlenie
    sorted_tag_counts = sorted(tag_counts.items(), key=lambda item: item[1], reverse=True)
    print("")
    for tag, count in sorted_tag_counts:                      # Procentowa wartość dla lepszej wizualizacji
        print(f"Tag '{tag}' pojawił się w {count/record_count*100:.2f}% wszystkich rekordów.")

def display_menu():
    # make this fellas global, fuck the establishment
    global chosen_file
    global data

    print("==== MENU ====")
    print(f"Current chosen file is: {chosen_file}")
    print("1. Choose a file")
    print("2. Run an Overpass query (make a json file)")
    print("3. Convert JSON --> GeoJSON")
    print("4. Simplify GeoJSON")
    print("5. Tag counter in Json file")
    print("6. Exit")
    choice = int(input("Enter your choice: "))

    if choice == 1:
        display_files()
        chosen_file = input("Enter the name of the file: ")
        
        current_directory = os.path.dirname(os.path.abspath(__file__))
        chosen_file_path = os.path.join(current_directory, chosen_file)
        
        with open(chosen_file_path, "r") as file:
            data = json.load(file)

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
        
        # TODO: It takes wrong file here, Fix thattt
        simplify_geojson(chosen_file, chosen_file.replace(".geojson", "_simplified.geojson"), tolerance)
        
        print("Everything done !")
        sleep(3)
    elif choice == 5:
        count_tags(data)
        print("Press any key to continue...")
        key = msvcrt.getch()
    elif choice == 6:
        exit()
    else:
        print("Invalid choice")

if __name__ == "__main__":
    while True:
        display_menu()
        os.system('cls')
