import osmnx as ox
import json
import networkx as nx

# Define bbox
north, south, east, west = -7.3, -8.0, 111.1, 110.4

print("Downloading railway graph...")
try:
    G = ox.graph_from_bbox(bbox=(north, south, east, west), custom_filter='["railway"~"rail"]')
    print(f"Graph downloaded: {len(G.nodes)} nodes")
    
    # Save graph coordinates
    nodes_data = {}
    for node, data in G.nodes(data=True):
        nodes_data[node] = (data['y'], data['x'])
    
    with open('data/rail_nodes.json', 'w') as f:
        json.dump(nodes_data, f)
except Exception as e:
    print(f"Error: {e}")

