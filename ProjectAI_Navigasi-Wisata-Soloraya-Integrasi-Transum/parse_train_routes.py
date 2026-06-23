import json

nodes_path = 'data/nodes.json'
routes_path = 'data/routes.json'

with open(nodes_path, 'r') as f:
    nodes = json.load(f)
with open(routes_path, 'r') as f:
    routes = json.load(f)

# Define the new routes
krl_stops = ["ST_BBN", "ST_SWT", "ST_KT", "ST_CE", "ST_DL", "ST_GW", "ST_PWS", "ST_SLO", "ST_SK", "ST_PL"]
batara_stops = ["ST_PWS", "ST_STA", "ST_SKH", "ST_PNT", "ST_WNG"]
bias_stops = ["ST_SMO", "ST_KDO", "ST_SLO", "ST_SK", "ST_SR"]
aglo_stops = ["ST_SLO", "ST_SLM", "ST_TW"]

new_routes = [
    {
        "id": "KA_KRL",
        "name": "KRL Yogyakarta - Palur",
        "hierarchy": "TRAIN",
        "speed_kmh": 60,
        "fare": 8000,
        "stops": krl_stops
    },
    {
        "id": "KA_BATARA_KRESNA",
        "name": "KA Batara Kresna",
        "hierarchy": "TRAIN",
        "speed_kmh": 40,
        "fare": 4000,
        "stops": batara_stops
    },
    {
        "id": "KA_BIAS",
        "name": "KA Bandara (BIAS)",
        "hierarchy": "TRAIN",
        "speed_kmh": 50,
        "fare": 15000,
        "stops": bias_stops
    },
    {
        "id": "KA_AGLOMERASI",
        "name": "KA Aglomerasi",
        "hierarchy": "TRAIN",
        "speed_kmh": 60,
        "fare": 50000,
        "stops": aglo_stops
    }
]

# Append new routes if not exist
existing_route_ids = {r["id"] for r in routes}
for nr in new_routes:
    if nr["id"] not in existing_route_ids:
        routes.append(nr)

# Map stops to node
for nr in new_routes:
    r_id = nr["id"]
    r_stops = nr["stops"]
    for node in nodes:
        if node["id"] in r_stops:
            if r_id not in node["routes"]:
                node["routes"].append(r_id)

with open(nodes_path, 'w') as f:
    json.dump(nodes, f, indent=4)
with open(routes_path, 'w') as f:
    json.dump(routes, f, indent=4)

print("SUCCESS")
