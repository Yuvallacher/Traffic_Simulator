#from simulation.world.Point import Point
import json
import pygame.image
from pygame.math import Vector2
from pygame.surface import Surface

class Road:
    def __init__(self, startingNumberOfLanes : int, allLanesInRoad : list[list['Lane']], laneImages : list[Surface], imagesPositions : list[list[int]]):
        self.allLanesInRoad = allLanesInRoad
        self.numberOfDirections = len(allLanesInRoad)
        self.currNumOfLanes = startingNumberOfLanes
        self.laneImages = laneImages
        self.imagesPositions = imagesPositions
               
        
        
    def get_target_position(self, directionIndex : int, laneIndex : int, currentTargetPositionIndex : int) -> Vector2:
        path = self.allLanesInRoad[directionIndex][laneIndex].path
        if currentTargetPositionIndex + 1 < len(path):
            return path[currentTargetPositionIndex] 
        else:
            return path[-1]
        
    def get_left_adjacent_lane_index(self, directionIndex : int, laneIndex : int) -> int:
        if laneIndex == 0:
            return None
        else:
            return laneIndex - 1

    def get_right_adjacent_lane_index(self, directionIndex : int, laneIndex : int) -> int:
        if laneIndex == len(self.allLanesInRoad[directionIndex]) - 1:
            return None
        else:
            return laneIndex + 1
        
    def get_rightmost_lane_index(self, directionIndex : int) -> int:
        return len(self.allLanesInRoad[directionIndex]) - 1

    class Lane:
        def __init__(self, listOfCoordinates : list[Vector2]):
            self.path = listOfCoordinates
            self.startingPoint = listOfCoordinates[0]
        
        


class RoadBuilder:
    @staticmethod
    def create_road(roadName : str, startingNumberOfLanes=2) -> list[Road]:
        if 'straight' in roadName:
            roads = RoadBuilder.straight_road_read_lanes_from_file(startingNumberOfLanes)
        elif 'junction' in roadName:
            roads = RoadBuilder.junction_road_read_lanes_from_file(startingNumberOfLanes, roadName)
        
     
        return roads
        
    @staticmethod
    def straight_road_read_lanes_from_file(startingNumberOfLanes : int) -> list[Road]: # TODO implement and move to inheriting classes
        with open("jsons\\road.json", 'r') as file:
            data = json.load(file)

            roadData = data['straight_road']
            lanesData = roadData['lanes']

            lanesDirection1 = []
            lanesDirection2 = []
            roadsList = []
            
            for idx, laneCoordinates in enumerate(lanesData):
                if idx < 2 * startingNumberOfLanes:
                    path = [Vector2(coord) for coord in laneCoordinates]
                    lane = Road.Lane(path)

                    if idx % 2 == 0:
                        lanesDirection1.append(lane) # (left-to-right driving direction)
                    else:
                        lanesDirection2.append(lane) # (right-to-left driving direction)
            images, imagesPos = RoadBuilder.load_lane_images(roadData)
            roadDirections = [lanesDirection1, lanesDirection2]
            road = Road(startingNumberOfLanes, roadDirections, images, imagesPos)
            roadsList.append(road)
            return roadsList
    
    

    @staticmethod
    def load_lane_images(roadData : dict) -> list[list]: # TODO implement and move to inheriting classes
        imagesPaths = roadData["images_path"]
        imagesScales = roadData["images_scales"]
        imagesPos = roadData["image_pos"]
        images = []
        for index, imagePath in enumerate(imagesPaths):
            images.append(pygame.transform.scale(pygame.image.load(imagePath), imagesScales[index])) #TODO add scale? if so, what scale            
        return [images, imagesPos]       


    @staticmethod
    def junction_road_read_lanes_from_file(startingNumberOfLanes : int, roadName : str) -> list[Road]: # TODO implement and move to inheriting classes
        with open("jsons\\road.json", 'r') as file:
            
            data = json.load(file)
            roadsList = []
            roadData = data['junction_road']
            lanesData = roadData['lanes']

            lanesDirection1 = []
            lanesDirection2 = []
            imagesPaths = roadData["images_path"]
            imagesScales = roadData["images_scales"]
            imagesPos = roadData["image_pos"]
            

            #TODO add a way to limit user - only 1 or 2 lanes in each direction           
            for idx, lane_coordinates in enumerate(lanesData):
                path = [Vector2(coord) for coord in lane_coordinates]
                lane = Road.Lane(path)

                if idx % 2 == 0:
                    lanesDirection1.append(lane) # (left-to-right driving direction)
                else:
                    lanesDirection2.append(lane) # (right-to-left driving direction)
                    roadDirections = [lanesDirection1, lanesDirection2]
                    road = Road(startingNumberOfLanes, roadDirections, imagesScales, imagesPos)
                    roadsList.append(road)
                    lanesDirection1 = []
                    lanesDirection2 = []
                    

            return roadsList  

    

