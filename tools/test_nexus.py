import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
try:
    from nexus_sync import NexusSync
    n = NexusSync()
    print("Importado NexusSync con éxito")
    n.log_event('TEST_AGENT', 'TEST_EVENT', 'Testing keyword argument', log_to_md=False)
    print("Llamada a log_event exitosa")
except Exception as e:
    print(f"ERROR: {e}")
