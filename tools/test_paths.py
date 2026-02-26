import os
from dotenv import load_dotenv
load_dotenv()
base_path = os.environ.get("BASE_PATH")
registry_path = os.path.join(base_path, "context/data/bunny_registry.json")
print(f"BASE_PATH: {base_path}")
print(f"Registry Path: {registry_path}")
print(f"File exists: {os.path.exists(registry_path)}")
