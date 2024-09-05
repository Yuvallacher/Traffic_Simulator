from simulation.vehicle.vehicles_manager import VehiclesManager
from simulation.data.DataManager import DataManager
from simulation.world.World import World
from gui.inputBox import InputBox
from gui.button import Button
from tkinter import filedialog
import tkinter as tk
import pygame
import time
import sys

class SimulatorManager():
    def __init__(self, roadType : str, numOfLanes : int, maxSpeed : float, filePath : str):
        self.roadType = roadType
        self.numOfLanes = numOfLanes
        self.maxSpeed = maxSpeed
        self.filePath = filePath


    @staticmethod
    def select_road(screen, previousFilePath : str = None) -> 'SimulatorManager':
        root = tk.Tk()
        root.withdraw()
        chooseFileButton = Button(500, 200, pygame.image.load("pictures\\buttonPictures\\folderIcon.png").convert_alpha(), 0.1)
        selectedFilePath = previousFilePath
        fileNameLabel = previousFilePath.split('/')[-1] if previousFilePath is not None else "Press the folder icon to select a file"

        roadImages = [
            pygame.image.load("pictures\\roadPictures\\straightRoadPictures\\straightRoad2.png").convert_alpha(),
            pygame.image.load("pictures\\roadPictures\\junctionRoad.jpg").convert_alpha(),
            pygame.image.load("pictures\\roadPictures\\roundaboutRoad.jpg").convert_alpha()
        ]
        scaledRoadImages = [pygame.transform.scale(img, (200, 100)) for img in roadImages]

        scaledRoadButtons = [
            Button(50 + i * 250, 50, img, scale=1.0)
            for i, img in enumerate(scaledRoadImages)
        ]

        roadTypes = ["straight", "junction", "roundabout"]

        roadDefaults = [
            {"maxSpeed": "90", "numOfLanes": "2"},  # For straight road
            {"maxSpeed": "50", "numOfLanes": "1"},  # For junction
            {"maxSpeed": "50", "numOfLanes": "1"}   # For roundabout
        ]

        font = pygame.font.Font(None, 32)
        maxSpeedInput = InputBox(250, 200, 140, 32, font, defaultText="90")
        numOfLanesInput = InputBox(250, 250, 140, 32, font, defaultText="2")

        startButton = Button(350, 350, pygame.image.load("pictures\\buttonPictures\\startIcon.png").convert_alpha(), 0.3)
        selectedRoadIndex = None
        errorMessage = ""

        while True:
            screen.fill((255, 255, 255))

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

            if chooseFileButton.draw(screen):
                filePath = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
                if filePath:
                    selectedFilePath = filePath
                    fileNameLabel = filePath.split('/')[-1]
                        
            # Display the selected file name
            screen.blit(font.render(fileNameLabel, True, (0, 0, 0)), (chooseFileButton.rect.right + 20, chooseFileButton.rect.y + 5))

            if startButton.draw(screen):
                if selectedRoadIndex is not None and selectedFilePath is not None:
                    maxSpeed = maxSpeedInput.get_text()
                    numOfLanes = numOfLanesInput.get_text()

                    # Input verification
                    if not maxSpeed.replace('.', '', 1).isdigit() or float(maxSpeed) <= 0:
                        errorMessage = "Max Speed must be a positive number!"
                    elif not numOfLanes.isdigit() or int(numOfLanes) < 1 or (selectedRoadIndex == 0 and int(numOfLanes) > 2) or (selectedRoadIndex > 0 and int(numOfLanes) != 1):
                        errorMessage = "Number of Lanes must be 1 (or 2 for straight road)!"
                    else:
                        return SimulatorManager(roadTypes[selectedRoadIndex], int(numOfLanes), float(maxSpeed), selectedFilePath)
                else:
                    errorMessage = "Please select a road and a file!"

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
    def initialize_simulation(simulationManager : 'SimulatorManager') -> list[World, DataManager, int]:
        simulationWorld = World(simulationManager.roadType, simulationManager.numOfLanes, simulationManager.maxSpeed)
        simulationWorld.set_vehicles_manager(VehiclesManager(simulationWorld.NUMBER_OF_CARS))
        dataManager = DataManager(simulationManager.filePath, 2, simulationManager.roadType, simulationManager.numOfLanes)
        nextStatUpdate = pygame.time.get_ticks() + dataManager.export_interval * 1000
        
        return simulationWorld, dataManager, nextStatUpdate