import csv
import json
import os
import re

def clean_name(name):
    # Remove trailing 1, 2, 3 if preceded by space
    return re.sub(r'\s+\d+$', '', name.strip())

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nodes_file = os.path.join(base_dir, 'nodes.json')
    routes_file = os.path.join(base_dir, 'routes.json')
    csv_file = os.path.join(base_dir, 'transjateng.csv')

    with open(nodes_file, 'r', encoding='utf-8') as f:
        nodes = json.load(f)
    
    with open(routes_file, 'r', encoding='utf-8') as f:
        routes = json.load(f)

    # 1. Hapus rute TJ1 lama dan ganti dengan SW dan WS
    routes = [r for r in routes if r['id'] != 'TJ1']
    
    route_sw = {
        "id": "SW",
        "name": "Trans Jateng (Solo - Wonogiri)",
        "hierarchy": "BRT",
        "speed_kmh": 35,
        "fare": 4000
    }
    route_ws = {
        "id": "WS",
        "name": "Trans Jateng (Wonogiri - Solo)",
        "hierarchy": "BRT",
        "speed_kmh": 35,
        "fare": 4000
    }
    
    if not any(r['id'] == 'SW' for r in routes):
        routes.append(route_sw)
    if not any(r['id'] == 'WS' for r in routes):
        routes.append(route_ws)

    # 2. Hapus TJ1 dari semua halte yang ada
    for node in nodes:
        if 'TJ1' in node['routes']:
            node['routes'].remove('TJ1')
            
    name_to_node = {n['name'].lower(): n for n in nodes}

    # 3. Baca CSV dan tetapkan rute baru (SW untuk arah pergi, WS untuk arah pulang)
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)

    # Kolom 1 adalah arah Solo -> Wonogiri (SW)
    # Kolom 3 adalah arah Wonogiri -> Solo (WS)
    for row in lines[2:]:
        if not row: continue
        
        # Arah Pergi (SW)
        if len(row) > 1 and row[1].strip():
            name = clean_name(row[1]).lower()
            if name in name_to_node:
                if 'SW' not in name_to_node[name]['routes']:
                    name_to_node[name]['routes'].append('SW')
                    
        # Arah Pulang (WS)
        if len(row) > 3 and row[3].strip():
            name = clean_name(row[3]).lower()
            if name in name_to_node:
                if 'WS' not in name_to_node[name]['routes']:
                    name_to_node[name]['routes'].append('WS')

    # Write back
    with open(nodes_file, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, indent=4)
        
    with open(routes_file, 'w', encoding='utf-8') as f:
        json.dump(routes, f, indent=4)

    print("Berhasil memisahkan rute menjadi SW dan WS!")

if __name__ == "__main__":
    main()
