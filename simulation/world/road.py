from pygame.surface import Surface
from pygame.math import Vector2
import pygame.image
import json

class Road:
    def __init__(self, startingNumberOfLanes : int, allLanesInRoad : list[list['Lane']], laneImages : list[Surface], imagesPositions : list[list[int]], junctions : dict[int, 'Junction'] = None, roundabouts : dict[int, 'Roundabout'] = None):
        self.allLanesInRoad = allLanesInRoad
        self.numberOfDirections = len(allLanesInRoad)
        self.currNumOfLanes = startingNumberOfLanes
        self.laneImages = laneImages
        self.imagesPositions = imagesPositions
        self.junctions = junctions
        self.roundabouts = roundabouts
        self.density : int
 
        
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
            for junction in self.junctions.values():
                if junction.paths.get(str(sourceDirectionIndex)) is not None:
                    for key in junction.paths[str(sourceDirectionIndex)].keys():
                        if Vector2(junction.paths[str(sourceDirectionIndex)][key][1][0]) == targetPosition:
                            return True, junction.paths[str(sourceDirectionIndex)], junction.id
        return False, None, -1
    
    
    def get_target_position_junction(self, junctionID : int, sourceDirectionIndex : int, destRoadIndex : str, destDirectionIndex : str, currentTargetPositionIndex : int) -> Vector2:
        """
        while in a junction, check for the next target position
        """
        destChoiceIndex = f"[{destRoadIndex},{destDirectionIndex}]"
        path = self.junctions[junctionID].paths[str(sourceDirectionIndex)][destChoiceIndex][1]
        if currentTargetPositionIndex + 1 < len(path):
            return path[currentTargetPositionIndex] 
        else:
            return path[-1]
    
    
    def get_junction_path(self,  junctionID : int, sourceDirectionIndex : int, destRoadIndex : str, destDirectionIndex : str) -> list[Vector2]:
        destChoiceIndex = f"[{destRoadIndex},{destDirectionIndex}]"
        path = self.junctions[junctionID].paths[str(sourceDirectionIndex)][destChoiceIndex][1]
        return path
        
    
    def is_end_of_junction(self, targetPosition : Vector2, junctionID : int, sourceDirectionIndex : int, destRoadIndex : str, destDirectionIndex : str) -> list[bool, int]:
        destChoiceIndex = f"[{destRoadIndex},{destDirectionIndex}]"
        path = self.junctions[junctionID].paths[str(sourceDirectionIndex)][destChoiceIndex][1]
        if targetPosition == path[-1]:
            return True, self.junctions[junctionID].paths[str(sourceDirectionIndex)][destChoiceIndex][0]
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

    
    def check_road_and_direction_priority(self, junctionIndex: int, roadIndex: int, directionIndex: int) -> int:
        key = (str(roadIndex), str(directionIndex))
        if key in self.junctions[junctionIndex].priorities:
            if self.junctions[junctionIndex].priorities[key][0] <= 1:
                return 1
            else:
                return 2
        else:
            return 0
    
    
    def update_road_and_direction_priority(self, junctionID : int, roadIndex : int, directionIndex : int, hazardID : int, increase : bool):
        if increase and hazardID in self.junctions[junctionID].priorities[(str(roadIndex), str(directionIndex))][1]:
            self.junctions[junctionID].priorities[(str(roadIndex), str(directionIndex))][0] += 1
            self.junctions[junctionID].priorities[(str(roadIndex), str(directionIndex))][1].remove(hazardID)
        elif not increase and hazardID not in self.junctions[junctionID].priorities[(str(roadIndex), str(directionIndex))][1]:
            self.junctions[junctionID].priorities[(str(roadIndex), str(directionIndex))][0] -= 1
            self.junctions[junctionID].priorities[(str(roadIndex), str(directionIndex))][1].append(hazardID)
    
    
    def is_point_part_of_junction(self, coordinate : Vector2) -> bool:
        if self.junctions is not None:
            for junction in self.junctions.values():
                for sourceDirectionIndex in junction.paths.keys():
                    for destChoiceIndex in junction.paths[sourceDirectionIndex].keys():
                        path = junction.paths[sourceDirectionIndex][destChoiceIndex][1]
                        if coordinate in path:
                            return True
        return False
    
    # === Added ===
    def is_first_in_junction_queue(self, junctionID : int, vehicleId : int):
        if self.junctions[junctionID].check_queue_position(vehicleId) == 0:
            return True
        return False


    def is_roundabout_entry_point(self, targetPosition : Vector2, sourceDirectionIndex : int) -> list[bool, int]:
        if self.roundabouts is not None:
            for roundabout in self.roundabouts.values():
                if roundabout.entryPaths[str(sourceDirectionIndex)][1][0] == targetPosition:
                    return (True, roundabout.id)
        return (False , None)
    
    
    def get_roundabout_entry_target_position(self, targetPositionIndex : int, roundaboutId : int, sourceDirectionIndex : int) -> Vector2:
        entryPathTurnCoordinates = self.roundabouts[roundaboutId].entryPaths[str(sourceDirectionIndex)][1] # Coordinates of the turn
        if targetPositionIndex + 1 == len(entryPathTurnCoordinates):
            return entryPathTurnCoordinates[-1]
        else:
            return entryPathTurnCoordinates[targetPositionIndex]


    def is_turn_integrates_roundabout(self, targetPosition : Vector2, roundaboutId : int, sourceDirectionIndex : int) -> bool:
        entryPathTurnCoordinates = self.roundabouts[roundaboutId].entryPaths[str(sourceDirectionIndex)][1] # Coordinates of the turn
        if targetPosition == entryPathTurnCoordinates[-1]:
            return True
        return False
    
    
    def get_roundabout_entering_index(self, roundaboutId : int, sourceDirectionIndex : int) -> int:
        return self.roundabouts[roundaboutId].entryPaths[str(sourceDirectionIndex)][0]
    
    
    def get_next_target_position_of_roundabout_path(self, roundaboutId : int, targetPositionIndex) -> Vector2:
        path = self.roundabouts[roundaboutId].path
        pathSize = len(self.roundabouts[roundaboutId].path)
        return Vector2(path[targetPositionIndex % pathSize - 1])


    def is_desired_roundabout_exit_point(self, roundaboutId : int, targetPosition : Vector2, desiredRoadIndex : int, desiredDirectionIndex : int) -> bool:
        desiredPath = f"[{desiredRoadIndex},{desiredDirectionIndex}]"
        if targetPosition == self.roundabouts[roundaboutId].exitPaths[desiredPath][1][0]:
            return True
        return False

    
    def get_next_target_position_of_roundabout_exit(self, roundaboutId : int, targetPositionIndex, desiredRoadIndex, desiredDirectionIndex) -> Vector2:
        desiredPathIndexes = f"[{desiredRoadIndex},{desiredDirectionIndex}]"
        exitPath = self.roundabouts[roundaboutId].exitPaths[desiredPathIndexes][1]
        if targetPositionIndex + 1 == len(exitPath):
             return exitPath[-1]
        else:
            return exitPath[targetPositionIndex]


    def is_end_of_roundabout_exit(self, roundaboutId : int, targetPosition: Vector2, desiredRoadIndex, desiredDirectionIndex) -> bool:
        desiredPathIndexes = f"[{desiredRoadIndex},{desiredDirectionIndex}]"
        exitPath = self.roundabouts[roundaboutId].exitPaths[desiredPathIndexes][1]
        if targetPosition == exitPath[-1]:
            return True
        return False
    
    
    def get_roundabout_to_road_index(self, roundaboutId : int, desiredRoadIndex, desiredDirectionIndex) -> int:
        desiredPathIndexes = f"[{desiredRoadIndex},{desiredDirectionIndex}]"
        return self.roundabouts[roundaboutId].exitPaths[desiredPathIndexes][2]
    
    
    def is_point_part_of_roundabout(self, coordinate : Vector2) -> bool:
        if self.roundabouts is not None:
            for roundabout in self.roundabouts.values():
                roundaboutPath = roundabout.path
                if coordinate in roundaboutPath:
                    return True
                for exitPath in roundabout.exitPaths.values():
                    if coordinate in exitPath[1]:
                        return True
                for entryPath in roundabout.entryPaths.values():
                    if coordinate in entryPath[1]:
                        return True
        return False
    
    
    #======== class Lane ========#
    class Lane:
        def __init__(self, listOfCoordinates : list[Vector2], spawnPoint = True):
            self.path = listOfCoordinates
            self.startingPoint = listOfCoordinates[0]
            self.spawnPoint = spawnPoint
        
    #======== class Junction ========#
    class Junction:
        def __init__(self, paths : dict, id : int):
            self.paths = paths
            self.priorities : dict[tuple[str, str], list[int, list[int]]] = {}
            self.id = id
            self.queue = []
        
        def initiate_priorities(self, roadIndex):
            for directionIndex in self.paths.keys():
                self.priorities[(roadIndex, directionIndex)] = [2, []]
        
        def add_to_queue(self, vehicleId : int):
            self.queue.append(vehicleId)

        def remove_from_queue(self, vehicleId : int): 
            if len(self.queue) > 0:   
                self.queue.remove(vehicleId)
                
        def check_queue_position(self, vehicleId : int):
            if vehicleId in self.queue:
                return self.queue.index(vehicleId)
            return -1

    #======== class Roundabout ========#
    class Roundabout:
        def __init__(self, path : list[Vector2], entryPaths : dict, exitPaths : dict,  id : int):
            self.path = path
            self.entryPaths = entryPaths
            self.exitPaths = exitPaths
            self.id = id


