import time



class Accident:
    def __init__(self, accidentID : int):
        self.id = accidentID
        self.vehicles = []
        self.timeOfAccident = time.time()
        
    def check_if_3_seconds_elapsed(self) -> bool:
        return (time.time() - self.timeOfAccident) >= 3
    
    def remove_accident(self, allVehicles : list):
        for vehicle in self.vehicles:
            allVehicles.remove(vehicle)
            
            

class AccidentManager:
    def __init__(self):
        self.allAccidents : dict[int, Accident] = dict()
        self.numberOfAccidents = 0
        
    def add_accident(self) -> Accident:
        self.numberOfAccidents += 1
        newAccident = Accident(self.numberOfAccidents)
        self.allAccidents[self.numberOfAccidents] = newAccident
        return newAccident
        