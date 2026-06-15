import re

with open('rute/ai.py', 'r') as f:
    content = f.read()

new_get_route = """    def get_route_to_attraction(self, start_id: str, attraction_name: str) -> Optional[Dict]:
        \"\"\"Find route to a specific tourist attraction\"\"\"
        attraction = None
        for wisata in self.wisata_data:
            if wisata["name"].lower() == attraction_name.lower():
                attraction = wisata
                break
        
        if not attraction:
            return None
        
        best_halte = None
        min_distance = float('inf')
        
        # Now we don't rely on attraction["halte"], we search all haltes globally!
        for halte_id, halte in self.halte_dict.items():
            distance = haversine(
                halte["lat"], halte["lon"],
                attraction["lat"], attraction["lon"]
            )
            if distance < min_distance:
                min_distance = distance
                best_halte = halte_id
        
        if not best_halte:
            return None
        
        route_result = self.find_route(start_id, best_halte)
        if route_result:
            route_result["destination_attraction"] = attraction["name"]
            route_result["walking_distance_to_attraction"] = min_distance
            
            # Logic for Gojek vs Walking
            if min_distance > 1.5:
                route_result["last_mile_mode"] = "Gojek"
                route_result["last_mile_time"] = (min_distance / 40) * 60 # 40 km/h for gojek
                route_result["last_mile_fare"] = min_distance * 2500
            else:
                route_result["last_mile_mode"] = "Jalan Kaki"
                route_result["last_mile_time"] = min_distance * 12 # 12 min/km walking
                route_result["last_mile_fare"] = 0
            
            # Add base ticket fare if not already calculated properly at start
            # The start node doesn't charge fare in a_star if prev_route=None. We need to add the very first fare.
            if len(route_result["routes"]) > 0:
                first_route = route_result["routes"][0]
                first_fare = self.route_dict.get(first_route, {}).get("fare", 0)
                route_result["total_fare"] += first_fare
                
        return route_result"""

content = re.sub(r'    def get_route_to_attraction.*?return route_result', new_get_route, content, flags=re.DOTALL)

with open('rute/ai.py', 'w') as f:
    f.write(content)

print("Done updating gojek logic.")
