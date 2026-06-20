import json
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    nodes_file = os.path.join(base_dir, 'nodes.json')

    with open(nodes_file, 'r', encoding='utf-8') as f:
        nodes = json.load(f)

    for node in nodes:
        routes = node.get('routes', [])
        new_routes = []
        for r in routes:
            if r == 'SW':
                new_routes.append('WS')
            elif r == 'WS':
                new_routes.append('SW')
            else:
                new_routes.append(r)
        
        # Deduplicate and update
        node['routes'] = list(dict.fromkeys(new_routes))

    with open(nodes_file, 'w', encoding='utf-8') as f:
        json.dump(nodes, f, indent=4)

    print("Berhasil menukar arah rute SW dan WS!")

if __name__ == "__main__":
    main()
