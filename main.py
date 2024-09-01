from simulation.vehicle.vehicles_manager import VehiclesManager
from simulation.data.DataManager import DataManager
from drawings.vehicle_drawer import VehicleDrawer
from simulation.world.hazard import Hazard
from simulation.world.hazard import SpeedLimit
from simulation.world.hazard import StopSign
from simulation.world.World import World
from pygame.math import Vector2
import pygame
import sys

simulationWorld = World("junction", 1)
# simulationWorld = World("straight", 2)
simulationWorld.set_vehicles_manager(VehiclesManager(simulationWorld.NUMBER_OF_CARS))
dataManager = DataManager(filename='simulation_data.xlsx', export_interval=2)
next_stat_update = pygame.time.get_ticks() + dataManager.export_interval * 1000

speedLimit = SpeedLimit(Vector2([185, 405]), 1, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\speed_limit.png").convert_alpha(), (30, 70))], 30)
stopSign = StopSign(Vector2([670, 510]), 2, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
stopSign2 = StopSign(Vector2([670, 260]), 1, 1, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
simulationWorld.roads[2].update_road_and_direction_priority(1, 2, 0, 1)
simulationWorld.roads[1].update_road_and_direction_priority(0, 1, 0, 1)
simulationWorld.roads[1].update_road_and_direction_priority(0, 1, 1, 1)
simulationWorld.add_hazard(speedLimit)
simulationWorld.add_hazard(stopSign)
simulationWorld.add_hazard(stopSign2)

while simulationWorld.simulationRunning:
    simulationWorld.screen.fill(simulationWorld.WHITE)
    simulationWorld.screen.blit(simulationWorld.roads[0].laneImages[simulationWorld.roads[0].currNumOfLanes - 1], simulationWorld.roads[0].imagesPositions[simulationWorld.roads[0].currNumOfLanes - 1])

    simulationWorld.vehiclesManager.add_vehicles(simulationWorld, simulationWorld.screen)
    simulationWorld.vehiclesManager.updateCarPos(simulationWorld, dataManager, simulationWorld.accidentManager)
    VehicleDrawer.draw_vehicles(simulationWorld.vehiclesManager.vehicles, simulationWorld.screen)
    simulationWorld.vehiclesManager.remove_vehicles(simulationWorld.roads)

    simulationWorld.screen.blit(speedLimit.images[0], speedLimit.location)
    simulationWorld.screen.blit(stopSign.images[0], stopSign.location)
    simulationWorld.screen.blit(stopSign2.images[0], stopSign2.location)
    # simulationWorld.screen.blit(pygame.transform.scale(pygame.image.load(speedLimit.images[0]).convert(), (30,70)), speedLimit.location)
    # simulationWorld.screen.blit(pygame.transform.scale(pygame.image.load(stopSign.images[0]).convert(), (30,70)), stopSign.location)
    current_time = pygame.time.get_ticks()
    if current_time >= next_stat_update:
        dataManager.update_stats(simulationWorld.vehiclesManager.vehicles)
        next_stat_update = current_time + dataManager.export_interval * 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            simulationWorld.simulationRunning = False

    delete = [key for key in simulationWorld.accidentManager.allAccidents.keys() if simulationWorld.accidentManager.allAccidents[key].check_if_3_seconds_elapsed()]
    for key in delete:
        simulationWorld.accidentManager.allAccidents[key].remove_accident(simulationWorld.vehiclesManager.vehicles)
        del simulationWorld.accidentManager.allAccidents[key]
    
    pygame.display.update()
    # pygame.display.flip()
    simulationWorld.clock.tick(simulationWorld.FPS)

pygame.quit()
sys.exit()