from flask import Flask, render_template, request, jsonify
from rute.ai import BusRouteSystem # Mengintegrasikan ai.py

app = Flask(__name__)
bus_system = BusRouteSystem()

@app.route("/")
def home():
    # Mengirim data halte DAN data wisata ke frontend index.html
    return render_template('index.html', 
                           haltes=bus_system.halte_data, 
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
        for h_id in result["path"]:
            halte = bus_system.halte_dict[h_id]
            koordinat_path.append({
                "lat": halte["lat"],
                "lng": halte["lon"],
                "name": halte["name"]
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