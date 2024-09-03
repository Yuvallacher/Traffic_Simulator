from simulation.data.DataManager import DataManager
from drawings.vehicle_drawer import VehicleDrawer
from simulation.world.hazard import SpeedLimit
from simulation.world.hazard import StopSign
from simulation.world.hazard import Hazard
from simulation.world.World import World
from simulation.simulationManager import SimulatorManager
from pygame.math import Vector2
from gui.inputBox import InputBox
from gui.button import Button
import pygame
import sys

# # =============== old version =============== #
# simulationWorld = World("junction", 1)
# # simulationWorld = World("straight", 2)
# simulationWorld.set_vehicles_manager(VehiclesManager(simulationWorld.NUMBER_OF_CARS))
# dataManager = DataManager(filename='simulation_data.xlsx', export_interval=2)
# next_stat_update = pygame.time.get_ticks() + dataManager.export_interval * 1000
# pauseButton = gui.button.Button(1080, 10, pygame.image.load("pictures\\buttonPictures\\pauseIcon.png").convert_alpha(), 0.4)
# playButton = gui.button.Button(1130, 10, pygame.image.load("pictures\\buttonPictures\\playIcon.png").convert_alpha(), 0.4)
# restartButton = gui.button.Button(1180, 10, pygame.image.load("pictures\\buttonPictures\\restartIcon.png").convert_alpha(), 0.4)
# exitButton = gui.button.Button(1230, 10, pygame.image.load("pictures\\buttonPictures\\exitIcon.png").convert_alpha(), 0.4)

# speedLimit = SpeedLimit(Vector2([185, 405]), 1, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\speed_limit.png").convert_alpha(), (30, 70))], 30)
# stopSign = StopSign(Vector2([670, 510]), 2, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
# stopSign2 = StopSign(Vector2([670, 260]), 1, 1, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
# simulationWorld.roads[2].update_road_and_direction_priority(1, 2, 0, 1)
# simulationWorld.roads[1].update_road_and_direction_priority(0, 1, 0, 1)
# simulationWorld.roads[1].update_road_and_direction_priority(0, 1, 1, 1)
# simulationWorld.add_hazard(speedLimit)
# simulationWorld.add_hazard(stopSign)
# simulationWorld.add_hazard(stopSign2)

# while simulationWorld.simulationRunning:
#     simulationWorld.screen.fill(simulationWorld.WHITE)
#     simulationWorld.screen.blit(simulationWorld.roads[0].laneImages[simulationWorld.roads[0].currNumOfLanes - 1], simulationWorld.roads[0].imagesPositions[simulationWorld.roads[0].currNumOfLanes - 1])
    
#     if pauseButton.draw(simulationWorld.screen):
#         simulationWorld.simulationPaused = True
#     if playButton.draw(simulationWorld.screen):
#         simulationWorld.simulationPaused = False
    
#     restartButton.draw(simulationWorld.screen)
    
#     if exitButton.draw(simulationWorld.screen):
#         simulationWorld.simulationRunning = False
    
#     if not simulationWorld.simulationPaused:
#         simulationWorld.vehiclesManager.add_vehicles(simulationWorld, simulationWorld.screen)
#         simulationWorld.vehiclesManager.updateCarPos(simulationWorld, dataManager, simulationWorld.accidentManager)
#         simulationWorld.vehiclesManager.remove_vehicles(simulationWorld.roads)


#         current_time = pygame.time.get_ticks()
        
#         if current_time >= next_stat_update:
#             dataManager.update_stats(simulationWorld.vehiclesManager.vehicles)
#             next_stat_update = current_time + dataManager.export_interval * 1000
        
#         delete = [key for key in simulationWorld.accidentManager.allAccidents.keys() if simulationWorld.accidentManager.allAccidents[key].check_if_3_seconds_elapsed()]
#         for key in delete:
#             simulationWorld.accidentManager.allAccidents[key].remove_accident(simulationWorld.vehiclesManager.vehicles)
#             del simulationWorld.accidentManager.allAccidents[key]

#     simulationWorld.screen.blit(speedLimit.images[0], speedLimit.location)
#     simulationWorld.screen.blit(stopSign.images[0], stopSign.location)
#     simulationWorld.screen.blit(stopSign2.images[0], stopSign2.location)
#     VehicleDrawer.draw_vehicles(simulationWorld.vehiclesManager.vehicles, simulationWorld.screen)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             simulationWorld.simulationRunning = False

