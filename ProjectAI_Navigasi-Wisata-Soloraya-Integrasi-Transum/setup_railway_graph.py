import json
import urllib.request
import urllib.parse
import math

# Overpass QL query to get railways in the bounding box
# Bbox: south, west, north, east
query = """
[out:json][timeout:25];
way["railway"="rail"](-8.0, 110.4, -7.2, 111.1);
out geom;
"""

url = "https://overpass-api.de/api/interpreter"
data = urllib.parse.urlencode({'data': query}).encode('utf-8')

print("Fetching OSM railway data...")
try:
    req = urllib.request.Request(url, data=data)
    with urllib.request.urlopen(req) as response:
        osm_data = json.loads(response.read().decode('utf-8'))
except Exception as e:
    print("Error fetching from Overpass API:", e)
    exit(1)

nodes = {}
graph = {}

# Build graph from ways
for element in osm_data.get('elements', []):
    if element['type'] == 'way' and 'geometry' in element:
        geom = element['geometry']
        for i in range(len(geom)):
            pt = geom[i]
            node_id = f"{pt['lat']}_{pt['lon']}"
            if node_id not in nodes:
                nodes[node_id] = pt
            if node_id not in graph:
                graph[node_id] = []
                
            # Connect to previous node
            if i > 0:
                prev_pt = geom[i-1]
                prev_id = f"{prev_pt['lat']}_{prev_pt['lon']}"
                
                # Calculate distance
                dlat = math.radians(pt['lat'] - prev_pt['lat'])
                dlon = math.radians(pt['lon'] - prev_pt['lon'])
                a = math.sin(dlat/2)**2 + math.cos(math.radians(prev_pt['lat'])) * math.cos(math.radians(pt['lat'])) * math.sin(dlon/2)**2
                c = 2 * math.asin(math.sqrt(a))
                dist = 6371 * c
                
                graph[node_id].append({'node': prev_id, 'dist': dist})
                graph[prev_id].append({'node': node_id, 'dist': dist})

# Save to file
railway_data = {
    'nodes': nodes,
    'graph': graph
}

with open('data/railway_graph.json', 'w') as f:
    json.dump(railway_data, f)

print(f"Saved {len(nodes)} railway nodes and {len(graph)} graph entries to data/railway_graph.json")
