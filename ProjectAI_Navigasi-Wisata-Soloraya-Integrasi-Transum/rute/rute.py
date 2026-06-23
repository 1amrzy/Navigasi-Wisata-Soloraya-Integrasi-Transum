# import math
# from typing import List, Dict, Tuple, Any, Optional

# # Haversine formula to calculate distance between two points (lat, lon) in kilometers
# def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
#     R = 6371.0  # Earth's radius in kilometers
#     lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
#     dlat = lat2 - lat1
#     dlon = lon2 - lon1
#     a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
#     c = 2 * math.asin(math.sqrt(a))
#     return R * c

# # Calculate travel time in minutes given distance (km) and speed (km/h)
# def calculate_travel_time(distance_km: float, speed_kmh: float = 30.0) -> float:
#     return (distance_km / speed_kmh) * 60  # Convert hours to minutes

# import json
# import os

# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# try:
#     with open(os.path.join(base_dir, 'data', 'nodes.json'), 'r') as f:
#         halte_data = json.load(f)
# except Exception:
#     halte_data = []

# try:
#     with open(os.path.join(base_dir, 'data', 'wisata.json'), 'r') as f:
#         wisata_data = json.load(f)
# except Exception:
#     wisata_data = []

# # Function to find the nearest tourist attraction to a given halte
# def find_nearest_wisata(halte: Dict[str, Any]) -> Tuple[Optional[str], Optional[str], float]:
#     min_distance = float('inf')
#     nearest_wisata = None
#     nearest_wisata_id = None
#     for wisata in wisata_data:
#         distance = haversine(halte["lat"], halte["lon"], wisata["lat"], wisata["lon"])
#         if distance < min_distance:
#             min_distance = distance
#             nearest_wisata = wisata["name"]
#             nearest_wisata_id = wisata["id"]
#     return nearest_wisata_id, nearest_wisata, min_distance

# # Calculate distances and times between specific stops
# def calculate_route(halte1_id: str, halte2_id: str) -> Dict[str, Any]:
#     halte1 = next((h for h in halte_data if h["id"] == halte1_id), None)
#     halte2 = next((h for h in halte_data if h["id"] == halte2_id), None)
#     if not halte1 or not halte2:
#         return {"error": "Halte not found"}
    
#     distance = haversine(halte1["lat"], halte1["lon"], halte2["lat"], halte2["lon"])
#     time = calculate_travel_time(distance)
#     common_routes = list(set(halte1["routes"]) & set(halte2["routes"]))
    
#     return {
#         "from": halte1["name"],
#         "to": halte2["name"],
#         "distance_km": distance,
#         "time_minutes": time,
#         "common_routes": common_routes if common_routes else ["No common route; may require transfer"]
#     }

# # Main function to process routes and recommendations
# def main():
#     # Specific route calculations
#     routes = [
#     ("H01", "H02"),  # K1
#     ("H02", "H03"),
#     ("H03", "H04"),
#     ("H04", "H05"),
#     ("H05", "H06"),
#     ("H06", "H07"),
#     ("H07", "H08"),
    
#     ("H01", "H11"),  # FD2
#     ("H11", "H24"),

#     ("H06", "H07"),  # FD8 (juga ada di K1)
#     ("H07", "H19"),
#     ("H19", "H24"),
#     ("H24", "H25"),
#     ("H25", "H27"),

#     ("H09", "H10"),  # K3
#     ("H10", "H11"),
#     ("H11", "H12"),
#     ("H12", "H13"),
#     ("H13", "H14"),
#     ("H14", "H15"),

#     ("H16", "H17"),  # K4
#     ("H17", "H18"),

#     ("H18", "H22"),  # K6
#     ("H22", "H23"),

#     ("H19", "H20"),  # K5
#     ("H20", "H21"),

#     ("H26", "H27"),  # FD9

#     ("H28", "H29"),  # FD10
# ]
    
#     print("Route Calculations:")
#     for halte1_id, halte2_id in routes:
#         result = calculate_route(halte1_id, halte2_id)
#         if "error" in result:
#             print(f"\nCould not calculate route between {halte1_id} and {halte2_id}: {result['error']}")
#             continue
#         print(f"\nFrom {result['from']} to {result['to']}:")
#         print(f"  Distance: {result['distance_km']:.2f} km")
#         print(f"  Estimated Time: {result['time_minutes']:.2f} minutes")
#         print(f"  Routes: {', '.join(result['common_routes'])}")
    
#     # Nearest tourist attractions for each halte
#     print("\nNearest Tourist Attractions for Each Halte:")
#     for halte in halte_data:
#         wisata_id, wisata_name, distance = find_nearest_wisata(halte)
#         print(f"Halte {halte['name']} ({halte['id']}):")
#         print(f"  Nearest Attraction: {wisata_name} ({wisata_id})")
#         print(f"  Distance: {distance:.2f} km")

# if __name__ == "__main__":
#     main()