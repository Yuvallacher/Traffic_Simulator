from simulation.simulationInitiator import SimulatorInitiator
from simulation.data.DataManager import DataManager
from drawings.vehicle_drawer import VehicleDrawer
from simulation.world.hazard import SpeedLimit
from simulation.world.hazard import StopSign
from simulation.world.hazard import TrafficLight
from simulation.world.hazard import Hazard
from simulation.world.World import World
from pygame.math import Vector2
from gui.button import Button
import pygame
import sys
import os

def main_loop(simulationInitiator : SimulatorInitiator, simulationWorld : World, dataManager : DataManager, nextStatUpdate : int):
    global selectRoadButton, restartButton, pauseButton, playButton, exitButton
    global hazards
    activeSign = None
    selectedSign = None
        
    while simulationWorld.simulationRunning:
        simulationWorld.screen.fill(simulationWorld.GREEN)
        simulationWorld.screen.blit(simulationWorld.roads[0].laneImages[simulationWorld.roads[0].currNumOfLanes - 1], simulationWorld.roads[0].imagesPositions[simulationWorld.roads[0].currNumOfLanes - 1])

        if pauseButton.draw(simulationWorld.screen):
            simulationWorld.simulationPaused = True
        if playButton.draw(simulationWorld.screen):
            simulationWorld.simulationPaused = False
        if exitButton.draw(simulationWorld.screen):
            pygame.event.post(pygame.event.Event(pygame.QUIT))
        if restartButton.draw(simulationWorld.screen):
            trafficLightManager = simulationWorld.trafficlightManager
            accidentsData = dataManager.accidentsData
            simulationWorld, dataManager, nextStatUpdate = SimulatorInitiator.initialize_simulation(simulationInitiator)
            dataManager.accidentsData = accidentsData
            simulationWorld.hazards = hazards
            simulationWorld.trafficlightManager = trafficLightManager
            for hazard in simulationWorld.hazards:
                if hazard.nearJunction:
                    simulationWorld.roads[hazard.roadIndex].update_road_and_direction_priority(hazard.junctionID, hazard.roadIndex, hazard.directionIndex, hazard.id, False)
        if selectRoadButton.draw(simulationWorld.screen):
            dataManager.update_stats(simulationWorld.vehiclesManager.vehicles, finalCall=True)
            simulationInitiator = SimulatorInitiator.select_road(simulationWorld.screen, simulationInitiator.filePath)
            accidentsData = dataManager.accidentsData
            simulationWorld, dataManager, nextStatUpdate = SimulatorInitiator.initialize_simulation(simulationInitiator)
            dataManager.accidentsData = accidentsData
            initiate_buttons_and_hazards(simulationInitiator.roadType == "junction")
            simulationWorld.hazards = hazards
        
        VehicleDrawer.draw_vehicles(simulationWorld.vehiclesManager.vehicles, simulationWorld.screen)
        for hazard in simulationWorld.hazards:
            if isinstance(hazard, SpeedLimit) or isinstance(hazard, TrafficLight):
                hazard.draw(simulationWorld.screen)
            else:
                simulationWorld.screen.blit(hazard.images[0], hazard.rect)
            if hazard.drawLine:
                pygame.draw.line(simulationWorld.SCREEN, (255, 0, 0), hazard.lineStart, hazard.lineEnd, 2)

        if not simulationWorld.simulationPaused:
            simulationWorld.vehiclesManager.add_vehicles(simulationWorld, simulationWorld.screen)
            simulationWorld.vehiclesManager.updateCarPos(simulationWorld, dataManager, simulationWorld.accidentManager)
            simulationWorld.vehiclesManager.remove_vehicles(simulationWorld.roads)
            simulationWorld.trafficlightManager.synchronize_traffic_lights(simulationWorld.FPS)

            current_time = pygame.time.get_ticks()
            if current_time >= nextStatUpdate:
                dataManager.update_stats(simulationWorld.vehiclesManager.vehicles)
                nextStatUpdate = current_time + dataManager.export_interval * 1000

            delete = [key for key in simulationWorld.accidentManager.allAccidents.keys() if simulationWorld.accidentManager.allAccidents[key].check_if_3_seconds_elapsed()]
            for key in delete:
                simulationWorld.accidentManager.allAccidents[key].remove_accident(simulationWorld.vehiclesManager.vehicles)
                del simulationWorld.accidentManager.allAccidents[key]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                dataManager.update_stats(simulationWorld.vehiclesManager.vehicles, finalCall=True)
                simulationWorld.simulationRunning = False
            if event.type == pygame.KEYDOWN:
                if selectedSign is not None and selectedSign.inputActive:
                    if event.key == pygame.K_RETURN:
                        new_speed = selectedSign.inputBox.get_text()
                        if new_speed.replace('.', '', 1).isdigit() and float(new_speed) > 0:
                            selectedSign.set_speed_limit(float(new_speed))
                        selectedSign.inputBox.active = False
                        selectedSign.inputActive = False 
                        selectedSign = None
                    else:
                        selectedSign.inputBox.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN: 
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if selectedSign is not None:
                        if not selectedSign.rect.collidepoint(mouse_pos):
                            new_speed = selectedSign.inputBox.get_text()
                            if new_speed.replace('.', '', 1).isdigit() and float(new_speed) > 0:
                                selectedSign.set_speed_limit(float(new_speed))
                            selectedSign.inputBox.active = False
                            selectedSign.inputActive = False 
                            selectedSign = None
                    for hazard in simulationWorld.hazards:
                        if hazard.rect.collidepoint(mouse_pos):
                            activeSign = hazard
                elif event.button == 3:
                    mouse_pos = pygame.mouse.get_pos()
                    for hazard in simulationWorld.hazards:
                        if hazard.rect.collidepoint(mouse_pos) and hazard.type == "speedLimit":
                            selectedSign = hazard
                            selectedSign.inputActive = True 
                            selectedSign.inputBox.active = True
            if event.type == pygame.MOUSEMOTION:
                if activeSign is not None:
                    activeSign.rect.move_ip(event.rel)
                    if activeSign.type == "speedLimit":
                            activeSign.update_input_box_position()
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if activeSign is not None:
                        mousePosAsVector = Vector2(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
                        closestPoint = simulationWorld.search_closest_point_in_roads(mousePosAsVector)
                        if closestPoint:
                            if activeSign.priority == 2:
                                if activeSign.nearJunction:
                                    simulationWorld.roads[activeSign.roadIndex].update_road_and_direction_priority(activeSign.junctionID, activeSign.roadIndex, activeSign.directionIndex, activeSign.id, True)
                                if closestPoint["nearJunction"]:
                                    simulationWorld.roads[closestPoint["roadIndex"]].update_road_and_direction_priority(closestPoint["junctionID"], closestPoint["roadIndex"], closestPoint["directionIndex"], activeSign.id, False)
                                    activeSign.nearJunction = True
                                    activeSign.junctionID = closestPoint["junctionID"]
                                else:
                                    activeSign.nearJunction = False
                                    activeSign.junctionID = None
                            vector = closestPoint["coordinate"] - closestPoint["nextCoordinate"]
                            midpoint = (closestPoint["coordinate"] + closestPoint["nextCoordinate"]) / 2
                            perpendicularVector =  Vector2(-vector.y, vector.x).normalize() * 15
                            perpendicularStart = midpoint - perpendicularVector
                            perpendicularEnd = midpoint + perpendicularVector 
                            activeSign.rect.center = perpendicularStart + Vector2(0, -40)
                            activeSign.set_new_position(closestPoint["roadIndex"], closestPoint["directionIndex"], closestPoint["coordinate"])
                            activeSign.lineMidPoint = midpoint
                            activeSign.lineStart = perpendicularStart
                            activeSign.lineEnd = perpendicularEnd
                            activeSign.drawLine = True                     
                            if isinstance(activeSign, TrafficLight):
                                simulationWorld.trafficlightManager.add_traffic_light(activeSign)
                        else:
                            if isinstance(activeSign, TrafficLight):
                                simulationWorld.trafficlightManager.remove_traffic_light(activeSign)
                            activeSign.drawLine = False
                            if activeSign.nearJunction:
                                if activeSign.priority == 2:
                                    simulationWorld.roads[activeSign.roadIndex].update_road_and_direction_priority(activeSign.junctionID, activeSign.roadIndex, activeSign.directionIndex, activeSign.id, True)
                                activeSign.nearJunction = False
                                activeSign.junctionID = None
                            activeSign.roadIndex = -1
                            activeSign.directionIndex = -1
                        activeSign = None

        pygame.display.flip()
        simulationWorld.clock.tick(simulationWorld.FPS)

    pygame.quit()
    sys.exit()



def initiate_buttons_and_hazards(isJunction : bool):
    global selectRoadButton, restartButton, pauseButton, playButton, exitButton
    selectRoadButton = Button(920, 10, pygame.image.load("pictures\\buttonPictures\\selectRoadIcon.png").convert_alpha(), 0.3)
    restartButton = Button(1090, 10, pygame.image.load("pictures\\buttonPictures\\restartIcon.png").convert_alpha(), 0.3)
    pauseButton = Button(1140, 10, pygame.image.load("pictures\\buttonPictures\\pauseIcon.png").convert_alpha(), 0.3)
    playButton = Button(1190, 10, pygame.image.load("pictures\\buttonPictures\\playIcon.png").convert_alpha(), 0.3)
    exitButton = Button(1240, 10, pygame.image.load("pictures\\buttonPictures\\exitIcon.png").convert_alpha(), 0.3)

    global hazards
    speedLimit1 = SpeedLimit(Vector2([1090, 70]), -1, -1, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\speed_limit.png").convert_alpha(), (30, 70))], 30)
    speedLimit2 = SpeedLimit(Vector2([1140, 70]), -1, -1, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\speed_limit.png").convert_alpha(), (30, 70))], 30)
    stopSign1 = StopSign(Vector2([1190, 70]), 2, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
    stopSign2 = StopSign(Vector2([1240, 70]), 2, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
    stopSign3 = StopSign(Vector2([1140, 140]), 2, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
    stopSign4 = StopSign(Vector2([1190, 140]), 2, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
    stopSign5 = StopSign(Vector2([1240, 140]), 2, 0, [pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\stop.png").convert_alpha(), (30, 70))])
    if isJunction:
        redLightImage = pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\traffic_light_red2.png").convert_alpha(), (30, 70))
        yellowLightImage = pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\traffic_light_yellow2.png").convert_alpha(), (30, 70))
        greenLightImage = pygame.transform.scale(pygame.image.load("pictures\\hazardsPictures\\traffic_light_green2.png").convert_alpha(), (30, 70))
        trafficLight1 = TrafficLight(Vector2([1090, 140]), 2, 0, [redLightImage, yellowLightImage, greenLightImage], [1,0,0])
        trafficLight2 = TrafficLight(Vector2([1140, 210]), 2, 0, [redLightImage, yellowLightImage, greenLightImage], [1,0,0])
        trafficLight3 = TrafficLight(Vector2([1190, 210]), 2, 0, [redLightImage, yellowLightImage, greenLightImage], [1,0,0])
        trafficLight4 = TrafficLight(Vector2([1240, 210]), 2, 0, [redLightImage, yellowLightImage, greenLightImage], [1,0,0])
        hazards = [speedLimit1, speedLimit2, stopSign1, stopSign2, stopSign3, stopSign4, stopSign5, trafficLight1, trafficLight2, trafficLight3, trafficLight4]
    else:
        hazards = [speedLimit1, speedLimit2, stopSign1, stopSign2, stopSign3, stopSign4, stopSign5]

    
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Traffic Simulator")
    simulatorManager = SimulatorInitiator.select_road(screen)
    initiate_buttons_and_hazards(simulatorManager.roadType == "junction")
    simulationWorld, dataManager, nextStatUpdate = SimulatorInitiator.initialize_simulation(simulatorManager)
    global hazards
    simulationWorld.hazards = hazards
    if os.path.exists(dataManager.filename):
        os.remove(dataManager.filename)
    main_loop(simulatorManager, simulationWorld, dataManager, nextStatUpdate)