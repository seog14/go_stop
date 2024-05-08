class Flags: 
    
    def __init__(self):

        self.go = False 
        self.select_match = False 
    
    def serialize(self) -> tuple:

        return tuple((
            self.go,
            self.select_match
        ))

    @staticmethod
    def deserialize(data: tuple):

        go = bool(data[0])
        select_match = bool(data[1])
        flags = Flags()
        flags.go = go 
        flags.select_match = select_match

        return flags
        