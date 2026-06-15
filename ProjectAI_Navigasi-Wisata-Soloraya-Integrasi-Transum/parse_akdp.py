import json

raw_data = """Bus AKDP Langsung Jaya	Terminal Tirtonadi	-7.551750, 110.819611
	RS Dr. Oen Kandang Sapi	-7.555456611059432, 110.83739045206134
	Terminal Palur	-7.565980353361813, 110.87255700504775
	Papahan	-7.589650951463289, 110.9263661048479
	Alun Alun Karanganyar	-7.593548946468367, 110.94026558246695
	Terminal Karanganyar	-7.60461882974963, 110.97193717513953
	Terminal Karangpandan	-7.614425362654565, 111.07403841909803
	Terminal Tawangmangu	-7.668736395402045, 111.11940270042919
Bus AKDP Wahyu Putro	Terminal Tirtonadi	-7.551750, 110.819611
	Terminal Sukoharjo	-7.694609608640546, 110.84926336293498
	Terminal Giri Adipura	-7.791390155407918, 110.90071358096273
	Terminal Baturetno	-7.98059193643646, 110.93444492421135
Bus AKDP Purwo Widodo	Terminal Tirtonadi	-7.551750, 110.819611
	Terminal Sukoharjo	-7.694609608640546, 110.84926336293498
	Terminal Giri Adipura	-7.791390155407918, 110.90071358096273
	Terminal Baturetno	-7.98059193643646, 110.93444492421135
Bus AKDP Safari / Royal Safari	Terminal Tirtonadi	-7.551750, 110.819611
	Terminal Kartasura	-7.54394566724765, 110.73594639966804
	Terminal Penggung (Boyolali)	-7.5015310374600475, 110.5768259864474
	Terminal Ampel (Boyolali)	-7.430224768209558, 110.53301656604138
Bus AKDP Taruna	Terminal Tirtonadi	-7.551750, 110.819611
	Terminal Kartasura	-7.54394566724765, 110.73594639966804
	Terminal Penggung (Boyolali)	-7.5015310374600475, 110.5768259864474
	Terminal Ampel (Boyolali)	-7.430224768209558, 110.53301656604138
Bus AKDP Rela	Terminal Tirtonadi	-7.551750, 110.819611
	Joglo	-7.540180717522594, 110.820542798379
	Gemolong (Sragen)	-7.398406250246949, 110.82635873159448
	Sumberlawang (Sragen)	-7.3292192449956115, 110.86124054553721
Bus AKDP Harta Sanjaya	Terminal Tirtonadi	-7.551750, 110.819611
	Terminal Palur	-7.565980353361813, 110.87255700504775
	Terminal Pilangsari (Sragen)	-7.410488077754635, 111.05079756861645"""

import os
nodes_path = 'data/nodes.json'
routes_path = 'data/routes.json'

with open(nodes_path, 'r') as f:
    nodes = json.load(f)

with open(routes_path, 'r') as f:
    existing_routes = json.load(f)

# Create lookup dict to avoid duplicates and to assign routes
node_lookup = {n['name']: n for n in nodes}
# Tirtonadi exists? Let's check. Actually Terminal Tirtonadi might already exist in Halte.
# If not, we'll create it.

current_bus = None
new_routes_info = {} # bus_name -> list of node ids

def get_or_create_node(name, lat, lon):
    # exact name match
    if name in node_lookup:
        return node_lookup[name]['id']
    
    # Try case insensitive
    for n_name, n in node_lookup.items():
        if name.lower() in n_name.lower() or n_name.lower() in name.lower():
            # If distance is very close, it's the same node
            import math
            def haversine(lat1, lon1, lat2, lon2):
                R = 6371.0
                lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
                c = 2 * math.asin(math.sqrt(a))
                return R * c
            if haversine(float(lat), float(lon), n['lat'], n['lon']) < 0.5:
                return n['id']

    new_id = f"AKDP_{len(node_lookup) + 1:02d}"
    new_node = {
        "id": new_id,
        "name": name,
        "lat": float(lat),
        "lon": float(lon),
        "routes": [],
        "type": "TERMINAL" if "Terminal" in name else "HALTE"
    }
    nodes.append(new_node)
    node_lookup[name] = new_node
    return new_id

for line in raw_data.split('\n'):
    parts = line.split('\t')
    if len(parts) == 3:
        # First row of a bus
        current_bus = parts[0].strip()
        name = parts[1].strip()
        coords = parts[2].strip().split(',')
        lat = coords[0].strip()
        lon = coords[1].strip()
        
        node_id = get_or_create_node(name, lat, lon)
        if current_bus not in new_routes_info:
            new_routes_info[current_bus] = []
        new_routes_info[current_bus].append(node_id)
        
    elif len(parts) == 2:
        # Subsequent row (tab at the start usually means parts[0] is empty)
        # Or maybe it split into 3 but parts[0] is empty
        pass
    else:
        # Let's handle parts correctly
        if line.startswith('\t'):
            name, coords_str = line.strip().split('\t')
            coords = coords_str.split(',')
            lat = coords[0].strip()
            lon = coords[1].strip()
            
            node_id = get_or_create_node(name, lat, lon)
            new_routes_info[current_bus].append(node_id)

# Now, add route info to nodes
for bus_name, path in new_routes_info.items():
    route_id = bus_name.replace(' ', '_').replace('/', '').upper()
    route = {
        "id": route_id,
        "name": bus_name,
        "hierarchy": "INTER_REGIONAL", # AKDP is inter-city
        "speed_kmh": 40,
        "stops": path
    }
    existing_routes.append(route)
    
    # Append route_id to nodes
    for node in nodes:
        if node['id'] in path:
            if route_id not in node['routes']:
                node['routes'].append(route_id)

with open(nodes_path, 'w') as f:
    json.dump(nodes, f, indent=4)

with open(routes_path, 'w') as f:
    json.dump(existing_routes, f, indent=4)

print("SUCCESS: Data injected.")
