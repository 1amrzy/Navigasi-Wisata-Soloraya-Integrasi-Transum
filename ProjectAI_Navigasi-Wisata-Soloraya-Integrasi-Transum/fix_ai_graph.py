import re

with open('rute/ai.py', 'r') as f:
    content = f.read()

new_build_graph = """    def _build_graph(self) -> Dict[str, List[Tuple[str, float, str]]]:
        \"\"\"Build adjacency graph with connections between haltes\"\"\"
        graph = {}
        for halte in self.halte_data:
            graph[halte["id"]] = []
            
        for i, halte1 in enumerate(self.halte_data):
            for j, halte2 in enumerate(self.halte_data):
                if i != j:
                    distance = haversine(
                        halte1["lat"], halte1["lon"],
                        halte2["lat"], halte2["lon"]
                    )
                    common_routes = set(halte1["routes"]) & set(halte2["routes"])
                    
                    if common_routes:
                        # Connect with transum route
                        route = list(common_routes)[0]
                        graph[halte1["id"]].append((halte2["id"], distance, route))
                    elif distance <= 0.8: # Allow walking transfer up to 800 meters
                        # Connect with walking edge
                        graph[halte1["id"]].append((halte2["id"], distance, "WALK"))
        return graph"""

content = re.sub(r'    def _build_graph\(self\).*?return graph', new_build_graph, content, flags=re.DOTALL)

# In a_star, we must handle route_info for "WALK"
# It currently defaults to: route_info = self.route_dict.get(route, {"speed_kmh": 30, "fare": 0, "hierarchy": "LOCAL"})
# We will just change the default to match WALK if it's WALK
# Or we can just add "WALK" to self.route_dict during init. It's safer to add it to route_dict.
# Let's add it to route_dict in __init__
new_init = """        self.route_dict = {r['id']: r for r in self.route_data}
        self.route_dict["WALK"] = {"id": "WALK", "name": "Jalan Kaki", "speed_kmh": 5, "fare": 0, "hierarchy": "WALK"}"""

content = re.sub(r'        self\.route_dict = \{r\[\'id\'\]: r for r in self\.route_data\}', new_init, content)

with open('rute/ai.py', 'w') as f:
    f.write(content)

print("SUCCESS")
