import json
import requests
import time

print("Memuat nodes dan rute...")
with open('data/nodes.json', 'r') as f:
    nodes = json.load(f)
with open('data/routes.json', 'r') as f:
    routes = json.load(f)

train_routes = [r for r in routes if r.get("hierarchy") == "TRAIN"]
station_dict = {n['id']: n for n in nodes if n['type'] == 'STASIUN'}
rail_segments = {}

print("Menghitung rute menggunakan BRouter Railway API...")
for route in train_routes:
    stops = route.get("stops", [])
    for i in range(len(stops) - 1):
        s1_id = stops[i]
        s2_id = stops[i+1]
        
        if s1_id not in station_dict or s2_id not in station_dict:
            continue
            
        pair_key = f"{s1_id}_{s2_id}"
        pair_key_rev = f"{s2_id}_{s1_id}"
        
        if pair_key in rail_segments:
            continue
            
        s1 = station_dict[s1_id]
        s2 = station_dict[s2_id]
        
        try:
            # Query BRouter for railway profile
            url = f"https://brouter.de/brouter?lonlats={s1['lon']},{s1['lat']}|{s2['lon']},{s2['lat']}&profile=rail&alternativeidx=0&format=geojson"
            res = requests.get(url, timeout=10)
            
            if res.status_code == 200:
                data = res.json()
                coords_list = data["features"][0]["geometry"]["coordinates"]
                # Convert [lon, lat] to {lat, lng}
                coords = [{"lat": pt[1], "lng": pt[0]} for pt in coords_list]
                
                rail_segments[pair_key] = coords
                rail_segments[pair_key_rev] = coords[::-1]
                print(f"Sukses BRouter: {s1['name']} -> {s2['name']} ({len(coords)} titik lengkung)")
            else:
                print(f"Gagal BRouter: {s1['name']} -> {s2['name']} (Status: {res.status_code})")
                
            # Beri jeda agar tidak di-rate-limit
            time.sleep(1)
            
        except Exception as e:
            print(f"Error pada {s1['name']} -> {s2['name']}: {e}")
            
with open('data/rail_segments.json', 'w') as f:
    json.dump(rail_segments, f, indent=4)
    
print("Berhasil menyusun data/rail_segments.json menggunakan BRouter!")
