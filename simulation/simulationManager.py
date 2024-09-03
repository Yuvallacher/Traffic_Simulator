from simulation.vehicle.vehicles_manager import VehiclesManager
from simulation.data.DataManager import DataManager
from simulation.world.World import World
from gui.inputBox import InputBox
from gui.button import Button
import pygame
import sys

class SimulatorManager():
    def __init__(self, roadType : str, numOfLanes : int, maxSpeed : float):
        self.roadType = roadType
        self.numOfLanes = numOfLanes
        self.maxSpeed = maxSpeed


    @staticmethod
    def select_road(screen) -> 'SimulatorManager':
        roadImages = [
            pygame.image.load("pictures\\roadPictures\\straightRoadPictures\\straightRoad2.png").convert_alpha(),
            pygame.image.load("pictures\\roadPictures\\junctionRoad.jpg").convert_alpha(),
            pygame.image.load("pictures\\roadPictures\\roundaboutRoad.jpg").convert_alpha()
        ]
        scaledRoadImages = [pygame.transform.scale(img, (200, 100)) for img in roadImages]
        
        scaledRoadButtons = [
            Button(50 + i*250, 50, img, scale=1.0) 
            for i, img in enumerate(scaledRoadImages)
        ]
        
        roadTypes = ["straight", "junction", "roundabout"]
        
        roadDefaults = [
            {"maxSpeed": "90", "numOfLanes": "2"},  # For straight road
            {"maxSpeed": "50", "numOfLanes": "1"},  # For junction
            {"maxSpeed": "50", "numOfLanes": "1"}   # For roundabout
        ]
        
        font = pygame.font.Font(None, 32)
        maxSpeedInput = InputBox(250, 200, 140, 32, font, default_text="90")
        numOfLanesInput = InputBox(250, 250, 140, 32, font, default_text="2")
        
        selectedRoadIndex = None
        errorMessage = ""
        
        while True:
            screen.fill((255, 255, 255))  # Clear screen with white background

            # Display the road images as buttons
            for i, button in enumerate(scaledRoadButtons):
                if button.draw(screen):  # If a button is clicked
                    selectedRoadIndex = i
                    maxSpeedInput.text = roadDefaults[i]["maxSpeed"]
                    maxSpeedInput.txt_surface = font.render(maxSpeedInput.text, True, maxSpeedInput.color)
                    numOfLanesInput.text = roadDefaults[i]["numOfLanes"]
                    numOfLanesInput.txt_surface = font.render(numOfLanesInput.text, True, numOfLanesInput.color)
                
                # Draw a green highlight around the selected road
                if selectedRoadIndex == i:
                    pygame.draw.rect(screen, (0, 0, 255), button.rect, 3)

            # Display the labels and input boxes
            screen.blit(font.render("Max Speed:", True, (0, 0, 0)), (50, 205))
            maxSpeedInput.draw(screen)
            
            screen.blit(font.render("Number of Lanes:", True, (0, 0, 0)), (50, 255))
            numOfLanesInput.draw(screen)
            
            startButton = Button(350, 350, pygame.image.load("pictures\\buttonPictures\\startIcon.png").convert_alpha(), 0.3)
            if startButton.draw(screen):
                if selectedRoadIndex is not None:
                    maxSpeed = maxSpeedInput.get_text()
                    numOfLanes = numOfLanesInput.get_text()
                    
                    # Input verification
                    if not maxSpeed.replace('.', '', 1).isdigit() or float(maxSpeed) <= 0:
                        errorMessage = "Max Speed must be a positive number!"
                    elif not numOfLanes.isdigit() or int(numOfLanes) < 1 or (selectedRoadIndex == 0 and int(numOfLanes) > 2) or (selectedRoadIndex > 0 and int(numOfLanes) != 1):
                        errorMessage = "Number of Lanes must be 1 (or 2 for straight road)!"
                    else:
                        return SimulatorManager(roadTypes[selectedRoadIndex], int(numOfLanes), float(maxSpeed))
                else:
                    errorMessage = "Please select a road!"
            
            if errorMessage:
                screen.blit(font.render(errorMessage, True, (255, 0, 0)), (100, 300))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                maxSpeedInput.handle_event(event)
                numOfLanesInput.handle_event(event)

            maxSpeedInput.update()
            numOfLanesInput.update()
            
            pygame.display.flip()
            

    @staticmethod
    def initialize_simulation(roadType : str = "junction", numOfLanes : int = 1, maxSpeed : float = 50) -> list[World, DataManager, int, list[Button]]:
        simulationWorld = World(roadType, numOfLanes, maxSpeed)
        simulationWorld.set_vehicles_manager(VehiclesManager(simulationWorld.NUMBER_OF_CARS))
        dataManager = DataManager('simulation_data.xlsx', 2, roadType, numOfLanes)
        nextStatUpdate = pygame.time.get_ticks() + dataManager.export_interval * 1000
        
        selectRoadButton = Button(920, 10, pygame.image.load("pictures\\buttonPictures\\selectRoadIcon.png").convert_alpha(), 0.3)
        restartButton = Button(1090, 10, pygame.image.load("pictures\\buttonPictures\\restartIcon.png").convert_alpha(), 0.3)
        pauseButton = Button(1140, 10, pygame.image.load("pictures\\buttonPictures\\pauseIcon.png").convert_alpha(), 0.3)
        playButton = Button(1190, 10, pygame.image.load("pictures\\buttonPictures\\playIcon.png").convert_alpha(), 0.3)
        exitButton = Button(1240, 10, pygame.image.load("pictures\\buttonPictures\\exitIcon.png").convert_alpha(), 0.3)
        
        return simulationWorld, dataManager, nextStatUpdate, [selectRoadButton, restartButton, pauseButton, playButton, exitButton]