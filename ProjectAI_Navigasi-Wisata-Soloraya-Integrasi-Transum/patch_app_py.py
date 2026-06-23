import re

with open('app.py', 'r') as f:
    content = f.read()

target = """        for h_id in result["path"]:
            halte = bus_system.halte_dict[h_id]
            koordinat_path.append({
                "lat": halte["lat"],
                "lng": halte["lon"],
                "name": halte["name"]
            })"""

replacement = """        for i, h_id in enumerate(result["path"]):
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

content = content.replace(target, replacement)

with open('app.py', 'w') as f:
    f.write(content)

print("SUCCESS")
