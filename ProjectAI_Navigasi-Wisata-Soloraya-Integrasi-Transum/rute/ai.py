import math
import heapq
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field

# Haversine formula to calculate distance between two points (lat, lon) in kilometers
def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0  # Earth's radius in kilometers
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

# Calculate travel time in minutes given distance (km) and speed (km/h)
def calculate_travel_time(distance_km: float, speed_kmh: float = 30.0) -> float:
    return (distance_km / speed_kmh) * 60  # Convert hours to minutes

@dataclass
class Node:
    """Node for A* algorithm"""
    halte_id: str
    g_cost: float = float('inf')  # Cost from start
    h_cost: float = 0.0  # Heuristic cost to goal
    f_cost: float = field(init=False)  # Total cost
    parent: Optional['Node'] = None
    route_used: str = ""
    
    def __post_init__(self):
        self.f_cost = self.g_cost + self.h_cost
    
    def __lt__(self, other):
        return self.f_cost < other.f_cost

class BusRouteSystem:
    def __init__(self):
        import json
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(base_dir, 'data', 'nodes.json'), 'r') as f:
            self.halte_data = json.load(f)
        with open(os.path.join(base_dir, 'data', 'wisata.json'), 'r') as f:
            self.wisata_data = json.load(f)
        with open(os.path.join(base_dir, 'data', 'routes.json'), 'r') as f:
            self.route_data = json.load(f)
        
        self.route_dict = {r['id']: r for r in self.route_data}
        self.route_dict["WALK"] = {"id": "WALK", "name": "Jalan Kaki", "speed_kmh": 5, "fare": 0, "hierarchy": "WALK"}
        self.route_dict["GOJEK"] = {"id": "GOJEK", "name": "Gojek/Ojek Online", "speed_kmh": 40, "fare": 10000, "hierarchy": "WALK"}
        self.hierarchy_levels = {
            "TRAIN": 1,
            "INTER_REGIONAL": 2,
            "LOCAL": 3,
            "WALK": 4
        }
        self.halte_dict = {h['id']: h for h in self.halte_data}
        
        # Inject wisata into halte_data and halte_dict to act as graph nodes
        for w in self.wisata_data:
            w_dict = {
                "id": w["id"],
                "name": w["name"],
                "lat": w["lat"],
                "lon": w["lon"],
                "type": "WISATA",
                "routes": []
            }
            self.halte_dict[w["id"]] = w_dict
            self.halte_data.append(w_dict)
            
        self.graph = self._build_graph()

    def _build_graph(self) -> Dict[str, List[Tuple[str, float, str]]]:
        """Build adjacency graph with connections between haltes and wisata"""
        graph = {}
        
        # Initialize graph and coordinates lookup
        halte_coords = {}
        for halte in self.halte_data:
            graph[halte["id"]] = []
            halte_coords[halte["id"]] = (halte["lat"], halte["lon"])
            
        # Group haltes by route for fallback mechanism
        haltes_by_route = {}
        for halte in self.halte_data:
            for r in halte.get("routes", []):
                if r not in haltes_by_route:
                    haltes_by_route[r] = []
                haltes_by_route[r].append(halte)
                
        # Build connections based on routes
        for route in self.route_data:
            route_id = route.get("id")
            if not route_id:
                continue
                
            # If route has a specific 'stops' array, use it for directed connections (1-way)
            if "stops" in route and isinstance(route["stops"], list) and len(route["stops"]) > 1:
                stops = route["stops"]
                for i in range(len(stops) - 1):
                    current_stop = stops[i]
                    next_stop = stops[i+1]
                    
                    if current_stop in halte_coords and next_stop in halte_coords:
                        distance = haversine(
                            halte_coords[current_stop][0], halte_coords[current_stop][1],
                            halte_coords[next_stop][0], halte_coords[next_stop][1]
                        )
                        # Directed edge: current -> next
                        graph[current_stop].append((next_stop, distance, route_id))
            else:
                # Fallback: Fully connected undirected graph for this route (old logic)
                haltes_on_route = haltes_by_route.get(route_id, [])
                for i in range(len(haltes_on_route)):
                    for j in range(len(haltes_on_route)):
                        if i != j:
                            h1 = haltes_on_route[i]
                            h2 = haltes_on_route[j]
                            distance = haversine(h1["lat"], h1["lon"], h2["lat"], h2["lon"])
                            graph[h1["id"]].append((h2["id"], distance, route_id))
                            
        # Build Walk / Transfer connections (cross-modal integration)
        haltes_only = [h for h in self.halte_data if h.get("type") != "WISATA"]
        wisatas = [h for h in self.halte_data if h.get("type") == "WISATA"]
        
        # 1. Transit Walk connection: Halte to Halte (Max 500m)
        for i in range(len(haltes_only)):
            for j in range(i + 1, len(haltes_only)):
                h1 = haltes_only[i]
                h2 = haltes_only[j]
                dist = haversine(h1["lat"], h1["lon"], h2["lat"], h2["lon"])
                if dist <= 0.5:
                    graph[h1["id"]].append((h2["id"], dist, "WALK"))
                    graph[h2["id"]].append((h1["id"], dist, "WALK"))
                    
        # 2. Last Mile connection: Wisata to Halte
        for wisata in wisatas:
            distances = []
            for halte in haltes_only:
                dist = haversine(wisata["lat"], wisata["lon"], halte["lat"], halte["lon"])
                distances.append((dist, halte))
            
            # Sort haltes by distance to this wisata
            distances.sort(key=lambda x: x[0])
            
            connected_count = 0
            for dist, halte in distances:
                # Connect if within 2.5km (ideal), OR force connect to the 2 nearest haltes regardless of distance
                if dist <= 2.5 or connected_count < 2:
                    mode = "WALK" if dist <= 1.5 else "GOJEK"
                    graph[halte["id"]].append((wisata["id"], dist, mode))
                    connected_count += 1
        
        return graph
    
    def heuristic(self, halte1_id: str, halte2_id: str) -> float:
        """Heuristic function: straight-line distance.
        Since we want time cost, we assume max speed of 60km/h (1km/min), so time in min is approx equal to distance in km.
        """
        halte1 = self.halte_dict[halte1_id]
        halte2 = self.halte_dict[halte2_id]
        dist = haversine(halte1["lat"], halte1["lon"], halte2["lat"], halte2["lon"])
        return dist # Return as minutes (assuming max speed 60km/h)
    
    def a_star(self, start_id: str, goal_id: str) -> Optional[Dict]:
        """A* pathfinding algorithm to find optimal route based on time and hierarchy"""
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
                    # Menentukan waktu penalti berdasarkan jenis rute
                    prev_hierarchy = self.route_dict.get(prev_route, {}).get("hierarchy", "LOCAL") if prev_route else "LOCAL"
                    curr_hierarchy = route_info.get("hierarchy", "LOCAL")
                    
                    if "TRAIN" in prev_hierarchy or "TRAIN" in curr_hierarchy:
                        transfer_penalty = 15 # Pindah dari/ke kereta lebih lama (masuk stasiun)
                    else:
                        transfer_penalty = 5 # 5 menit penalty for transferring antar bus
                        
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
        
        return None
    
    def _reconstruct_path(self, came_from: Dict, start_id: str, goal_id: str, total_time: float, total_distance: float, total_fare: int) -> Dict:
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
        }
    
    def find_route(self, start_id: str, end_id: str) -> Optional[Dict]:
        """Find optimal route between two haltes using A*"""
        return self.a_star(start_id, end_id)
    
    def find_nearest_wisata(self, halte_id: str) -> Optional[Tuple[str, str, float]]:
        """Find the nearest tourist attraction to a given halte"""
        if halte_id not in self.halte_dict:
            return None
        
        halte = self.halte_dict[halte_id]
        min_distance = float('inf')
        nearest_wisata = None
        nearest_wisata_id = None
        
        for wisata in self.wisata_data:
            distance = haversine(halte["lat"], halte["lon"], wisata["lat"], wisata["lon"])
            if distance < min_distance:
                min_distance = distance
                nearest_wisata = wisata["name"]
                nearest_wisata_id = wisata["id"]
        
        if nearest_wisata_id is None or nearest_wisata is None:
            return None
            
        return (nearest_wisata_id, nearest_wisata, min_distance)
    
    def get_route_to_attraction(self, start_id: str, attraction_name: str) -> Optional[Dict]:
        """Find route to a specific tourist attraction by routing directly to the attraction node"""
        attraction = None
        for wisata in self.wisata_data:
            if wisata["name"].lower() == attraction_name.lower():
                attraction = wisata
                break
        
        if not attraction:
            return None
        
        # Cari rute langsung ke titik wisata
        route_result = self.find_route(start_id, attraction["id"])
        if not route_result:
            return None
            
        # Parse the last segment to match the expected API structure
        if len(route_result["path"]) >= 2:
            last_halte_id = route_result["path"][-2]
            wisata_id = route_result["path"][-1]
            last_route = route_result["routes"][-1]
            last_dist = route_result["segment_distances"][-1]
            
            # Remove the wisata node from the main path arrays
            # to prevent it from being treated as a normal halte in some old logic
            route_result["path"].pop()
            route_result["path_names"].pop()
            
            route_result["routes"].pop()
            route_result["segment_distances"].pop()
            
            # Add metadata for the UI
            route_result["destination_attraction"] = attraction["name"]
            route_result["walking_distance_to_attraction"] = last_dist
            
            if last_route == "GOJEK":
                route_result["last_mile_mode"] = "Gojek"
                route_result["last_mile_time"] = (last_dist / 40) * 60
                route_result["last_mile_fare"] = 5000 + int(last_dist * 2500)
            else:
                route_result["last_mile_mode"] = "Jalan Kaki"
                route_result["last_mile_time"] = (last_dist / 5) * 60
                route_result["last_mile_fare"] = 0
            
            # Adjust total_distance and total_time to exclude the last mile
            # (as the UI expects them separate)
            route_result["total_distance"] -= last_dist
            route_result["total_time"] -= route_result["last_mile_time"]
            
            if len(route_result["routes"]) > 0:
                first_route = route_result["routes"][0]
                first_fare = self.route_dict.get(first_route, {}).get("fare", 0)
                # Avoid double counting if it was added
                pass
                
            return route_result
            
        return None

    def get_attractions_along_route(self, path: List[str], radius_km: float = 1.0) -> List[Dict]:
        """Find tourist attractions along the route within specified radius"""
        attractions_found = []
        
        for halte_id in path:
            halte = self.halte_dict[halte_id]
            
            for wisata in self.wisata_data:
                distance = haversine(halte["lat"], halte["lon"], wisata["lat"], wisata["lon"])
                if distance <= radius_km:
                    attractions_found.append({
                        "attraction": wisata["name"],
                        "attraction_id": wisata["id"],
                        "near_halte": halte["name"],
                        "near_halte_id": halte_id,
                        "distance_km": distance,
                        "walking_time_min": distance * 12  # Approx 12 min per km walking
                    })
        
        # Remove duplicates and sort by distance
        seen = set()
        unique_attractions = []
        for attr in attractions_found:
            if attr["attraction_id"] not in seen:
                seen.add(attr["attraction_id"])
                unique_attractions.append(attr)
        
        return sorted(unique_attractions, key=lambda x: x["distance_km"])
    
    def get_route_analysis(self, route_result: Dict) -> Dict:
        """Analyze route and provide recommendations"""
        if not route_result:
            return {}
        
        analysis = {
            "efficiency": "Unknown",
            "complexity": "Unknown",
            "cost_estimate": 0,
            "recommendations": [],
            "considerations": []
        }
        
        # Efficiency analysis
        total_time = route_result["total_time"]
        if total_time <= 15:
            analysis["efficiency"] = "Sangat Efisien"
        elif total_time <= 30:
            analysis["efficiency"] = "Efisien"
        elif total_time <= 45:
            analysis["efficiency"] = "Sedang"
        else:
            analysis["efficiency"] = "Kurang Efisien"
        
        # Complexity analysis
        transfers = route_result["transfers"]
        if transfers == 0:
            analysis["complexity"] = "Sangat Mudah (Langsung)"
        elif transfers == 1:
            analysis["complexity"] = "Mudah (1 Transfer)"
        elif transfers == 2:
            analysis["complexity"] = "Sedang (2 Transfer)"
        else:
            analysis["complexity"] = "Rumit (3+ Transfer)"
        
        # Cost estimate (assuming Rp 3700 per route segment)
        analysis["cost_estimate"] = (transfers + 1) * 3700
        
        # Recommendations
        if transfers == 0:
            analysis["recommendations"].append("✓ Rute langsung - sangat mudah dan efisien")
        else:
            analysis["recommendations"].append(f"⚠ Memerlukan {transfers} kali transfer")
        
        if total_time > 45:
            analysis["recommendations"].append("⚠ Perjalanan cukup lama, siapkan waktu ekstra")
        
        if route_result["total_distance"] > 15:
            analysis["recommendations"].append("⚠ Jarak cukup jauh, pastikan kondisi fisik prima")
        
        # Considerations
        analysis["considerations"].extend([
            f"Estimasi biaya: Rp {analysis['cost_estimate']:,}",
            f"Waktu perjalanan: ~{total_time:.0f} menit",
            f"Jarak total: {route_result['total_distance']:.1f} km"
        ])
        
        if transfers > 0:
            analysis["considerations"].append(f"Waktu tunggu transfer: ~{transfers * 5}-{transfers * 10} menit tambahan")
        
        return analysis

