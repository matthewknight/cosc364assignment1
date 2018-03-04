import sys
import json

class ripDemon(object):
    
    def __init__(self, filename):
        self.filename = filename
        
        

    def load_config(self):
        data = json.load(open(self.filename))
        routing_id = data["router-id"]
        input_ports = data["input-ports"]
        output_ports = data["outputs"]
        return routing_id, input_ports, output_ports



if __name__ == "__main__":
    config_file_name = sys.argv[1]    
    router = ripDemon(config_file_name)
    routing_id, input_ports, output_ports = router.load_config()
    print("Routing id: " + routing_id)
    print("Input ports: " + input_ports)
    print("Output ports: " + output_ports)
    
        
