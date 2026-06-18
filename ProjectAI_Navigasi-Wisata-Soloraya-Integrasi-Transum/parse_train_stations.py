import json

data_text = """Brambanan	BBN	Klaten	-7.751.685	110.499.092
Srowot	SWT	Klaten	-7.738.361	110.535.970
Klaten	KT	Klaten	-7.712.615	110.603.378
Ceper	CE	Klaten	-7.682.650	110.650.893
Delanggu	DL	Klaten	-7.632.008	110.686.522
Gawok	GW	Sukoharjo	-7.586.940	110.741.870
Purwosari	PWS	Surakarta	-7.561.638	110.796.695
Solo Balapan	SLO	Surakarta	-7.556.209	110.821.034
Solo Jebres	SK	Surakarta	-7.558.661	110.842.797
Palur	PL	Karanganyar	-7.574.676	110.867.906
Solo Kota	STA	Surakarta	-7.576.086	110.835.777
Sukoharjo	SKH	Sukoharjo	-7.674.987	110.836.515
Pasar Nguter	PNT	Sukoharjo	-7.735.955	110.855.018
Wonogiri	WNG	Wonogiri	-7.817.757	110.923.171
Bandara Adi Soemarmo	SMO	Boyolali	-7.514.937	110.756.653
Kadipiro	KDO	Surakarta	-7.539.308	110.817.540
Salem	SLM	Sragen	-7.387.123	110.825.122
Telawa	TW	Boyolali	-7.228.966	110.718.870
Sragen	SR	Sragen	-7.429.074	111.020.584"""

nodes_path = 'data/nodes.json'

with open(nodes_path, 'r') as f:
    nodes = json.load(f)

for line in data_text.split('\n'):
    if not line.strip():
        continue
    parts = line.split('\t')
    if len(parts) >= 5:
        nama = f"Stasiun {parts[0].strip()}"
        kode = parts[1].strip()
        kab = parts[2].strip()
        
        # fix format -7.751.685 -> -7.751685
        # logic: split by '.', keep first two parts separated by '.', join the rest without '.'
        def fix_coord(coord_str):
            c = coord_str.replace('.', '')
            # For lat, it starts with '-' and then digit. we want -7.XXXX
            # Actually since the original is -7.751.685
            # We can find the first dot. Wait, the first dot is correct. 
            # So just replace the SECOND dot onwards.
            # Example: -7.751.685 -> split by '.' -> ['-7', '751', '685']
            # Join [1:] -> '751685'
            # Combine: '-7.' + '751685'
            parts = coord_str.split('.')
            if len(parts) > 2:
                return f"{parts[0]}.{''.join(parts[1:])}"
            return coord_str
        
        lat = fix_coord(parts[3].strip())
        lon = fix_coord(parts[4].strip())
        
        # Check if already exists
        exists = False
        for n in nodes:
            if n['id'] == f"ST_{kode}":
                exists = True
                break
        
        if not exists:
            nodes.append({
                "id": f"ST_{kode}",
                "name": nama,
                "lat": float(lat),
                "lon": float(lon),
                "routes": [],
                "type": "STASIUN"
            })

with open(nodes_path, 'w') as f:
    json.dump(nodes, f, indent=4)

print("Added stations to nodes.json")
