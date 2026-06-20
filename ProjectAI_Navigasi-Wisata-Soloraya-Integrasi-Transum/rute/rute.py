import math
from typing import List, Dict, Tuple

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

# Bus stops (halte) data
halte_data = [
    {"id": "H01", "name": "Jurug (Solo Safari)", "lat": -7.56513474408024, "lon": 110.858685876169, "routes": ["K1", "FD2"]},
    {"id": "H02", "name": "UNS", "lat": -7.56455236195493, "lon": 110.8561722718, "routes": ["K1"]},
    {"id": "H03", "name": "Vastenburg", "lat": -7.57175743180982, "lon": 110.8297470581, "routes": ["K1"]},
    {"id": "H04", "name": "Gladag", "lat": -7.57203341152584, "lon": 110.827739168751, "routes": ["K1"]},
    {"id": "H05", "name": "Pasar Pon Selatan", "lat": -7.57053451729552, "lon": 110.822770250784, "routes": ["K1"]},
    {"id": "H06", "name": "Sriwedari 1 Selatan", "lat": -7.56729936753916, "lon": 110.812057143543, "routes": ["K1", "FD8"]},
    {"id": "H07", "name": "Sriwedari 2 Selatan", "lat": -7.56795480396892, "lon": 110.814320671231, "routes": ["K1", "FD8"]},
    {"id": "H08", "name": "Colomadu Utara", "lat": -7.53253942382143, "lon": 110.748923594566, "routes": ["K1"]},
    {"id": "H09", "name": "Tugu Lilin", "lat": -7.567581219, "lon": 110.7835961, "routes": ["K3"]},
    {"id": "H10", "name": "Vestenburg (Kantor Pos)", "lat": -7.57140133360988, "lon": 110.829647652826, "routes": ["K3"]},
    {"id": "H11", "name": "Balai Kota", "lat": -7.56993057310902, "lon": 110.830046989632, "routes": ["K3", "FD2"]},
    {"id": "H12", "name": "Pasar Gede", "lat": -7.5684698254206, "lon": 110.831727375632, "routes": ["K3"]},
    {"id": "H13", "name": "Solo Techno Park", "lat": -7.55653679470118, "lon": 110.852209973442, "routes": ["K3"]},
    {"id": "H14", "name": "Kantor Kecamatan Jebres", "lat": -7.55541900174376, "lon": 110.854977935521, "routes": ["K3"]},
    {"id": "H15", "name": "Halte RS Jiwa / Taman Lansia", "lat": -7.55707042819373, "lon": 110.860610255225, "routes": ["K3"]},
    {"id": "H16", "name": "Halte Kecamatan Colomadu", "lat": -7.532634345, "lon": 110.7487969, "routes": ["K4"]},
    {"id": "H17", "name": "Stadion Manahan", "lat": -7.556663684, "lon": 110.8048193, "routes": ["K4"]},
    {"id": "H18", "name": "Terminal Tirtonadi", "lat": -7.551298569, "lon": 110.8182099, "routes": ["K4", "K6"]},
    {"id": "H19", "name": "Ngapeman", "lat": -7.568500872, "lon": 110.8166443, "routes": ["K5", "FD8"]},
    {"id": "H20", "name": "Sriwedari", "lat": -7.567047482, "lon": 110.8118452, "routes": ["K5"]},
    {"id": "H21", "name": "Landasan Udara (Pasar Colomadu)", "lat": -7.53171343, "lon": 110.7473448, "routes": ["K5", "FD7"]},
    {"id": "H22", "name": "Ngarsopuro", "lat": -7.569086355, "lon": 110.8221284, "routes": ["K6"]},
    {"id": "H23", "name": "Pasar Kembang", "lat": -7.571950677, "lon": 110.8166645, "routes": ["K6"]},
    {"id": "H24", "name": "Sriwedari 2 Utara", "lat": -7.567852615, "lon": 110.8146095, "routes": ["FD2", "FD8"]},
    {"id": "H25", "name": "Museum Keris B", "lat": -7.568829291, "lon": 110.8106188, "routes": ["FD8"]},
    {"id": "H26", "name": "Mangkunegaran", "lat": -7.567624751, "lon": 110.8220978, "routes": ["FD9"]},
    {"id": "H27", "name": "Sahid", "lat": -7.564166826, "lon": 110.8185673, "routes": ["FD8", "FD9"]},
    {"id": "H28", "name": "Pasar Klewer", "lat": -7.575037806, "lon": 110.8264383, "routes": ["FD10"]},
    {"id": "H29", "name": "Pasar Pucang Sawit A", "lat": -7.567996022, "lon": 110.8582507, "routes": ["FD10"]},
]

