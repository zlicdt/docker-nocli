import docker

class dockerutils:
    client = None
    def __init__(self):
        self.client = docker.client.from_env()
    
    def info(self):
        return self.client.info()

    def version(self):
        return self.client.version()
    
    # TODO Complete this
    def containers_list(self):
        return self.client.containers.list()
    
