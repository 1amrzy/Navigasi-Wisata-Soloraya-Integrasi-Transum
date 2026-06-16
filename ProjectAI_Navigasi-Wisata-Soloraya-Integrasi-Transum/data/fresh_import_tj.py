import csv
import json
import os
import re

def clean_coord(coord_str):
    if not coord_str or coord_str.strip() == '-' or coord_str.strip() == '':
        return None
    try:
        parts = coord_str.replace('"', '').split(',')
        return float(parts[0].strip()), float(parts[1].strip())
    except:
        return None

def strip_number(name):
    return re.sub(r'\s+\d+$', '', name.strip()).lower()

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nodes_file = os.path.join(base_dir, 'nodes.json')
    routes_file = os.path.join(base_dir, 'routes.json')
    csv_file = os.path.join(base_dir, 'transjateng.csv')

    with open(nodes_file, 'r', encoding='utf-8') as f:
        nodes = json.load(f)
    with open(routes_file, 'r', encoding='utf-8') as f:
        routes = json.load(f)

    # 1. Clean up old TJ data completely
    # Remove routes SW and WS
    routes = [r for r in routes if r['id'] not in ['SW', 'WS', 'TJ1']]
    
    routes.append({
        "id": "SW",
        "name": "Trans Jateng (Solo - Wonogiri)",
        "hierarchy": "BRT",
        "speed_kmh": 35,
        "fare": 4000
    })
    routes.append({
        "id": "WS",
        "name": "Trans Jateng (Wonogiri - Solo)",
        "hierarchy": "BRT",
        "speed_kmh": 35,
        "fare": 4000
    })

    # Remove SW, WS, TJ1 from all nodes
    for node in nodes:
        node['routes'] = [r for r in node.get('routes', []) if r not in ['SW', 'WS', 'TJ1']]
        
    # Also delete nodes that were created purely for TJ (those starting with TJ_)
    nodes = [n for n in nodes if not n['id'].startswith('TJ_')]

    name_to_node = {n['name'].lower(): n for n in nodes}

    # 2. Parse CSV
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)

    # First pass: collect ALL coordinates mapping stripped names to coordinates
    coord_dict = {}
    for row in lines[2:]:
        if not row: continue
        # Col 1 (SW) coords in Col 4
        if len(row) > 1 and row[1].strip():
            c = clean_coord(row[4] if len(row) > 4 else None)
            if c: coord_dict[strip_number(row[1])] = c
        # Col 3 (WS) coords in Col 6
        if len(row) > 3 and row[3].strip():
            c = clean_coord(row[6] if len(row) > 6 else None)
            if c: coord_dict[strip_number(row[3])] = c

    new_stops = {}

    def process_stop(name, coord, route_id):
        name_clean = name.strip()
        if not name_clean: return
        
        final_coord = coord
        if not final_coord:
            final_coord = coord_dict.get(strip_number(name_clean))
            
        key = name_clean.lower()
        if key in name_to_node:
            node = name_to_node[key]
            if route_id not in node['routes']:
                node['routes'].append(route_id)
        elif key in new_stops:
            node = new_stops[key]
            if route_id not in node['routes']:
                node['routes'].append(route_id)
        else:
            if final_coord:
                # Find highest TJ id to avoid conflicts if any remain
                new_id = f"TJ_{len(new_stops) + 1:03d}"
                node = {
                    "id": new_id,
                    "name": name_clean,
                    "lat": final_coord[0],
                    "lon": final_coord[1],
                    "routes": [route_id],
                    "type": "HALTE"
                }
                new_stops[key] = node
            else:
                print(f"Warning: No coordinates for {name_clean}")

    for row in lines[2:]:
        if not row: continue
        # SW (Col 1)
        if len(row) > 1 and row[1].strip():
            process_stop(row[1], clean_coord(row[4] if len(row) > 4 else None), 'SW')
        # WS (Col 3)
        if len(row) > 3 and row[3].strip():
            process_stop(row[3], clean_coord(row[6] if len(row) > 6 else None), 'WS')

    nodes.extend(new_stops.values())

    with open(nodes_file, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, indent=4)
    with open(routes_file, 'w', encoding='utf-8') as f:
        json.dump(routes, f, indent=4)

if __name__ == "__main__":
    main()
