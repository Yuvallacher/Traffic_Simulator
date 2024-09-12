from simulation.vehicle.vehicles_manager import VehiclesManager
from simulation.data.DataManager import DataManager
from simulation.world.World import World
from gui.inputBox import InputBox
from gui.button import Button
from tkinter import filedialog
import tkinter as tk
import pygame
import sys

class SimulatorInitiator():
    def __init__(self, roadType : str, numOfLanes : int, maxSpeed : float, filePath : str, roadDensities : dict, truckPercentage : float):
        self.roadType = roadType
        self.numOfLanes = numOfLanes
        self.maxSpeed = maxSpeed
        self.filePath = filePath
        self.roadDensities = roadDensities
        self.truckPercentage = truckPercentage


    @staticmethod
    def select_road(screen, previousFilePath: str = None) -> 'SimulatorInitiator':
        root = tk.Tk()
        root.withdraw()
        chooseFileButton = Button(600, 300, pygame.image.load("pictures\\buttonPictures\\folderIcon.png").convert_alpha(), 0.1)
        selectedFilePath = previousFilePath
        fileNameLabel = previousFilePath.split('/')[-1] if previousFilePath is not None else "Press the folder icon to select a file"

        roadImages = [
            pygame.image.load("pictures\\roadPictures\\straightRoadPictures\\straightRoad2.png").convert_alpha(),
            pygame.image.load("pictures\\roadPictures\\junctionRoad.png").convert_alpha(),
            pygame.image.load("pictures\\roadPictures\\roundaboutRoad.png").convert_alpha()
        ]
        scaledRoadImages = [pygame.transform.scale(img, (300, 150)) for img in roadImages]

        scaledRoadButtons = [
            Button(50 + i * 400, 50, img, scale=1.0)
            for i, img in enumerate(scaledRoadImages)
        ]

        roadTypes = ["straight", "junction", "roundabout"]

        roadDefaults = [
            {"maxSpeed": "90", "numOfLanes": "2", "numOfRoads": 1},  # For straight road
            {"maxSpeed": "50", "numOfLanes": "1", "numOfRoads": 3},  # For junction
            {"maxSpeed": "50", "numOfLanes": "1", "numOfRoads": 3}   # For roundabout
        ]

        font = pygame.font.Font(None, 32)
        maxSpeedInput = InputBox(300, 300, 140, 32, font, defaultText="90")
        numOfLanesInput = InputBox(300, 350, 140, 32, font, defaultText="1")
        truckPercentageInput = InputBox(300, 400, 140, 32, font, defaultText="10") 
        roadDensityInputs = {}

        startButton = Button(550, 550, pygame.image.load("pictures\\buttonPictures\\startIcon.png").convert_alpha(), 0.3)
        selectedRoadIndex = None
        errorMessage = ""
        roadDensityMessage = ""

        while True:
            screen.fill((255, 255, 255))

            for i, button in enumerate(scaledRoadButtons):
                if button.draw(screen):  
                    selectedRoadIndex = i
                    maxSpeedInput.text = roadDefaults[i]["maxSpeed"]
                    maxSpeedInput.txt_surface = font.render(maxSpeedInput.text, True, maxSpeedInput.color)
                    numOfLanesInput.text = roadDefaults[i]["numOfLanes"]
                    numOfLanesInput.txt_surface = font.render(numOfLanesInput.text, True, numOfLanesInput.color)

                    roadDensityInputs = {}
                    for roadNum in range(1, roadDefaults[i]["numOfRoads"] + 1):
                        roadDensityInputs[roadNum] = InputBox(300, 450 + (roadNum * 50), 140, 32, font, defaultText="3") 
                    roadDensityMessage = "Choose road density on a scale of 1 to 5, with 5 being the most dense:"

                if selectedRoadIndex == i:
                    pygame.draw.rect(screen, (0, 0, 255), button.rect, 3)

            screen.blit(font.render("Allowed Speed:", True, (0, 0, 0)), (50, 305))
            maxSpeedInput.draw(screen)

            screen.blit(font.render("Number of Lanes:", True, (0, 0, 0)), (50, 355))
            numOfLanesInput.draw(screen)

            screen.blit(font.render("Truck Percentage (%):", True, (0, 0, 0)), (50, 405))
            truckPercentageInput.draw(screen)

            for roadNum, densityInput in roadDensityInputs.items():
                screen.blit(font.render(f"Road {roadNum} Density:", True, (0, 0, 0)), (50, 450 + (roadNum * 50)))
                densityInput.draw(screen)

            if chooseFileButton.draw(screen):
                filePath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
                if filePath:
                    selectedFilePath = filePath
                    fileNameLabel = filePath.split('/')[-1]
                            
            screen.blit(font.render(fileNameLabel, True, (0, 0, 0)), (chooseFileButton.rect.right + 30, chooseFileButton.rect.y + 5))

            if startButton.draw(screen):
                errorMessage = ""
                if selectedRoadIndex is not None and selectedFilePath is not None:
                    maxSpeed = maxSpeedInput.get_text()
                    numOfLanes = numOfLanesInput.get_text()
                    truckPercentage = truckPercentageInput.get_text()  

                    if not truckPercentage.replace('.', '', 1).isdigit() or not (0 <= float(truckPercentage) <= 100):
                        errorMessage = "Truck Percentage must be a number between 0 and 100!"
                    elif not maxSpeed.replace('.', '', 1).isdigit() or float(maxSpeed) <= 0:
                        errorMessage = "Allowed Speed must be a positive number!"
                    elif not numOfLanes.isdigit() or int(numOfLanes) < 1 or (selectedRoadIndex == 0 and int(numOfLanes) > 2) or (selectedRoadIndex > 0 and int(numOfLanes) != 1):
                        errorMessage = "Number of Lanes must be 1 (or 2 for straight road)!"
                    else:
                        densities = {}
                        for roadNum, densityInput in roadDensityInputs.items():
                            density = densityInput.get_text()
                            if not density.isdigit() or not (1 <= int(density) <= 5):
                                errorMessage = f"Density for Road {roadNum} must be an integer between 1 and 5!"
                                break
                            densities[roadNum] = int(density)

                        if not errorMessage:
                            return SimulatorInitiator(
                                roadTypes[selectedRoadIndex], 
                                int(numOfLanes), 
                                float(maxSpeed), 
                                selectedFilePath, 
                                densities, 
                                float(truckPercentage) / 100 
                            )
                else:
                    errorMessage = "Please select a road and a file!"

            if errorMessage:
                screen.blit(font.render(errorMessage, True, (255, 0, 0)), (600, 360))
            if roadDensityMessage:
                screen.blit(font.render(roadDensityMessage, True, (0, 0, 255)), (50, 455))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                maxSpeedInput.handle_event(event)
                numOfLanesInput.handle_event(event)
                truckPercentageInput.handle_event(event)  
                for densityInput in roadDensityInputs.values():
                    densityInput.handle_event(event)

            maxSpeedInput.update()
            numOfLanesInput.update()
            truckPercentageInput.update() 
            for densityInput in roadDensityInputs.values():
                densityInput.update()

            pygame.display.flip()
                

    @staticmethod
    def initialize_simulation(simulationInitiator : 'SimulatorInitiator') -> list[World, DataManager, int]:
        simulationWorld = World(simulationInitiator.roadType, simulationInitiator.numOfLanes, simulationInitiator.maxSpeed)
        for roadIndex, road in enumerate(simulationWorld.roads):
            road.density = simulationInitiator.roadDensities[roadIndex + 1] * 2
        simulationWorld.set_vehicles_manager(VehiclesManager(simulationWorld.NUMBER_OF_CARS, simulationInitiator.truckPercentage))
        dataManager = DataManager(simulationInitiator.filePath, 5, simulationInitiator.roadType, simulationInitiator.numOfLanes)
        nextStatUpdate = pygame.time.get_ticks() + dataManager.export_interval * 1000
        
        return simulationWorld, dataManager, nextStatUpdate