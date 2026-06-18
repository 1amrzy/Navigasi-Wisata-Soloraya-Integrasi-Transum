import re

with open('templates/index.html', 'r') as f:
    content = f.read()

new_func = """        async function gambarPeta(result) {
            routeLayer.clearLayers();
            const pathData = result.koordinat_path;
            const latlngs = [];

            // 1. Gambar Marker & Kumpulkan Koordinat
            pathData.forEach((pt) => {
                latlngs.push([pt.lat, pt.lng]);
                let popupText = `<b>${pt.name}</b><br>Halte/Stasiun`;
                if (pt.mode === "TRAIN") popupText = `<b>${pt.name}</b><br>Stasiun Kereta`;
                L.marker([pt.lat, pt.lng]).addTo(routeLayer).bindPopup(popupText);
            });

            // 2. Pecah path menjadi segmen berdasarkan mode transportasi
            let segments = [];
            let currentSegment = [];
            let currentMode = null;

            for (let i = 0; i < pathData.length; i++) {
                const pt = pathData[i];
                if (currentSegment.length === 0) {
                    currentSegment.push(pt);
                    currentMode = pt.mode;
                } else {
                    currentSegment.push(pt);
                    if (pt.mode !== currentMode) {
                        segments.push({ mode: currentMode, points: currentSegment });
                        currentSegment = [pt];
                        currentMode = pt.mode;
                    }
                }
            }
            if (currentSegment.length > 1) {
                segments.push({ mode: currentMode, points: currentSegment });
            }

            // 3. Render tiap segmen
            for (const seg of segments) {
                if (seg.points.length < 2) continue;
                
                const coords = seg.points;
                
                if (seg.mode === "TRAIN") {
                    // Kereta Api: Garis lurus biru tua
                    L.polyline(coords.map(pt => [pt.lat, pt.lng]), { color: '#0055a4', weight: 6, opacity: 0.9 }).addTo(routeLayer);
                } else if (seg.mode === "WALK") {
                    // Jalan Kaki antar halte: Garis putus-putus abu-abu
                    L.polyline(coords.map(pt => [pt.lat, pt.lng]), { color: '#888888', weight: 4, dashArray: '5, 10' }).addTo(routeLayer);
                } else {
                    // Bus (LOCAL / INTER_REGIONAL): OSRM Driving Oranye
                    const coordsStr = coords.map(pt => `${pt.lng},${pt.lat}`).join(';');
                    const osrmUrl = `https://router.project-osrm.org/route/v1/driving/${coordsStr}?overview=full&geometries=geojson`;
                    try {
                        const response = await fetch(osrmUrl);
                        const data = await response.json();
                        if (data.routes && data.routes.length > 0) {
                            L.geoJSON(data.routes[0].geometry, { style: { color: '#f78837', weight: 5, opacity: 0.8 } }).addTo(routeLayer);
                        } else {
                            L.polyline(coords.map(pt => [pt.lat, pt.lng]), { color: '#f78837', weight: 5, opacity: 0.8 }).addTo(routeLayer);
                        }
                    } catch (e) {
                        L.polyline(coords.map(pt => [pt.lat, pt.lng]), { color: '#f78837', weight: 5, opacity: 0.8 }).addTo(routeLayer);
                    }
                }
            }

            // 4. Rute Jalan kaki ke Tempat Wisata
            if(result.koordinat_wisata) {
                const wisata = result.koordinat_wisata;
                const halteTerakhir = pathData[pathData.length - 1];
                latlngs.push([wisata.lat, wisata.lng]);

                L.circleMarker([wisata.lat, wisata.lng], {
                    color: '#075056', fillColor: '#075056', fillOpacity: 1, radius: 8
                }).addTo(routeLayer).bindPopup(`<b>${wisata.name}</b><br>Tujuan Wisata`);

                L.polyline([[halteTerakhir.lat, halteTerakhir.lng], [wisata.lat, wisata.lng]], { 
                    color: '#075056', weight: 4, dashArray: '5, 10' 
                }).addTo(routeLayer);
            }

            if (latlngs.length > 0) {
                const bounds = L.latLngBounds(latlngs);
                map.fitBounds(bounds, { padding: [50, 50] });
            }
        }"""

content = re.sub(r'        async function gambarPeta\(result\) \{.*?(?=</script>)', new_func + '\n    ', content, flags=re.DOTALL)

with open('templates/index.html', 'w') as f:
    f.write(content)

print("SUCCESS")
