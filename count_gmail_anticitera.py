import json
import subprocess

GWS_BIN = "/home/pirate/docker/Arquimedes/bin/gws"

def run_gws(args):
    command = [GWS_BIN] + args + ["--format", "json"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error executing gws: {e}")
        return None

def count_messages(query):
    total_count = 0
    next_page_token = None
    
    while True:
        params = {"userId": "me", "q": query}
        if next_page_token:
            params["pageToken"] = next_page_token
            
        res = run_gws(["gmail", "users", "messages", "list", "--params", json.dumps(params)])
        
        if not res or 'messages' not in res:
            break
            
        total_count += len(res['messages'])
        next_page_token = res.get('nextPageToken')
        
        if not next_page_token:
            break
            
    return total_count

if __name__ == "__main__":
    query_anticitera = "from:me subject:Anticitera"
    query_antikythera = "from:me subject:Antikythera"
    
    print(f"Searching Gmail for Sant messages...")
    
    count_1 = count_messages(query_anticitera)
    count_2 = count_messages(query_antikythera)
    
    print(f"BREAKDOWN:")
    print(f"- Sent with 'Anticitera': {count_1}")
    print(f"- Sent with 'Antikythera': {count_2}")
    print(f"- Total unique sent (approx): {count_1 + count_2}") # Note: some might have both, but usually it's one or the other.
