import os
from dotenv import load_dotenv
load_dotenv('/home/pirate/docker/synapse-ia/.env')
from tools.select_bunny_proposal import BunnySelector
s = BunnySelector()
print(f'Registry Path: {s.registry_path}')
s.load_data()
for i in range(5):
    cand = s.select_candidate()
    if cand:
        print(f'Candidate {i}: {cand[1]["name"]} - {cand[1]["status"]}')
    else:
        print(f'Candidate {i}: None')
