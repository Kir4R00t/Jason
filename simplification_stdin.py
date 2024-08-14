import geopandas as gpd
import json
import sys
from shapely.geometry import LineString, MultiLineString, MultiPolygon, Polygon
from simplification.cutil import simplify_coords
from io import StringIO

def simplify_geojson(geojson_data, tolerance):
    # StringIO string --> file-like object powinno pomóc
    geojson_file_like = StringIO(geojson_data)
    gdf = gpd.read_file(geojson_file_like)

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
    return simplified_geojson

def main():
    if len(sys.argv) != 2:
        print("Error, please specify tolerance --> python3 simplify.py <tolerance>")
        return
    
    tolerance = float(sys.argv[1])

    input_geojson = sys.stdin.read()
    simplified_geojson = simplify_geojson(input_geojson, tolerance)
    
    print(json.dumps(simplified_geojson, indent=2))

if __name__ == "__main__":
    main()