#     pygame.display.set_caption("Traffic Simulator")
#     pygame.display.update()
#     simulationWorld.clock.tick(simulationWorld.FPS)

# pygame.quit()
# sys.exit()





# # =============== new version =============== #
# def initialize_simulation(roadType : str = "junction", numOfLane : int = 1):
#     global simulationWorld, dataManager, nextStatUpdate, pauseButton, playButton, exitButton, restartButton, selectRoadButton

#     simulationWorld = World(roadType, numOfLane)
#     simulationWorld.set_vehicles_manager(VehiclesManager(simulationWorld.NUMBER_OF_CARS))
#     dataManager = DataManager(filename='simulation_data.xlsx', export_interval=2)
#     nextStatUpdate = pygame.time.get_ticks() + dataManager.export_interval * 1000
    
#     selectRoadButton = Button(920, 10, pygame.image.load("pictures\\buttonPictures\\selectRoadIcon.png").convert_alpha(), 0.3)
#     restartButton = Button(1090, 10, pygame.image.load("pictures\\buttonPictures\\restartIcon.png").convert_alpha(), 0.3)
#     pauseButton = Button(1140, 10, pygame.image.load("pictures\\buttonPictures\\pauseIcon.png").convert_alpha(), 0.3)
#     playButton = Button(1190, 10, pygame.image.load("pictures\\buttonPictures\\playIcon.png").convert_alpha(), 0.3)
#     exitButton = Button(1240, 10, pygame.image.load("pictures\\buttonPictures\\exitIcon.png").convert_alpha(), 0.3)
    
#     # speedLimit = SpeedLimit(Vector2([185, 405]), 1, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\speed_limit.png").convert_alpha(), (30, 70))], 30)
#     # stopSign = StopSign(Vector2([670, 510]), 2, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
#     # stopSign2 = StopSign(Vector2([670, 260]), 1, 1, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
    
#     # simulationWorld.roads[2].update_road_and_direction_priority(1, 2, 0, 1)
#     # simulationWorld.roads[1].update_road_and_direction_priority(0, 1, 0, 1)
#     # simulationWorld.roads[1].update_road_and_direction_priority(0, 1, 1, 1)
    
#     # simulationWorld.add_hazard(speedLimit)
#     # simulationWorld.add_hazard(stopSign)
#     # simulationWorld.add_hazard(stopSign2)


# def main_loop():
#     global nextStatUpdate, roadType, numOfLanes
#     pygame.display.set_caption("Traffic Simulator")
    
#     while simulationWorld.simulationRunning:
#         simulationWorld.screen.fill(simulationWorld.GREEN)
#         simulationWorld.screen.blit(simulationWorld.roads[0].laneImages[simulationWorld.roads[0].currNumOfLanes - 1], simulationWorld.roads[0].imagesPositions[simulationWorld.roads[0].currNumOfLanes - 1])

#         if pauseButton.draw(simulationWorld.screen):
#             simulationWorld.simulationPaused = True
#         if playButton.draw(simulationWorld.screen):
#             simulationWorld.simulationPaused = False
#         if exitButton.draw(simulationWorld.screen):
#             simulationWorld.simulationRunning = False
#         if restartButton.draw(simulationWorld.screen):
#             initialize_simulation(roadType, numOfLanes)
#         selectRoadButton.draw(simulationWorld.screen)

#         VehicleDrawer.draw_vehicles(simulationWorld.vehiclesManager.vehicles, simulationWorld.screen)
#         for hazard in simulationWorld.hazards:
#             simulationWorld.screen.blit(hazard.images[0], hazard.location)

#         if not simulationWorld.simulationPaused:
#             simulationWorld.vehiclesManager.add_vehicles(simulationWorld, simulationWorld.screen)
#             simulationWorld.vehiclesManager.updateCarPos(simulationWorld, dataManager, simulationWorld.accidentManager)
#             simulationWorld.vehiclesManager.remove_vehicles(simulationWorld.roads)

#             current_time = pygame.time.get_ticks()
#             if current_time >= nextStatUpdate:
#                 dataManager.update_stats(simulationWorld.vehiclesManager.vehicles)
#                 nextStatUpdate = current_time + dataManager.export_interval * 1000

