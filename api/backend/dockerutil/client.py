import docker

def get_client() -> docker.DockerClient:
    # I think this try-catch is useless because we already have deploy check
    try:
        client = docker.client.from_env()
        return client
    except:
        return None