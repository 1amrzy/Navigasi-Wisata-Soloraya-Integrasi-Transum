import re

with open('rute/ai.py', 'r') as f:
    content = f.read()

# Replace heuristic
new_heuristic = """    def heuristic(self, halte1_id: str, halte2_id: str) -> float:
        \"\"\"Heuristic function: straight-line distance.
        Since we want time cost, we assume max speed of 60km/h (1km/min), so time in min is approx equal to distance in km.
        \"\"\"
        halte1 = self.halte_dict[halte1_id]
        halte2 = self.halte_dict[halte2_id]
        dist = haversine(halte1["lat"], halte1["lon"], halte2["lat"], halte2["lon"])
        return dist # Return as minutes (assuming max speed 60km/h)"""
content = re.sub(r'    def heuristic.*?return haversine\(.*?\)', new_heuristic, content, flags=re.DOTALL)

# Replace a_star
new_astar = """    def a_star(self, start_id: str, goal_id: str) -> Optional[Dict]:
        \"\"\"A* pathfinding algorithm to find optimal route based on time and hierarchy\"\"\"
        if start_id not in self.halte_dict or goal_id not in self.halte_dict:
            return None
        
        if start_id == goal_id:
            return {
                "path": [start_id],
                "total_distance": 0.0,
                "total_time": 0.0,
                "routes": [],
                "transfers": 0,
                "fare": 0
            }
        
        open_set = []
        heapq.heappush(open_set, Node(start_id, g_cost=0.0, h_cost=self.heuristic(start_id, goal_id)))
        
        closed_set = set()
        open_set_dict = {start_id: 0.0}
        
        came_from = {}
        g_score = {start_id: 0.0}
        dist_score = {start_id: 0.0}
        fare_score = {start_id: 0}
        
        while open_set:
            current_node = heapq.heappop(open_set)
            current_id = current_node.halte_id
            
            if current_id in closed_set:
                continue
            
            if current_id == goal_id:
                return self._reconstruct_path(came_from, start_id, goal_id, g_score[goal_id], dist_score[goal_id], fare_score[goal_id])
            
            closed_set.add(current_id)
            
            for neighbor_id, distance, route in self.graph.get(current_id, []):
                if neighbor_id in closed_set:
                    continue
                
                route_info = self.route_dict.get(route, {"speed_kmh": 30, "fare": 0, "hierarchy": "LOCAL"})
                speed = route_info.get("speed_kmh", 30)
                
                # Calculate time in minutes
                time_cost = (distance / speed) * 60
                
                transfer_penalty = 0
                fare_add = 0
                prev_route = came_from.get(current_id, (None, None, None))[1]
                
                if prev_route != route:
                    transfer_penalty = 5 # 5 minutes penalty for transferring
                    fare_add = route_info.get("fare", 0) # pay fare when boarding a new route
                
                tentative_g_score = g_score[current_id] + time_cost + transfer_penalty
                tentative_dist_score = dist_score[current_id] + distance
                tentative_fare_score = fare_score[current_id] + fare_add
                
                if neighbor_id not in g_score or tentative_g_score < g_score[neighbor_id]:
                    came_from[neighbor_id] = (current_id, route, distance)
                    g_score[neighbor_id] = tentative_g_score
                    dist_score[neighbor_id] = tentative_dist_score
                    fare_score[neighbor_id] = tentative_fare_score
                    h_score = self.heuristic(neighbor_id, goal_id)
                    
                    if neighbor_id not in open_set_dict or tentative_g_score < open_set_dict[neighbor_id]:
                        heapq.heappush(open_set, Node(
                            neighbor_id,
                            g_cost=tentative_g_score,
                            h_cost=h_score
                        ))
                        open_set_dict[neighbor_id] = tentative_g_score
        
        return None"""
content = re.sub(r'    def a_star\(self, start_id: str, goal_id: str\).*?return None  # No path found', new_astar, content, flags=re.DOTALL)

# Replace _reconstruct_path
new_reconstruct = """    def _reconstruct_path(self, came_from: Dict, start_id: str, goal_id: str, total_time: float, total_distance: float, total_fare: int) -> Dict:
        path = []
        routes = []
        distances = []
        current = goal_id
        
        while current != start_id:
            path.append(current)
            parent, route, distance = came_from[current]
            routes.append(route)
            distances.append(distance)
            current = parent
        
        path.append(start_id)
        path.reverse()
        routes.reverse()
        distances.reverse()
        
        transfers = 0
        for i in range(1, len(routes)):
            if routes[i] != routes[i-1]:
                transfers += 1
        
        return {
            "path": path,
            "path_names": [self.halte_dict[h_id]["name"] for h_id in path],
            "total_distance": total_distance,
            "total_time": total_time,
            "routes": routes,
            "segment_distances": distances,
            "transfers": transfers,
            "total_fare": total_fare
        }"""
content = re.sub(r'    def _reconstruct_path\(self, came_from: Dict, start_id: str, goal_id: str, total_distance: float\) -> Dict:.*?transfers\n        }', new_reconstruct, content, flags=re.DOTALL)

with open('rute/ai.py', 'w') as f:
    f.write(content)

print("Done updating a_star logic.")
