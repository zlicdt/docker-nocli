import docker

def init() -> docker.DockerClient:
    return docker.client.from_env()