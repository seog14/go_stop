class Flags: 
    
    def __init__(self):

        self.go = False 
        self.select_match = False 
    
    def serialize(self) -> dict:

        return self.__dict__

    @staticmethod
    def deserialize(data: dict):

        flags = Flags()
        flags.__dict__ = data

        return flags
        