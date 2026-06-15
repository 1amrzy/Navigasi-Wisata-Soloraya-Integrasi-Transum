import re

with open('rute/ai.py', 'r') as f:
    content = f.read()

new_func = """    def get_route_to_attraction(self, start_id: str, attraction_name: str) -> Optional[Dict]:
        \"\"\"Find route to a specific tourist attraction\"\"\"
        attraction = None
        for wisata in self.wisata_data:
            if wisata["name"].lower() == attraction_name.lower():
                attraction = wisata
                break
        
        if not attraction:
            return None
        
        # Calculate distance to all haltes
        halte_distances = []
        for halte_id, halte in self.halte_dict.items():
            import math
            def haversine_local(lat1, lon1, lat2, lon2):
                R = 6371.0
                lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
                return R * 2 * math.asin(math.sqrt(a))
            
            dist = haversine_local(
                halte["lat"], halte["lon"],
                attraction["lat"], attraction["lon"]
            )
            halte_distances.append((dist, halte_id))
            
        # Sort by closest first
        halte_distances.sort(key=lambda x: x[0])
        
        # Try finding a route to the closest haltes until one succeeds
        for min_distance, best_halte in halte_distances:
            route_result = self.find_route(start_id, best_halte)
            if route_result:
                route_result["destination_attraction"] = attraction["name"]
                route_result["walking_distance_to_attraction"] = min_distance
                
                if min_distance > 1.5:
                    route_result["last_mile_mode"] = "Gojek"
                    route_result["last_mile_time"] = (min_distance / 40) * 60
                    route_result["last_mile_fare"] = min_distance * 2500
                else:
                    route_result["last_mile_mode"] = "Jalan Kaki"
                    route_result["last_mile_time"] = min_distance * 12
                    route_result["last_mile_fare"] = 0
                
                if len(route_result["routes"]) > 0:
                    first_route = route_result["routes"][0]
                    first_fare = self.route_dict.get(first_route, {}).get("fare", 0)
                    route_result["total_fare"] += first_fare
                    
                return route_result
                
        return None"""

content = re.sub(r'    def get_route_to_attraction\(self, start_id: str, attraction_name: str\) -> Optional\[Dict\]:.*?return route_result', new_func, content, flags=re.DOTALL)

with open('rute/ai.py', 'w') as f:
    f.write(content)

print("SUCCESS")
