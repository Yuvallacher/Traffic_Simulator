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
               
        
    def add_lane(self):
        if self.currNumOfLanes < self.maxNumOfLanes:
            self.currNumOfLanes += 1


    def remove_lane(self):
        if self.currNumOfLanes != 1:
            self.currNumOfLanes -= 1
            # TODO remove all vehicles on deleted lane
        
    def get_target_position(self, directionIndex : int, laneIndex : int, currentTargetPositionIndex : int) -> Vector2:
        path = self.allLanesInRoad[directionIndex][laneIndex].path
        if currentTargetPositionIndex + 1 < len(path):
            return path[currentTargetPositionIndex] #TODO maybe change +1 to take speed into consideration
        else:
            return path[-1]

    class Lane:
        def __init__(self, listOfCoordinates : list[Vector2]):
            self.path = listOfCoordinates
            self.startingPoint = listOfCoordinates[0]
        
        


class RoadBuilder:
    @staticmethod
    def create_road(roadName : str, startingNumberOfLanes=2) -> Road:
        if 'straight' in roadName:
            lanes = RoadBuilder.straight_road_read_lanes_from_file(startingNumberOfLanes)
        elif 'curved' in roadName:
            lanes # TODO implement new functions
        
        images, imagesPos = RoadBuilder.load_lane_images(roadName)
        return Road(startingNumberOfLanes, lanes, images, imagesPos)
        
        
    @staticmethod
    def straight_road_read_lanes_from_file(startingNumberOfLanes : int) -> list[list[Road.Lane]]: # TODO implement and move to inheriting classes
        with open("jsons\\road.json", 'r') as file:
            data = json.load(file)

            road_data = data['straight_road']
            lanes_data = road_data['lanes']

            lanes_direction_1 = []
            lanes_direction_2 = []
            
            #TODO add a way to limit user - only 1 or 2 lanes in each direction
            
            for idx, lane_coordinates in enumerate(lanes_data):
                if idx < 2 * startingNumberOfLanes:
                    path = [Vector2(coord) for coord in lane_coordinates]
                    lane = Road.Lane(path)

                    # in the JSON, odd-indexed lanes are put in lane_direction_2 (that means left-to-right driving direction)
                    if idx % 2 != 0:
                        lanes_direction_1.append(lane)
                    else:
                        lanes_direction_2.append(lane)

            return [lanes_direction_1, lanes_direction_2]
    
    
    @staticmethod
    def load_lane_images(roadName : str) -> list[list]: # TODO implement and move to inheriting classes
        with open("jsons\\road.json", 'r') as file:
            data = json.load(file)
            if "straight" in roadName:
                roadData = data["straight_road"]
            elif "curved" in roadName:
                roadData #TODO implement
            
            imagesPaths = roadData["images_path"]
            imagesScales = roadData["images_scales"]
            imagesPos = roadData["image_pos"]
            images = []
            for index, imagePath in enumerate(imagesPaths):
                images.append(pygame.transform.scale(pygame.image.load(imagePath), imagesScales[index])) #TODO add scale? if so, what scale            
            return [images, imagesPos]

            # pygame.transform.scale(pygame.image.load('carPictures\\redCar.png'), (25, 15))




# class Road:
#     def __init__(self, starting_position : Point, ending_position : Point, number_of_lanes : int, lane_width):
#         self.starting_position = starting_position
#         self.ending_position = ending_position
#         self.numer_of_lanes = number_of_lanes
#         self.lanes = []
#         for i in range(number_of_lanes):
#             lane_y = self.starting_position.y + 10 + (20 * i)
#             self.lanes.append(Road.Lane(lane_width, Point(0, lane_y), Point(self.ending_position.x, lane_y)))
        
#     def addLane(self):
#         lane_y = self.starting_position.y + 10 + (20 * self.numer_of_lanes)
#         self.lanes.append(Road.Lane(20, Point(0, lane_y), Point(self.ending_position, lane_y)))
#         self.numer_of_lanes += 1
        
#     def removeLane(self):
#         self.lanes.remove(self.lanes[self.numer_of_lanes - 1])
#         self.numer_of_lanes -= 1
#         #TODO: delete cars on the removed lane
    
#     # get index of lane based on specific point
#     def getLane(self, coordinates : Vector2):
#         lane_y = coordinates.y
#         for lane in self.lanes:
#             if lane_y == lane.y:
#                 return self.lanes.index(lane)
#         return -1
    
#     class Lane:
#         def __init__(self, lane_width, starting_position : Point, ending_position : Point):
#             self.lane_width = lane_width
#             self.starting_position = starting_position
#             self.ending_position = ending_position
#             self.y = starting_position.y