import re

with open('app.py', 'r') as f:
    content = f.read()

target = """        for i, h_id in enumerate(result["path"]):
            halte = bus_system.halte_dict[h_id]
            mode = "WALK"
            route_id = "WALK"
            if i < len(result["routes"]):
                route_id = result["routes"][i]
                route_info = bus_system.route_dict.get(route_id, {})
                mode = route_info.get("hierarchy", "LOCAL")
                
            koordinat_path.append({
                "lat": halte["lat"],
                "lng": halte["lon"],
                "name": halte["name"],
                "route": route_id,
                "mode": mode
            })"""

replacement = """        import os
        import json
        rail_segments = {}
        if os.path.exists('data/rail_segments.json'):
            with open('data/rail_segments.json', 'r') as f:
                rail_segments = json.load(f)
                
        for i, h_id in enumerate(result["path"]):
            halte = bus_system.halte_dict[h_id]
            mode = "WALK"
            route_id = "WALK"
            if i < len(result["routes"]):
                route_id = result["routes"][i]
                route_info = bus_system.route_dict.get(route_id, {})
                mode = route_info.get("hierarchy", "LOCAL")
                
            koordinat_path.append({
                "lat": halte["lat"],
                "lng": halte["lon"],
                "name": halte["name"],
                "route": route_id,
                "mode": mode,
                "is_intermediate": False
            })
            
            if mode == "TRAIN" and i < len(result["path"]) - 1:
                next_h_id = result["path"][i+1]
                pair_key = f"{h_id}_{next_h_id}"
                if pair_key in rail_segments:
                    for pt in rail_segments[pair_key][1:-1]:
                        koordinat_path.append({
                            "lat": pt["lat"],
                            "lng": pt["lng"],
                            "name": f"Track {h_id}-{next_h_id}",
                            "route": route_id,
                            "mode": mode,
                            "is_intermediate": True
                        })"""

content = content.replace(target, replacement)

with open('app.py', 'w') as f:
    f.write(content)

print("SUCCESS")
