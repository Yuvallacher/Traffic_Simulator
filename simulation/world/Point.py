class Point:
    def __init__(self, x : float, y : float):
        self.x = x
        self.y = y
        self.taken = False
        
    def isTaken(self):
        return self.taken
    
    def takePoint(self):
        self.taken = True
    
    def releasePoint(self):
        self.taken = False