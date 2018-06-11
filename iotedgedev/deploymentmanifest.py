import json

class DeploymentManifest:
    def __init__(self, path, is_template):
        self.path = path
        self.json = json.load(open(path))
        self.is_template = is_template

    def add_module_template(self, module_name):
        new_module = """{
            "version": "1.0",
            "type": "docker",
            "status": "running",
            "restartPolicy": "always",
            "settings": {
              "image": \"{MODULES.""" + module_name + """.amd64}\",
              "createOptions": ""
            }
        }"""

        self.json["moduleContent"]["$edgeAgent"]["properties.desired"]["modules"][module_name] = json.loads(new_module)

    def save(self):
        with open(self.path, "w") as deployment_manifest:
            json.dump(self.json, deployment_manifest, indent=2)
