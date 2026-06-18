import json
import subprocess

def get_json_from_git(stage, git_path):
    try:
        content = subprocess.check_output(['git', 'show', f':{stage}:{git_path}'])
        return json.loads(content)
    except Exception as e:
        print(f"Error loading {git_path} stage {stage}: {e}")
        return []

def resolve(local_path, git_path, key="id"):
    ours = get_json_from_git(2, git_path)
    theirs = get_json_from_git(3, git_path)
    
    merged = {item[key]: item for item in ours}
    for item in theirs:
        if item[key] not in merged:
            merged[item[key]] = item
        else:
            if 'routes' in item and 'routes' in merged[item[key]]:
                merged_routes = set(merged[item[key]]['routes']) | set(item['routes'])
                merged[item[key]]['routes'] = list(merged_routes)
                
    with open(local_path, 'w') as f:
        json.dump(list(merged.values()), f, indent=4)
    
    subprocess.check_call(['git', 'add', local_path])
    print(f"Resolved {local_path}")

resolve('data/nodes.json', 'ProjectAI_Navigasi-Wisata-Soloraya-Integrasi-Transum/data/nodes.json')
resolve('data/routes.json', 'ProjectAI_Navigasi-Wisata-Soloraya-Integrasi-Transum/data/routes.json')