class RoadBuilder:
    @staticmethod
    def create_road(roadName : str, startingNumberOfLanes=2) -> list[Road]:
        if 'straight' in roadName:
            roads = RoadBuilder.straight_road_read_lanes_from_file(startingNumberOfLanes)
        elif 'junction' in roadName:
            roads = RoadBuilder.junction_road_read_lanes_from_file(startingNumberOfLanes, roadName)
        elif 'roundabout' in roadName:
            roads = RoadBuilder.roundabout_road_read_lanes_from_file(startingNumberOfLanes, roadName)    
        return roads
        
    
    @staticmethod
    def straight_road_read_lanes_from_file(startingNumberOfLanes : int) -> list[Road]:
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
                        lanesDirection1.append(lane) 
                    else:
                        lanesDirection2.append(lane) 
            images, imagesPos = RoadBuilder.load_lane_images(roadData)
            roadDirections = [lanesDirection1, lanesDirection2]
            road = Road(startingNumberOfLanes, roadDirections, images, imagesPos)
            roadsList.append(road)
            return roadsList
    
    
    @staticmethod
    def load_lane_images(roadData : dict) -> list[list]:
        imagesPaths = roadData["images_path"]
        imagesScales = roadData["images_scales"]
        imagesPos = roadData["image_pos"]
        images = []
        for index, imagePath in enumerate(imagesPaths):
            images.append(pygame.transform.scale(pygame.image.load(imagePath), imagesScales[index]).convert())            
        return [images, imagesPos]


    @staticmethod
    def junction_road_read_lanes_from_file(startingNumberOfLanes : int, roadName : str) -> list[Road]:
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
            
            images, imagesPos = RoadBuilder.load_lane_images(roadData)
            
            junctions = RoadBuilder.read_junctions_from_json(roadData)
            roadIndex = 0
             
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
                    road = Road(startingNumberOfLanes, roadDirections, images, imagesPos, relevantJunctions)
                    roadIndex += 1
                    roadsList.append(road)
                    lanesDirection1 = []
                    lanesDirection2 = []
                    
            return roadsList  

    
    @staticmethod
    def read_junctions_from_json(roadData) -> dict[int, Road.Junction]:
        """
            parses json to return list of junction dicts
        """
        junctionDict : dict[int, Road.Junction] = {}
        
        for id, key in enumerate(roadData["junctions"].keys()):
            junctionDict[id] = (Road.Junction(roadData["junctions"][key], id))
                       
        return junctionDict

    
    @staticmethod
    def get_relevant_junction_info(junctions : dict[int, Road.Junction], roadIndex : int) -> dict[int, Road.Junction]:
        """
        take only the junction-paths that involve the specific road in question
        """
        relevantJunctions : dict[int, Road.Junction] = {}
        for junction in junctions.values():
            for key in junction.paths.keys():
                if str(roadIndex) == key:
                    relevantJunction = Road.Junction(junction.paths[key], junction.id)
                    relevantJunction.initiate_priorities(key)
                    relevantJunctions[junction.id] = relevantJunction
        return relevantJunctions
    
    @staticmethod
    def roundabout_road_read_lanes_from_file(startingNumberOfLanes : int, roadName : str) -> list[Road]:
         with open("jsons\\road.json", 'r') as file:
            
            data = json.load(file)
            roadsList = []
            roadData = data['roundabout_road']
            lanesData = roadData['lanes']   
            lanesDirection1 = []
            lanesDirection2 = []
            roundaboutData = roadData['roundabouts']
            images, imagesPos = RoadBuilder.load_lane_images(roadData)
            
            junctions = RoadBuilder.read_junctions_from_json(roadData)
            roadIndex = 0
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
                    relevantRoundabouts = RoadBuilder.create_roundabouts(roundaboutData, roadIndex)
                    road = Road(startingNumberOfLanes, roadDirections, images, imagesPos, relevantJunctions, relevantRoundabouts)
                    roadIndex += 1
                    roadsList.append(road)
                    lanesDirection1 = []
                    lanesDirection2 = []
                    
            return roadsList
    
    @staticmethod
    def create_roundabouts(roundabouts : dict, roadIndex : int) -> dict[int, Road.Roundabout]:
        roundaboutsDict = {}
        for roundaboutId, roundabout in enumerate(roundabouts.values()):
            if roadIndex in roundabout["roadsIndexes"]:
                path = roundabout["roundabout_path"]
                entryPaths = roundabout["entry_paths"]
                exitPaths = roundabout["exit_paths"]
                entryDict = entryPaths[str(roadIndex)]
                roundaboutsDict[roundaboutId] = Road.Roundabout(path, entryDict, exitPaths, roundaboutId)
        return roundaboutsDict           