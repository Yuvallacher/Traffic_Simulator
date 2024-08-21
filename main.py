import pygame
from simulation.vehicle.Vehicle import Vehicle
from simulation.world.road import Road
from simulation.world.road import RoadBuilder
from simulation.world.World import World
from simulation.manager.vehicles_manager import VehiclesManager
from drawings.vehicle_drawer import VehicleDrawer
from simulation.data.DataManager import DataManager
from simulation.data.Accident import AccidentManager
from simulation.world.junction import JunctionBuilder

roads = RoadBuilder.create_road("junction", 0)
#roads = RoadBuilder.create_road("straight", 2)


# junction = JunctionBuilder.create_junction_from_file('junction_road')
# junctionDicts = RoadBuilder.read_junctions_from_json()
#world creation
simulationWorld = World(roads)
simulationRunning = True

# def updateCarPos(vehicles: list[Vehicle], simulationWorld : World, dataManager : DataManager, road : Road): #TODO probably move to a different place
#     for vehicle in vehicles:
#         vehicle.drive(vehicles, simulationWorld, dataManager, road)

def updateCarPos(vehicles: list[Vehicle], simulationWorld : World, dataManager : DataManager): #TODO probably move to a different place
    for vehicle in vehicles:
        vehicleRoad = simulationWorld.get_vehicle_road(vehicle.roadIndex)
        vehicle.drive(vehicles, simulationWorld, dataManager, accidentManager, vehicleRoad)

screen = pygame.display.set_mode((simulationWorld.SCREEN_WIDTH, simulationWorld.SCREEN_HEIGHT))
vehiclesManager = VehiclesManager(simulationWorld.NUMBER_OF_CARS)

#clock
clock = pygame.time.Clock()

#dataManager
dataManager = DataManager(filename='simulation_data.xlsx', export_interval=2)
next_stat_update = pygame.time.get_ticks() + dataManager.export_interval * 1000  # Convert seconds to milliseconds
accidentManager =  AccidentManager()

while simulationRunning:
    screen.fill(simulationWorld.WHITE)
    #screen.blit(roads[0].laneImages[roads[0].currNumOfLanes * 2 - 1], roads[0].imagesPositions[roads[0].currNumOfLanes * 2 - 1]) #TODO renove this late, this is for testing only
    screen.blit(pygame.image.load("roadPictures\\junctionRoad.png"),[0, 10])
    # vehiclesManager.add_vehicles(road.allLanesInRoad, simulationWorld)
    vehiclesManager.add_vehicles(simulationWorld, screen)
    updateCarPos(vehiclesManager.vehicles, simulationWorld, dataManager)
    VehicleDrawer.draw_vehicles(vehiclesManager.vehicles, screen)
    #vehiclesManager.remove_vehicles(road.allLanesInRoad)
    vehiclesManager.remove_vehicles(roads)

    current_time = pygame.time.get_ticks()
    if current_time >= next_stat_update:
        dataManager.update_stats(vehiclesManager.vehicles)
        next_stat_update = current_time + dataManager.export_interval * 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationRunning = False

    delete = [key for key in accidentManager.allAccidents.keys() if accidentManager.allAccidents[key].check_if_3_seconds_elapsed()]
    for key in delete:
        accidentManager.allAccidents[key].remove_accident(vehiclesManager.vehicles)
        del accidentManager.allAccidents[key]
    # for accidentID in accidentManager.allAccidents.keys():
    #     if accidentManager.allAccidents[accidentID].check_if_3_seconds_elapsed():
    #         accidentManager.allAccidents[accidentID].remove_accident(vehiclesManager.vehicles)
    #         del accidentManager.allAccidents[accidentID]

    pygame.display.update()
    clock.tick(simulationWorld.FPS)

pygame.quit()