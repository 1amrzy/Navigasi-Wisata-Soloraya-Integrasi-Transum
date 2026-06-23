# pyrefly: ignore [missing-import]
import json
import os
from flask import Flask, render_template, request, jsonify
from rute.ai import BusRouteSystem # Mengintegrasikan ai.py

app = Flask(__name__)
bus_system = BusRouteSystem()

# Load rail segments pre-calculated data
try:
    with open(os.path.join(os.path.dirname(__file__), 'data', 'rail_segments.json'), 'r') as f:
        rail_segments = json.load(f)
except Exception:
    rail_segments = {}

@app.route("/")
def home():
    # Mengirim data halte DAN data wisata ke frontend index.html
    # Filter out WISATA from haltes to prevent duplicates in the Start dropdown
    pure_haltes = [h for h in bus_system.halte_data if h.get("type") != "WISATA"]
    return render_template('index.html', 
                           haltes=pure_haltes, 
                           wisatas=bus_system.wisata_data)

@app.route("/api/cari_rute_wisata", methods=["POST"])
def cari_rute_wisata():
    data = request.get_json()
    start_id = data.get("start_id")
    wisata_name = data.get("wisata_name")
    
    # Menjalankan algoritma A* khusus rute wisata dari ai.py
    result = bus_system.get_route_to_attraction(start_id, wisata_name)
    
    if result:
        # Menyiapkan koordinat rute bus (Halte ke Halte)
        koordinat_path = []
        for i, h_id in enumerate(result["path"]):
            halte = bus_system.halte_dict[h_id]
            mode = "WALK"
            route_id = "WALK"
            if i < len(result["routes"]):
                route_id = result["routes"][i]
                route_info = bus_system.route_dict.get(route_id, {})
                mode = route_info.get("hierarchy", "LOCAL")
                
            prev_mode = "WALK"
            if i > 0:
                prev_route_id = result["routes"][i-1]
                prev_mode = bus_system.route_dict.get(prev_route_id, {}).get("hierarchy", "LOCAL")
                
            # Determine the coordinate to use for the station
            use_lat = halte["lat"]
            use_lon = halte["lon"]
            
            # Snap to rail segments to avoid zigzags
            if mode == "TRAIN" and i < len(result["path"]) - 1:
                next_h_id = result["path"][i+1]
                pair_key = f"{h_id}_{next_h_id}"
                if pair_key in rail_segments and len(rail_segments[pair_key]) > 0:
                    use_lat = rail_segments[pair_key][0]["lat"]
                    use_lon = rail_segments[pair_key][0]["lng"]
            elif prev_mode == "TRAIN" and i > 0:
                prev_h_id = result["path"][i-1]
                pair_key = f"{prev_h_id}_{h_id}"
                if pair_key in rail_segments and len(rail_segments[pair_key]) > 0:
                    use_lat = rail_segments[pair_key][-1]["lat"]
                    use_lon = rail_segments[pair_key][-1]["lng"]
                
            koordinat_path.append({
                "lat": use_lat,
                "lng": use_lon,
                "name": halte["name"],
                "route": route_id,
                "mode": mode,
                "is_intermediate": False
            })
            
            # Inject intermediate points for train
            if mode == "TRAIN" and i < len(result["path"]) - 1:
                next_h_id = result["path"][i+1]
                pair_key = f"{h_id}_{next_h_id}"
                if pair_key in rail_segments:
                    # Exclude the exact start and end coordinate to prevent duplicates
                    for pt in rail_segments[pair_key][1:-1]:
                        koordinat_path.append({
                            "lat": pt["lat"],
                            "lng": pt["lng"],
                            "name": halte["name"] + " (Jalur)",
                            "route": route_id,
                            "mode": mode,
                            "is_intermediate": True
                        })
        
        result["koordinat_path"] = koordinat_path
        result["analisis"] = bus_system.get_route_analysis(result)
        
        # Mengambil koordinat spesifik tempat wisata tujuan
        wisata_info = next((w for w in bus_system.wisata_data if w["name"] == wisata_name), None)
        if wisata_info:
            result["koordinat_wisata"] = {
                "lat": wisata_info["lat"], 
                "lng": wisata_info["lon"], 
                "name": wisata_info["name"]
            }
            
        return jsonify({"status": "success", "result": result})
    
    return jsonify({"status": "error", "message": "Rute ke tempat wisata tersebut tidak ditemukan!"})

if __name__ == "__main__":
    app.run(debug=True)