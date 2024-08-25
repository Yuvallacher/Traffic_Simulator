from simulation.vehicle.vehicles_manager import VehiclesManager
from simulation.data.DataManager import DataManager
from drawings.vehicle_drawer import VehicleDrawer
from simulation.world.hazard import Hazard
from simulation.world.World import World
import pygame
import sys

simulationWorld = World("junction", 1)
simulationWorld.set_vehicles_manager(VehiclesManager(simulationWorld.NUMBER_OF_CARS))
dataManager = DataManager(filename='simulation_data.xlsx', export_interval=2)
next_stat_update = pygame.time.get_ticks() + dataManager.export_interval * 1000
speedLimit = Hazard("speedLimit", [185, 405], 1, 0, ["pictures\\hazardsPictures\\speed_limit.png"], {"limit": 30},1)
stopSign = Hazard("stopSign", [647, 510], 2, 0, ["pictures\\hazardsPictures\\stop.jpg"], {}, 2)
simulationWorld.add_hazard(speedLimit)
simulationWorld.add_hazard(stopSign)

while simulationWorld.simulationRunning:
    # simulationWorld.screen.fill(simulationWorld.WHITE)
    simulationWorld.screen.blit(simulationWorld.roads[0].laneImages[simulationWorld.roads[0].currNumOfLanes - 1], simulationWorld.roads[0].imagesPositions[simulationWorld.roads[0].currNumOfLanes - 1])

    simulationWorld.vehiclesManager.add_vehicles(simulationWorld, simulationWorld.screen)
    simulationWorld.vehiclesManager.updateCarPos(simulationWorld, dataManager, simulationWorld.accidentManager)
    VehicleDrawer.draw_vehicles(simulationWorld.vehiclesManager.vehicles, simulationWorld.screen)
    simulationWorld.vehiclesManager.remove_vehicles(simulationWorld.roads)

    simulationWorld.screen.blit(pygame.transform.scale(pygame.image.load(speedLimit.images[0]).convert(), (30,70)), speedLimit.location)
    simulationWorld.screen.blit(pygame.transform.scale(pygame.image.load(stopSign.images[0]).convert(), (30,70)), stopSign.location)
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
    simulationWorld.clock.tick(simulationWorld.FPS)

pygame.quit()
sys.exit()