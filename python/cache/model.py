class CacheModel():
    def __init__(self):
        self.memory = {}
    
    def reset(self):
        self.memory = {}

    def read(self, address):
        if address in self.memory.keys():
            return self.memory[address]
        else:
            # TODO: Fix memory values
            return address

    def write(self, address, data):
        self.memory[address] = data
