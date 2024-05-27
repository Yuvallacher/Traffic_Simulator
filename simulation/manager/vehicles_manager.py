from vehicle.Vehicle import Vehicle

class VehiclesManager:
    
    def __init__(self) -> None:
        self.cars = []

    def add_car(self, vehicle : Vehicle):
        self.cars.append(vehicle)
