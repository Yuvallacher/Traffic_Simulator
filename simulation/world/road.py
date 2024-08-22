#from simulation.world.Point import Point
import json
import pygame.image
from pygame.math import Vector2
from pygame.surface import Surface

class Road:
    def __init__(self, startingNumberOfLanes : int, allLanesInRoad : list[list['Lane']], laneImages : list[Surface], imagesPositions : list[list[int]], junctions : list[dict] = None):
        self.allLanesInRoad = allLanesInRoad
        self.numberOfDirections = len(allLanesInRoad)
        self.currNumOfLanes = startingNumberOfLanes
        self.laneImages = laneImages
        self.imagesPositions = imagesPositions
        self.junctions = junctions
        
        
    def get_target_position(self, directionIndex : int, laneIndex : int, currentTargetPositionIndex : int) -> Vector2:
        """
        while NOT in a junction, check for the next target position
        """
        path = self.allLanesInRoad[directionIndex][laneIndex].path
        if currentTargetPositionIndex + 1 < len(path):
            return path[currentTargetPositionIndex] 
        else:
            return path[-1]
    
    
    def is_start_of_junction(self, targetPosition : Vector2, sourceDirectionIndex : int) -> list[bool, dict, int]:
        """
        check if a given target position is the start of a junction. if so - return True and the path-options for the vehicle that asked
        """
        if self.junctions is not None:
            for junction in self.junctions:
                for key in junction[str(sourceDirectionIndex)].keys():
                    if Vector2(junction[str(sourceDirectionIndex)][key][1][0]) == targetPosition:
                        return True, junction[str(sourceDirectionIndex)], self.junctions.index(junction)
        return False, None, -1
    
    
    def get_target_position_junction(self, junctionIndex : int, sourceDirectionIndex : int, destRoadIndex : str, destDirectionIndex : str, currentTargetPositionIndex : int) -> Vector2:
        """
        while in a junction, check for the next target position
        """
        destChoiceIndex = f"[{destRoadIndex},{destDirectionIndex}]"
        path = self.junctions[junctionIndex][str(sourceDirectionIndex)][destChoiceIndex][1]
        if currentTargetPositionIndex + 1 < len(path):
            return path[currentTargetPositionIndex] 
        else:
            return path[-1]
        
    
    def is_end_of_junction(self, targetPosition : Vector2, junctionIndex : int, sourceDirectionIndex : int, destRoadIndex : str, destDirectionIndex : str) -> list[bool, int]:
        destChoiceIndex = f"[{destRoadIndex},{destDirectionIndex}]"
        path = self.junctions[junctionIndex][str(sourceDirectionIndex)][destChoiceIndex][1]
        if targetPosition == path[-1]:
            return True, self.junctions[junctionIndex][str(sourceDirectionIndex)][destChoiceIndex][0]
        return False, -1
    
    
    def get_left_adjacent_lane_index(self, laneIndex : int) -> int:
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
        def __init__(self, listOfCoordinates : list[Vector2], spawnPoint = True):
            self.path = listOfCoordinates
            self.startingPoint = listOfCoordinates[0]
            self.spawnPoint = spawnPoint
        
        


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
        """
        reads and builds the roads for the junction-type scenario
        """
        with open("jsons\\road.json", 'r') as file:
            
            data = json.load(file)
            roadsList = []
            roadData = data['junction_road']
            lanesData = roadData['lanes']

            lanesDirection1 = []
            lanesDirection2 = []
            imagesPaths = roadData["images_path"]
            # imagesScales = roadData["images_scales"]
            imagesPos = roadData["image_pos"]
            
            junctions = RoadBuilder.read_junctions_from_json(data)
            roadIndex = 0
            #TODO add a way to limit user - only 1 or 2 lanes in each direction           
            for idx, lane_coordinates in enumerate(lanesData):
                path = [Vector2(coord) for coord in lane_coordinates]
                spawnPoint = False if idx == 5 else True
                lane = Road.Lane(path, spawnPoint)

                if idx % 2 == 0:
                    lanesDirection1.append(lane)
                else:
                    lanesDirection2.append(lane)
                    
                    roadDirections = [lanesDirection1, lanesDirection2]
                    relevantJunctions = RoadBuilder.get_relevant_junction_info(junctions, roadIndex)
                    road = Road(startingNumberOfLanes, roadDirections, imagesPaths, imagesPos, relevantJunctions)
                    roadIndex += 1
                    roadsList.append(road)
                    lanesDirection1 = []
                    lanesDirection2 = []
                    
            return roadsList  

    
    @staticmethod
    def read_junctions_from_json(data) -> list[dict]:
        """
            parses json to return list of junction dicts
        """
        junctionList : list[dict] = []
        
        for key in data["junction_road"]["junctions"].keys():
            junctionList.append(data["junction_road"]["junctions"][key])
                       
        return junctionList
    
    
    @staticmethod
    def get_relevant_junction_info(junctions : list[dict], roadIndex : int) -> list[dict]:
        """
        take only the junction-paths that involve the specific road in question
        """
        relevantJunctions = []
        for junction in junctions:
            for key in junction.keys():
                if str(roadIndex) == key:
                    relevantJunctions.append(junction[key])
        
        return relevantJunctions