def display_halte_list(bus_system):
    """Display all available haltes"""
    print("\n=== DAFTAR HALTE TERSEDIA ===")
    print("=" * 60)
    for halte in sorted(bus_system.halte_data, key=lambda x: x["id"]):
        routes_str = ", ".join(halte["routes"])
        print(f"{halte['id']}: {halte['name']} (Rute: {routes_str})")

def display_attraction_list(bus_system):
    """Display all available tourist attractions"""
    print("\n=== DAFTAR TEMPAT WISATA ===")
    print("=" * 60)
    for wisata in sorted(bus_system.wisata_data, key=lambda x: x["id"]):
        halte_str = ", ".join(wisata["halte"])
        print(f"{wisata['id']}: {wisata['name']} (Dekat halte: {halte_str})")

def search_halte(bus_system, query):
    """Search for halte by name or ID"""
    query = query.lower()
    matches = []
    
    for halte in bus_system.halte_data:
        if (query in halte["id"].lower() or 
            query in halte["name"].lower()):
            matches.append(halte)
    
    return matches

def interactive_route_planner():
    """Interactive route planning system"""
    bus_system = BusRouteSystem()
    
    print(" === SISTEM PERENCANAAN RUTE BUS SOLO === 🚌")
    print("Menggunakan Algoritma A* untuk rute optimal\n")
    
    while True:
        print("\n" + "="*60)
        print("MENU UTAMA:")
        print("1. Cari Rute Antar Halte")
        print("2. Cari Rute ke Tempat Wisata")
        print("3. Lihat Daftar Halte")
        print("4. Lihat Daftar Tempat Wisata")
        print("5. Cari Halte")
        print("0. Keluar")
        print("="*60)
        
        choice = input("Pilih menu (0-5): ").strip()
        
        if choice == "0":
            print("Terima kasih telah menggunakan sistem ini! 🙏")
            break
        
        elif choice == "1":
            print("\n  PENCARIAN RUTE ANTAR HALTE")
            print("-" * 40)
            
            # Input start halte
            start_query = input("Dari halte (ID atau nama): ").strip()
            start_matches = search_halte(bus_system, start_query)
            
            if not start_matches:
                print(" Halte asal tidak ditemukan!")
                continue
            elif len(start_matches) > 1:
                print("Beberapa halte ditemukan:")
                for i, halte in enumerate(start_matches):
                    print(f"  {i+1}. {halte['id']}: {halte['name']}")
                try:
                    idx = int(input("Pilih nomor: ")) - 1
                    start_halte = start_matches[idx]
                except (ValueError, IndexError):
                    print(" Pilihan tidak valid!")
                    continue
            else:
                start_halte = start_matches[0]
            
            # Input end halte
            end_query = input("Ke halte (ID atau nama): ").strip()
            end_matches = search_halte(bus_system, end_query)
            
            if not end_matches:
                print(" Halte tujuan tidak ditemukan!")
                continue
            elif len(end_matches) > 1:
                print("Beberapa halte ditemukan:")
                for i, halte in enumerate(end_matches):
                    print(f"  {i+1}. {halte['id']}: {halte['name']}")
                try:
                    idx = int(input("Pilih nomor: ")) - 1
                    end_halte = end_matches[idx]
                except (ValueError, IndexError):
                    print(" Pilihan tidak valid!")
                    continue
            else:
                end_halte = end_matches[0]
            
            # Find route
            result = bus_system.find_route(start_halte["id"], end_halte["id"])
            
            if result:
                print(f"\n RUTE DITEMUKAN!")
                print("=" * 50)
                print(f"Dari: {result['path_names'][0]}")
                print(f"Ke: {result['path_names'][-1]}")
                print(f"Jarak Total: {result['total_distance']:.1f} km")
                print(f"Waktu Tempuh: ~{result['total_time']:.0f} menit")
                print(f"Jumlah Transfer: {result['transfers']}")
                
                print(f"\n RUTE DETAIL:")
                for i, (halte_name, route) in enumerate(zip(result['path_names'], result['routes'] + [''])):
                    if i == len(result['path_names']) - 1:
                        print(f"  {i+1}. {halte_name} (TUJUAN)")
                    else:
                        print(f"  {i+1}. {halte_name} → Naik Bus {route}")
                
                # Get route analysis
                analysis = bus_system.get_route_analysis(result)
                print(f"\n ANALISIS RUTE:")
                print(f"Efisiensi: {analysis['efficiency']}")
                print(f"Kompleksitas: {analysis['complexity']}")
                print(f"Estimasi Biaya: Rp {analysis['cost_estimate']:,}")
                
                print(f"\n REKOMENDASI:")
                for rec in analysis['recommendations']:
                    print(f"  {rec}")
                
                print(f"\n PERTIMBANGAN:")
                for cons in analysis['considerations']:
                    print(f"  • {cons}")
                
                # Find attractions along route
                attractions = bus_system.get_attractions_along_route(result['path'])
                if attractions:
                    print(f"\n  TEMPAT WISATA DI SEPANJANG RUTE:")
                    for attr in attractions[:5]:  # Show top 5
                        print(f"  • {attr['attraction']} (dekat {attr['near_halte']})")
                        print(f"    Jarak jalan kaki: {attr['distance_km']:.1f} km (~{attr['walking_time_min']:.0f} menit)")
            else:
                print(" Tidak ada rute yang ditemukan!")
        
        elif choice == "2":
            print("\n  PENCARIAN RUTE KE TEMPAT WISATA")
            print("-" * 40)
            
            # Show popular attractions
            print("Tempat wisata populer:")
            popular = ["Solo Safari", "Benteng Vastenburg", "Pasar Gede", "Taman Sriwedari", "Pasar Klewer"]
            for i, attraction in enumerate(popular, 1):
                print(f"  {i}. {attraction}")
            
            attraction_name = input("Nama tempat wisata: ").strip()
            
            # Input start halte
            start_query = input("Dari halte (ID atau nama): ").strip()
            start_matches = search_halte(bus_system, start_query)
            
            if not start_matches:
                print(" Halte asal tidak ditemukan!")
                continue
            elif len(start_matches) > 1:
                print("Beberapa halte ditemukan:")
                for i, halte in enumerate(start_matches):
                    print(f"  {i+1}. {halte['id']}: {halte['name']}")
                try:
                    idx = int(input("Pilih nomor: ")) - 1
                    start_halte = start_matches[idx]
                except (ValueError, IndexError):
                    print(" Pilihan tidak valid!")
                    continue
            else:
                start_halte = start_matches[0]
            
            result = bus_system.get_route_to_attraction(start_halte["id"], attraction_name)
            
            if result:
                print(f"\n RUTE KE {result['destination_attraction']} DITEMUKAN!")
                print("=" * 50)
                print(f"Dari: {result['path_names'][0]}")
                print(f"Ke Halte: {result['path_names'][-1]}")
                print(f"Jarak Bus: {result['total_distance']:.1f} km")
                print(f"Waktu Bus: ~{result['total_time']:.0f} menit")
                print(f"Jarak Jalan Kaki: {result['walking_distance_to_attraction']:.1f} km")
                print(f"Waktu Jalan Kaki: ~{result['walking_distance_to_attraction']*12:.0f} menit")
                print(f"Transfer: {result['transfers']} kali")
                
                # Show detailed route
                print(f"\n RUTE DETAIL:")
                for i, (halte_name, route) in enumerate(zip(result['path_names'], result['routes'] + [''])):
                    if i == len(result['path_names']) - 1:
                        print(f"  {i+1}. {halte_name} → Jalan kaki ke {result['destination_attraction']}")
                    else:
                        print(f"  {i+1}. {halte_name} → Naik Bus {route}")
                
                # Analysis
                analysis = bus_system.get_route_analysis(result)
                print(f"\n ANALISIS:")
                print(f"Efisiensi: {analysis['efficiency']}")
                print(f"Kompleksitas: {analysis['complexity']}")
                
                total_cost = analysis['cost_estimate']
                total_time = result['total_time'] + (result['walking_distance_to_attraction'] * 12)
                print(f"Total Biaya: Rp {total_cost:,}")
                print(f"Total Waktu: ~{total_time:.0f} menit")
                
            else:
                print(" Rute ke tempat wisata tidak ditemukan!")
        
        elif choice == "3":
            display_halte_list(bus_system)
        
        elif choice == "4":
            display_attraction_list(bus_system)
        
        elif choice == "5":
            print("\n PENCARIAN HALTE")
            print("-" * 40)
            query = input("Masukkan nama atau ID halte: ").strip()
            matches = search_halte(bus_system, query)
            
            if matches:
                print(f"\nDitemukan {len(matches)} halte:")
                for halte in matches:
                    routes_str = ", ".join(halte["routes"])
                    print(f"  • {halte['id']}: {halte['name']} (Rute: {routes_str})")
            else:
                print("s[]p  Tidak ada halte yang ditemukan!")
        
        else:
            print(" Pilihan tidak valid!")

def main():
    # Run interactive route planner
    interactive_route_planner()

if __name__ == "__main__":
    main()

    