# Tourist attractions (wisata) data
wisata_data = [
    {"id": "W01", "name": "Solo Safari", "lat": -7.564391741, "lon": 110.8586613, "halte": ["H01"]},
    {"id": "W02", "name": "Danau UNS", "lat": -7.561172246, "lon": 110.8581931, "halte": ["H02"]},
    {"id": "W03", "name": "Benteng Vastenburg", "lat": -7.571804006, "lon": 110.8307858, "halte": ["H03"]},
    {"id": "W04", "name": "Kampung Wisata Batik Kauman", "lat": -7.573215566, "lon": 110.8263633, "halte": ["H04"]},
    {"id": "W05", "name": "Pasar Triwindu", "lat": -7.568984669, "lon": 110.8225384, "halte": ["H05"]},
    {"id": "W06", "name": "Taman Sriwedari", "lat": -7.568224905, "lon": 110.8129629, "halte": ["H06", "H07"]},
    {"id": "W07", "name": "De Tjolomadoe", "lat": -7.533922576, "lon": 110.7498663, "halte": ["H08"]},
    {"id": "W08", "name": "Lapangan Makamhaji", "lat": -7.5691203, "lon": 110.7831005, "halte": ["H09"]},
    {"id": "W09", "name": "Balaikota Surakarta", "lat": -7.569192352, "lon": 110.8296584, "halte": ["H11"]},
    {"id": "W10", "name": "Pasar Gede", "lat": -7.569143893, "lon": 110.8314553, "halte": ["H12"]},
    {"id": "W11", "name": "Solo Techno Park", "lat": -7.555835181, "lon": 110.8538009, "halte": ["H13"]},
    {"id": "W12", "name": "Taman Cerdas", "lat": -7.553839457, "lon": 110.8534741, "halte": ["H14"]},
    {"id": "W13", "name": "Taman Lansia", "lat": -7.55669203, "lon": 110.8607455, "halte": ["H15"]},
    {"id": "W14", "name": "Stadion Manahan", "lat": -7.555259829, "lon": 110.8065227, "halte": ["H17"]},
    {"id": "W15", "name": "Taman Tirtonadi", "lat": -7.551283848, "lon": 110.8204733, "halte": ["H18"]},
    {"id": "W16", "name": "Tumurun Private Museum", "lat": -7.570257605, "lon": 110.8164116, "halte": ["H23"]},
    {"id": "W17", "name": "Ngarsopuro Night Market", "lat": -7.568494751, "lon": 110.822291, "halte": ["H22"]},
    {"id": "W18", "name": "Taman Balikota Solo", "lat": -7.569219287, "lon": 110.8298679, "halte": ["H11"]},
    {"id": "W19", "name": "Museum Radya Pustaka", "lat": -7.568292105, "lon": 110.8144969, "halte": ["H24"]},
    {"id": "W20", "name": "Pasar Malangjiwan Colomadu", "lat": -7.531636047, "lon": 110.7472482, "halte": ["H21"]},
    {"id": "W21", "name": "Museum Keris Nusantara", "lat": -7.568754681, "lon": 110.8107542, "halte": ["H25"]},
    {"id": "W22", "name": "Loji Gandrung", "lat": -7.566305927, "lon": 110.8095326, "halte": ["H06"]},
    {"id": "W23", "name": "Gedung Wayang Orang Dance Theatre", "lat": -7.56905024, "lon": 110.812558, "halte": ["H24", "H07"]},
    {"id": "W24", "name": "House of Danar Hadi", "lat": -7.568506445, "lon": 110.8162107, "halte": ["H19"]},
    {"id": "W25", "name": "Taman Punggawan Ngesus", "lat": -7.564517132, "lon": 110.818271, "halte": ["H27"]},
    {"id": "W26", "name": "Pura Mangkunegaran", "lat": -7.566613944, "lon": 110.8228758, "halte": ["H26"]},
    {"id": "W27", "name": "Pasar Klewer", "lat": -7.575178766, "lon": 110.8267555, "halte": ["H28"]},
    {"id": "W28", "name": "Taman Sunan Jogo Kali", "lat": -7.569809858, "lon": 110.8581447, "halte": ["H29"]},
]

