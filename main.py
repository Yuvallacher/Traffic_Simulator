from simulation.manager.vehicles_manager import VehiclesManager
from simulation.data.Accident import AccidentManager
from simulation.data.DataManager import DataManager
from drawings.vehicle_drawer import VehicleDrawer
from simulation.world.road import RoadBuilder
from simulation.world.World import World
import pygame
import sys

roads = RoadBuilder.create_road("junction", 1)
# roads = RoadBuilder.create_road("straight", 2)

#world creation
simulationWorld = World(roads)
simulationRunning = True

screen = pygame.display.set_mode((simulationWorld.SCREEN_WIDTH, simulationWorld.SCREEN_HEIGHT))
vehiclesManager = VehiclesManager(simulationWorld.NUMBER_OF_CARS)

#clock
clock = pygame.time.Clock()

#dataManager and AccidentManager
dataManager = DataManager(filename='simulation_data.xlsx', export_interval=2)
next_stat_update = pygame.time.get_ticks() + dataManager.export_interval * 1000  # Convert seconds to milliseconds
accidentManager =  AccidentManager()

while simulationRunning:
    screen.fill(simulationWorld.WHITE)
    screen.blit(roads[0].laneImages[roads[0].currNumOfLanes - 1], roads[0].imagesPositions[roads[0].currNumOfLanes - 1])
    vehiclesManager.add_vehicles(simulationWorld, screen)
    vehiclesManager.updateCarPos(simulationWorld, dataManager, accidentManager)
    VehicleDrawer.draw_vehicles(vehiclesManager.vehicles, screen)
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
    
    pygame.display.update()
    clock.tick(simulationWorld.FPS)
    
pygame.quit()
sys.exit()