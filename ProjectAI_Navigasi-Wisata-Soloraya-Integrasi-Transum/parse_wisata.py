import json

data_text = """W01	Solo Safari	-7.564.391.741	1.108.586.613
W02	Danau UNS	-7.561.172.246	1.108.581.931
W03	Benteng Vastenburg	-7.571.804.006	1.108.307.858
W04	Kampung Wisata Batik Kauman	-7.573.215.566	1.108.263.633
W05	Pasar Triwindu	-7.568.984.669	1.108.225.384
W06	Taman Sriwedari	-7.568.224.905	1.108.129.629
W07	De Tjolomadoe	-7.533.922.576	1.107.498.663
W08	Lapangan Makamhaji	-75.691.203	1.107.831.005
W09	Balaikota Surakarta	-7.569.192.352	1.108.296.584
W10	Pasar Gede	-7.569.143.893	1.108.314.553
W11	Solo Techno Park	-7.555.835.181	1.108.538.009
W12	Taman Cerdas	-7.553.839.457	1.108.534.741
W13	Taman Lansia	-755.669.203	1.108.607.455
W14	Stadion Manahan	-7.555.259.829	1.108.065.227
W15	Taman Tirtonadi	-7.551.283.848	1.108.204.733
W16	Tumurun Private Museum	-7.570.257.605	1.108.164.116
W17	Ngarsopuro Night Market	-7.568.494.751	110.822.291
W18	Taman Balikota Solo	-7.569.219.287	1.108.298.679
W19	Museum Radya Pustaka	-7.568.292.105	1.108.144.969
W20	Pasar Malangjiwan Colomadu	-7.531.636.047	1.107.472.482
W21	Museum Keris Nusantara	-7.568.754.681	1.108.107.542
W22	Loji Gandrung	-7.566.305.927	1.108.095.326
W23	Gedung Wayang Orang Dance Theatre	-756.905.024	110.812.558
W24	House of Danar Hadi	-7.568.506.445	1.108.162.107
W25	Taman Punggawan Ngesus	-7.564.517.132	110.818.271
W26	Pura Mangkunegaran	-7.566.613.944	1.108.228.758
W27	Pasar Klewer	-7.575.178.766	1.108.267.555
W28	Taman Sunan Jogo Kali	-7.569.809.858	1.108.581.447
W29	Grojogan Sewu	-7.660.386	111.130.083
W30	Umbul Ponggok	-7.613.858	110.635.800
W31	Waduk Gajah Mungkur	-7.839.830	110.924.189
W32	Museum Sangiran	-7.399.997	110.809.830
W33	Masjid Agung Surakarta	-75.746,00	1.108.263
W34	Alun-Alun Utara Surakarta	-75.739,00	1.108.277
W35	Lokananta Recording Studio	-75.615,00	1.107.937
W36	Taman Budaya Jawa Tengah (TBJT)	-75.583,00	1.108.415
W37	Monumen 45 Banjarsari (Monjari)	-75.617,00	1.108.213
W38	Pasar Burung dan Ikan Hias Depok	-75.564,00	1.108.093
W39	Kampung Blangkon Serengan	-75.819,00	1.108.172
W40	Museum Samanhoedi	-75.684,00	1.107.963
W41	Taman Jayawijaya Mojosongo	-75.412,00	1.108.354
W42	Edupark UMS	-75.559,00	1.107.681
W43	Petilasan Keraton Kartasura	-75.529,00	1.107.381
W44	Pandawa Water World	-76.006,00	1.108.118
W45	Sentra Kerajinan Gitar Baki	-76.186,00	1.107.854
W46	Candi Plaosan	-77.404,00	1.105.045
W47	Pabrik Gula Gondang Winangoen	-77.317,00	1.105.516
W48	Rawa Jombor	-77.562,00	1.106.241
W49	Candi Sewu	-77.439,00	1.104.928
W50	Alun-Alun Karanganyar	-75.954,00	1.109.482
W51	Taman Pancasila	-75.947,00	1.109.427
W52	Simpang Lima Boyolali (Patung Kuda)	-75.306,00	1.105.961"""

wisata_path = 'data/wisata.json'
with open(wisata_path, 'r') as f:
    wisata = json.load(f)

# Clear existing to replace with this new master list or just merge?
# Since the user provides W01-W52, it's better to recreate the entire file or update matches
wisata_dict = {w["id"]: w for w in wisata}

for line in data_text.split('\n'):
    if not line.strip():
        continue
    parts = line.split('\t')
    if len(parts) >= 4:
        wid = parts[0].strip()
        name = parts[1].strip()
        lat_raw = parts[2].strip()
        lon_raw = parts[3].strip()
        
        # fix format
        lat_clean = lat_raw.replace('.', '').replace(',', '')
        # lat in Solo is ~ -7.xxxx. Wait, if lat_clean is -7564391741, we need -7.564391741
        # It always starts with '-7'. Wait, what about -76, -77?
        # Actually it's -7.56..., so insert dot after the second character (e.g. after '-7')
        if lat_clean.startswith('-7'):
            lat = f"-7.{lat_clean[2:]}"
        else:
            # Fallback
            lat = lat_raw
            
        lon_clean = lon_raw.replace('.', '').replace(',', '')
        # lon in Solo is ~ 110.xxxx or 111.xxxx
        if lon_clean.startswith('110'):
            lon = f"110.{lon_clean[3:]}"
        elif lon_clean.startswith('111'):
            lon = f"111.{lon_clean[3:]}"
        elif lon_clean.startswith('11'): # like 110822291 but written as 1.108... -> clean is 110822291
            if len(lon_clean) >= 3 and lon_clean[:3] in ('110', '111'):
                lon = f"{lon_clean[:3]}.{lon_clean[3:]}"
            else:
                lon = lon_raw
        else:
            lon = lon_raw
            
        # specifically fix "1.108.586.613" -> clean is "1108586613" -> "110.8586613"
        if lon_clean.startswith('1108'):
            lon = f"110.{lon_clean[3:]}"
        if lon_clean.startswith('1107'):
            lon = f"110.{lon_clean[3:]}"
        if lon_clean.startswith('1106'):
            lon = f"110.{lon_clean[3:]}"
        if lon_clean.startswith('1105'):
            lon = f"110.{lon_clean[3:]}"
        if lon_clean.startswith('1109'):
            lon = f"110.{lon_clean[3:]}"
        if lon_clean.startswith('1111'):
            lon = f"111.{lon_clean[3:]}"
            
        wisata_dict[wid] = {
            "id": wid,
            "name": name,
            "lat": float(lat),
            "lon": float(lon)
        }

with open(wisata_path, 'w') as f:
    json.dump(list(wisata_dict.values()), f, indent=4)

print("Added wisata to wisata.json")