# Function to find the nearest tourist attraction to a given halte
def find_nearest_wisata(halte: Dict[str, any]) -> Tuple[str, str, float]:
    min_distance = float('inf')
    nearest_wisata = None
    nearest_wisata_id = None
    for wisata in wisata_data:
        distance = haversine(halte["lat"], halte["lon"], wisata["lat"], wisata["lon"])
        if distance < min_distance:
            min_distance = distance
            nearest_wisata = wisata["name"]
            nearest_wisata_id = wisata["id"]
    return nearest_wisata_id, nearest_wisata, min_distance

# Calculate distances and times between specific stops
def calculate_route(halte1_id: str, halte2_id: str) -> Dict[str, any]:
    halte1 = next((h for h in halte_data if h["id"] == halte1_id), None)
    halte2 = next((h for h in halte_data if h["id"] == halte2_id), None)
    if not halte1 or not halte2:
        return {"error": "Halte not found"}
    
    distance = haversine(halte1["lat"], halte1["lon"], halte2["lat"], halte2["lon"])
    time = calculate_travel_time(distance)
    common_routes = list(set(halte1["routes"]) & set(halte2["routes"]))
    
    return {
        "from": halte1["name"],
        "to": halte2["name"],
        "distance_km": distance,
        "time_minutes": time,
        "common_routes": common_routes if common_routes else ["No common route; may require transfer"]
    }

# Main function to process routes and recommendations
def main():
    # Specific route calculations
    routes = [
    ("H01", "H02"),  # K1
    ("H02", "H03"),
    ("H03", "H04"),
    ("H04", "H05"),
    ("H05", "H06"),
    ("H06", "H07"),
    ("H07", "H08"),
    
    ("H01", "H11"),  # FD2
    ("H11", "H24"),

    ("H06", "H07"),  # FD8 (juga ada di K1)
    ("H07", "H19"),
    ("H19", "H24"),
    ("H24", "H25"),
    ("H25", "H27"),

    ("H09", "H10"),  # K3
    ("H10", "H11"),
    ("H11", "H12"),
    ("H12", "H13"),
    ("H13", "H14"),
    ("H14", "H15"),

    ("H16", "H17"),  # K4
    ("H17", "H18"),

    ("H18", "H22"),  # K6
    ("H22", "H23"),

    ("H19", "H20"),  # K5
    ("H20", "H21"),

    ("H26", "H27"),  # FD9

    ("H28", "H29"),  # FD10
]
    
    print("Route Calculations:")
    for halte1_id, halte2_id in routes:
        result = calculate_route(halte1_id, halte2_id)
        print(f"\nFrom {result['from']} to {result['to']}:")
        print(f"  Distance: {result['distance_km']:.2f} km")
        print(f"  Estimated Time: {result['time_minutes']:.2f} minutes")
        print(f"  Routes: {', '.join(result['common_routes'])}")
    
    # Nearest tourist attractions for each halte
    print("\nNearest Tourist Attractions for Each Halte:")
    for halte in halte_data:
        wisata_id, wisata_name, distance = find_nearest_wisata(halte)
        print(f"Halte {halte['name']} ({halte['id']}):")
        print(f"  Nearest Attraction: {wisata_name} ({wisata_id})")
        print(f"  Distance: {distance:.2f} km")

if __name__ == "__main__":
    main()