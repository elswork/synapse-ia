import docker
try:
    client = docker.from_env()
    print(client.containers.list())
except Exception as e:
    print(f"Error: {e}")
