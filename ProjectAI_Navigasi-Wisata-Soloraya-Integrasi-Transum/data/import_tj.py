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

    # Dictionary to quickly look up existing nodes by name (case insensitive)
    name_to_node = {n['name'].lower(): n for n in nodes}
    
    # We will collect all unique stops and their coordinates
    new_stops = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        lines = list(reader)

    # Data starts at row 2 (0-indexed 2 is the 3rd line, wait: lines[2] is the first data row)
    
    # Southbound: col 1 (name), col 4 (coord)
    # Northbound: col 3 (name), col 6 (coord)

    # Let's do a two-pass approach. 
    # First pass: collect all coordinates for names.
    name_to_coord = {}
    
    for row in lines[2:]:
        if not row: continue
        
        # Southbound
        if len(row) > 1 and row[1].strip():
            sb_name = clean_name(row[1])
            sb_coord_str = row[4] if len(row) > 4 else None
            sb_coord = clean_coord(sb_coord_str)
            if sb_coord:
                name_to_coord[sb_name.lower()] = sb_coord
                
    for row in lines[2:]:
        if not row: continue
        # Northbound
        if len(row) > 3 and row[3].strip():
            nb_name = clean_name(row[3])
            nb_coord_str = row[6] if len(row) > 6 else None
            nb_coord = clean_coord(nb_coord_str)
            if nb_coord:
                name_to_coord[nb_name.lower()] = nb_coord

    # Add Trans Jateng route to routes.json
    tj_route_id = "TJ1"
    route_exists = any(r['id'] == tj_route_id for r in routes)
    if not route_exists:
        routes.append({
            "id": tj_route_id,
            "name": "Trans Jateng (Tirtonadi - Wonogiri)",
            "hierarchy": "BRT",
            "speed_kmh": 35,
            "fare": 4000
        })

    # Now assign route to nodes
    def process_stop(name, coord):
        if not name: return
        name_lower = name.lower()
        
        # Determine coordinate
        final_coord = coord
        if not final_coord and name_lower in name_to_coord:
            final_coord = name_to_coord[name_lower]
            
        if name_lower in name_to_node:
            # Update existing node
            node = name_to_node[name_lower]
            if tj_route_id not in node['routes']:
                node['routes'].append(tj_route_id)
        else:
            # Create new node
            if final_coord:
                new_id = f"TJ_{len(new_stops) + 1:03d}"
                new_node = {
                    "id": new_id,
                    "name": name,
                    "lat": final_coord[0],
                    "lon": final_coord[1],
                    "routes": [tj_route_id],
                    "type": "HALTE"
                }
                new_stops[name_lower] = new_node
                name_to_node[name_lower] = new_node
                nodes.append(new_node)
            else:
                print(f"Warning: No coordinates found for new stop {name}")

    for row in lines[2:]:
        if len(row) > 1 and row[1].strip():
            name = clean_name(row[1])
            coord = clean_coord(row[4]) if len(row) > 4 else None
            process_stop(name, coord)
            
        if len(row) > 3 and row[3].strip():
            name = clean_name(row[3])
            coord = clean_coord(row[6]) if len(row) > 6 else None
            process_stop(name, coord)

    # Write back
    with open(nodes_file, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, indent=4)
        
    with open(routes_file, 'w', encoding='utf-8') as f:
        json.dump(routes, f, indent=4)

    print(f"Added {len(new_stops)} new stops.")
    print("Updated routes and existing stops successfully.")

if __name__ == "__main__":
    main()
