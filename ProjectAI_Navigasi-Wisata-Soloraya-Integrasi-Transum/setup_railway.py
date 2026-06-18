import requests
import json
import math

query = """
[out:json][timeout:25];
way["railway"="rail"](-8.0, 110.4, -7.2, 111.1);
out geom;
"""

url = "https://overpass-api.de/api/interpreter"
print("Fetching from overpass...")
response = requests.post(url, data={'data': query})
if response.status_code != 200:
    print("Error:", response.status_code, response.text)
    exit(1)

osm_data = response.json()
print("Parsing data...")
features = []

for element in osm_data.get('elements', []):
    if element['type'] == 'way' and 'geometry' in element:
        coords = [[pt['lon'], pt['lat']] for pt in element['geometry']]
        features.append({
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": coords
            }
        })

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open('static/rel_kereta.json', 'w') as f:
    json.dump(geojson, f)

print(f"Saved {len(features)} railway segments to static/rel_kereta.json")
