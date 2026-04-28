import os
import sys
sys.path.append("/home/pirate/docker/synapse-ia")
from tools.select_donut_proposal import DonutSelector

selector = DonutSelector()
try:
    proposal = selector.generate_proposal()
    print("PROPOSAL:", proposal)
except Exception as e:
    print("ERROR:", e)
