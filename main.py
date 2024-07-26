import pygame
from simulation.vehicle.Vehicle import Vehicle
from simulation.world.road import Road
from simulation.world.road import RoadBuilder
from simulation.world.World import World
from simulation.manager.vehicles_manager import VehiclesManager
from drawings.vehicle_drawer import VehicleDrawer
from simulation.data.DataManager import DataManager

#roads 
#road = Road(Point(0, 300), Point(SCREEN_WIDTH, 300), NUMBER_OF_LANES, LANE_SIZE)
road = RoadBuilder.create_road("straight", 2)

#world creation
simulationWorld = World(road)
simulationRunning = True

def updateCarPos(vehicles: list[Vehicle], simulationWorld : World, dataManager : DataManager): #TODO probably move to a different place
    for vehicle in vehicles:
        vehicle.accelerateAndBreak(vehicles, simulationWorld, dataManager, road)
    

screen = pygame.display.set_mode((simulationWorld.SCREEN_WIDTH, simulationWorld.SCREEN_HEIGHT))
vehiclesManager = VehiclesManager(simulationWorld.NUMBER_OF_CARS)

#clock
clock = pygame.time.Clock()

#dataManager
dataManager = DataManager(filename='simulation_data.xlsx', export_interval=2)
next_stat_update = pygame.time.get_ticks() + dataManager.export_interval * 1000  # Convert seconds to milliseconds


while simulationRunning:
    screen.fill(simulationWorld.WHITE)
    screen.blit(road.laneImages[road.currNumOfLanes * 2 - 1], road.imagesPositions[road.currNumOfLanes * 2 - 1]) #TODO renove this late, this is for testing only
    
    vehiclesManager.add_vehicles(road.allLanesInRoad, simulationWorld) #TODO check why this doesnt work
    updateCarPos(vehiclesManager.vehicles, simulationWorld, dataManager)
    VehicleDrawer.draw_vehicles(vehiclesManager.vehicles, screen)
    vehiclesManager.remove_vehicles(road.allLanesInRoad)

    current_time = pygame.time.get_ticks()
    if current_time >= next_stat_update:
        dataManager.update_stats(vehiclesManager.vehicles)
        next_stat_update = current_time + dataManager.export_interval * 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False

    pygame.display.update()
    clock.tick(simulationWorld.FPS)

pygame.quit()