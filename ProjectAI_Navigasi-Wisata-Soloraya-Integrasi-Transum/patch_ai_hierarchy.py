import re

with open('rute/ai.py', 'r') as f:
    content = f.read()

# 1. Update self.route_dict["WALK"] to ensure hierarchy is set
new_init = """        self.route_dict = {r['id']: r for r in self.route_data}
        self.route_dict["WALK"] = {"id": "WALK", "name": "Jalan Kaki", "speed_kmh": 5, "fare": 0, "hierarchy": "WALK"}
        self.hierarchy_levels = {
            "TRAIN": 1,
            "INTER_REGIONAL": 2,
            "LOCAL": 3,
            "WALK": 4
        }"""

content = re.sub(r'        self\.route_dict = \{r\[\'id\'\]: r for r in self\.route_data\}.*?self\.route_dict\["WALK"\].*?\}', new_init, content, flags=re.DOTALL)


# 2. In a_star, add penalty for upgrading hierarchy
# Search for where transfer penalty is added:
# "if current_route and route != current_route:"
# We will inject hierarchy check here.

target = """                transfer_penalty = 0
                if current_route and route != current_route:
                    transfer_penalty = 5  # 5 minutes transfer penalty"""

replacement = """                transfer_penalty = 0
                if current_route and route != current_route:
                    transfer_penalty = 5  # 5 minutes transfer penalty
                    
                    # Hierarchy penalty
                    curr_h = self.route_dict.get(current_route, {}).get("hierarchy", "LOCAL")
                    new_h = self.route_dict.get(route, {}).get("hierarchy", "LOCAL")
                    
                    curr_lvl = self.hierarchy_levels.get(curr_h, 3)
                    new_lvl = self.hierarchy_levels.get(new_h, 3)
                    
                    # Penalize going UP in hierarchy (e.g. LOCAL to TRAIN) unless we are walking
                    if current_route != "WALK" and new_lvl < curr_lvl:
                        transfer_penalty += 30  # HUGE penalty to discourage backward hierarchy"""

content = content.replace(target, replacement)

with open('rute/ai.py', 'w') as f:
    f.write(content)

print("SUCCESS")
