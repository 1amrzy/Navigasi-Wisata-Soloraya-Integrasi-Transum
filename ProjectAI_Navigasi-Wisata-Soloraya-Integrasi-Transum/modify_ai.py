import sys

with open('rute/ai.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "class BusRouteSystem:" in line:
        new_lines.append(line)
        new_lines.append("    def __init__(self):\n")
        new_lines.append("        import json\n")
        new_lines.append("        import os\n")
        new_lines.append("        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n")
        new_lines.append("        with open(os.path.join(base_dir, 'data', 'nodes.json'), 'r') as f:\n")
        new_lines.append("            self.halte_data = json.load(f)\n")
        new_lines.append("        with open(os.path.join(base_dir, 'data', 'wisata.json'), 'r') as f:\n")
        new_lines.append("            self.wisata_data = json.load(f)\n")
        new_lines.append("        with open(os.path.join(base_dir, 'data', 'routes.json'), 'r') as f:\n")
        new_lines.append("            self.route_data = json.load(f)\n")
        new_lines.append("        \n")
        new_lines.append("        self.route_dict = {r['id']: r for r in self.route_data}\n")
        new_lines.append("        self.graph = self._build_graph()\n")
        new_lines.append("        self.halte_dict = {h['id']: h for h in self.halte_data}\n")
        skip = True
        continue
    
    if skip and "def _build_graph" in line:
        skip = False
        new_lines.append("\n")
    
    if not skip:
        new_lines.append(line)

with open('rute/ai.py', 'w') as f:
    f.writelines(new_lines)

print("Modification successful.")
