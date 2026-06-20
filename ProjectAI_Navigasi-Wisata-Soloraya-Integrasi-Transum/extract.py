import json
import os
import sys

sys.path.append('.')
from rute.rute import halte_data, wisata_data

os.makedirs('data', exist_ok=True)

for h in halte_data:
    h['type'] = 'HALTE'

with open('data/nodes.json', 'w') as f:
    json.dump(halte_data, f, indent=4)

with open('data/wisata.json', 'w') as f:
    json.dump(wisata_data, f, indent=4)

routes = [
    {"id": "K1", "name": "Koridor 1", "hierarchy": "LOCAL", "speed_kmh": 30},
    {"id": "K3", "name": "Koridor 3", "hierarchy": "LOCAL", "speed_kmh": 30},
    {"id": "K4", "name": "Koridor 4", "hierarchy": "LOCAL", "speed_kmh": 30},
    {"id": "K5", "name": "Koridor 5", "hierarchy": "LOCAL", "speed_kmh": 30},
    {"id": "K6", "name": "Koridor 6", "hierarchy": "LOCAL", "speed_kmh": 30},
    {"id": "FD2", "name": "Feeder 2", "hierarchy": "LOCAL", "speed_kmh": 25},
    {"id": "FD7", "name": "Feeder 7", "hierarchy": "LOCAL", "speed_kmh": 25},
    {"id": "FD8", "name": "Feeder 8", "hierarchy": "LOCAL", "speed_kmh": 25},
    {"id": "FD9", "name": "Feeder 9", "hierarchy": "LOCAL", "speed_kmh": 25},
    {"id": "FD10", "name": "Feeder 10", "hierarchy": "LOCAL", "speed_kmh": 25}
]

with open('data/routes.json', 'w') as f:
    json.dump(routes, f, indent=4)

print("Extraction successful.")