#             delete = [key for key in simulationWorld.accidentManager.allAccidents.keys() if simulationWorld.accidentManager.allAccidents[key].check_if_3_seconds_elapsed()]
#             for key in delete:
#                 simulationWorld.accidentManager.allAccidents[key].remove_accident(simulationWorld.vehiclesManager.vehicles)
#                 del simulationWorld.accidentManager.allAccidents[key]

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 simulationWorld.simulationRunning = False

#         pygame.display.update()
#         simulationWorld.clock.tick(simulationWorld.FPS)

#     pygame.quit()
#     sys.exit()


# if __name__ == "__main__":
#     global roadType, numOfLanes
#     roadType = "junction"
#     numOfLanes = 1
#     initialize_simulation(roadType, numOfLanes)
#     main_loop()





# =============== newest version =============== #    
def main_loop(simulationManager : SimulatorManager, simulationWorld : World, dataManager : DataManager, nextStatUpdate : int, buttons : list[Button]):
    pygame.display.set_caption("Traffic Simulator")
    selectRoadButton = buttons[0]
    restartButton = buttons[1]
    pauseButton = buttons[2]
    playButton = buttons[3]
    exitButton = buttons[4]
    
    while simulationWorld.simulationRunning:
        simulationWorld.screen.fill(simulationWorld.GREEN)
        simulationWorld.screen.blit(simulationWorld.roads[0].laneImages[simulationWorld.roads[0].currNumOfLanes - 1], simulationWorld.roads[0].imagesPositions[simulationWorld.roads[0].currNumOfLanes - 1])

        if pauseButton.draw(simulationWorld.screen):
            simulationWorld.simulationPaused = True
        if playButton.draw(simulationWorld.screen):
            simulationWorld.simulationPaused = False
        if exitButton.draw(simulationWorld.screen):
            simulationWorld.simulationRunning = False
        if restartButton.draw(simulationWorld.screen):
            simulationWorld, dataManager, nextStatUpdate, _ = SimulatorManager.initialize_simulation(simulationManager.roadType, simulationManager.numOfLanes, simulationWorld.maxSpeed)
        if selectRoadButton.draw(simulationWorld.screen):
            simulationManager = SimulatorManager.select_road(simulationWorld.screen)
            simulationWorld, dataManager, nextStatUpdate, _ = SimulatorManager.initialize_simulation(simulationManager.roadType, simulationManager.numOfLanes, simulationManager.maxSpeed)

        VehicleDrawer.draw_vehicles(simulationWorld.vehiclesManager.vehicles, simulationWorld.screen)
        for hazard in simulationWorld.hazards:
            simulationWorld.screen.blit(hazard.images[0], hazard.location)

        if not simulationWorld.simulationPaused:
            simulationWorld.vehiclesManager.add_vehicles(simulationWorld, simulationWorld.screen)
            simulationWorld.vehiclesManager.updateCarPos(simulationWorld, dataManager, simulationWorld.accidentManager)
            simulationWorld.vehiclesManager.remove_vehicles(simulationWorld.roads)

            current_time = pygame.time.get_ticks()
            if current_time >= nextStatUpdate:
                dataManager.update_stats(simulationWorld.vehiclesManager.vehicles)
                dataManager.export_to_excel(simulationManager.roadType, simulationManager.numOfLanes) 
                nextStatUpdate = current_time + dataManager.export_interval * 1000

            delete = [key for key in simulationWorld.accidentManager.allAccidents.keys() if simulationWorld.accidentManager.allAccidents[key].check_if_3_seconds_elapsed()]
            for key in delete:
                simulationWorld.accidentManager.allAccidents[key].remove_accident(simulationWorld.vehiclesManager.vehicles)
                del simulationWorld.accidentManager.allAccidents[key]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                simulationWorld.simulationRunning = False

        pygame.display.update()
        simulationWorld.clock.tick(simulationWorld.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    simulatorManager = SimulatorManager.select_road(screen)
    simulationWorld, dataManager, nextStatUpdate, buttons = SimulatorManager.initialize_simulation(simulatorManager.roadType, simulatorManager.numOfLanes, simulatorManager.maxSpeed)
    main_loop(simulatorManager, simulationWorld, dataManager, nextStatUpdate, buttons)