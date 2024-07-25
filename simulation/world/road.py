#from simulation.world.Point import Point
from pygame.math import Vector2
from pygame.surface import Surface

class Road:
    def __init__(self, startingNumberOfLanes : int, lanes : list[list['Lane']], laneImages : list[Surface]):
        self.lanes = lanes
        self.numberOfDirections = len(lanes)
        self.currNumOfLanes = startingNumberOfLanes
        self.laneImages = laneImages
               
        
    def add_lane(self):
        if self.currNumOfLanes < self.maxNumOfLanes:
            self.currNumOfLanes += 1


    def remove_lane(self):
        if self.currNumOfLanes != 1:
            self.currNumOfLanes -= 1
            # TODO remove all vehicles on deleted lane
            

    class Lane:
        def __init__(self, listOfCoordinates : list[Vector2], availableLanesIndexes : list[int]):
            self.path = listOfCoordinates
            self.availableLanesIndexes = availableLanesIndexes



class RoadBuilder:
    staticmethod
    def create_road(filePath : str, startingNumberOfLanes=2) -> Road:
        if 'straight' in filePath:
            lanes = RoadBuilder.straight_road_read_lanes_from_file()
        elif 'curve' in filePath:
            lanes # TODO implement new functions
        
        images = RoadBuilder.load_lane_images(filePath)
        return Road(startingNumberOfLanes, lanes, images)
        
        
    staticmethod
    def straight_road_read_lanes_from_file(filePath) -> list[list[Road.Lane]]: # TODO implement and move to inheriting classes
        with open(filePath, 'r') as file:
            index = 0
            laneOneWay = []
            laneTwoWay = []
            
            lanes = [laneOneWay, laneTwoWay]
            for line in file:
                line = line.strip()
                coordinates = tuple(map(int, line.strip("()").split(',')))
                newLane = Road.Lane(coordinates, )
                
                if index % 2 == 0:
                    laneOneWay.append(coordinates)
                else:
                    laneTwoWay.append(coordinates)
                index += 1
                    
                # if line.startswith("lane"):
                #     lanes.append(list[Road.Lane])

                # elif line.startswith("("):
                #     # Extract the coordinates and convert them to a tuple of integers
                #     coordinates = tuple(map(int, line.strip("()").split(',')))
                #     lane.append(coordinates)
                # elif line == "":
                #     lanes.append()
                #     lane = []
                    
                         
                    
    
    
    
    staticmethod
    def load_lane_images(roadName : str) -> list[Surface]: # TODO implement and move to inheriting classes
        return 0


    def stam():
        # Read the file and extract lanes and segments correctly
        file_path = '/mnt/data/straight_road_lanes.txt'

        # Initialize an empty dictionary to store lanes and their coordinates
        lanes = {}

        # Read the file and process it
        with open(file_path, 'r') as file:
            current_lane = None
            segment = []
            for line in file:
                line = line.strip()
                if line.startswith("lane"):
                    if current_lane and segment:
                        lanes[current_lane].append(segment)
                    current_lane = line
                    lanes[current_lane] = []
                    segment = []
                elif line.startswith("("):
                    # Extract the coordinates and convert them to a tuple of integers
                    coordinates = tuple(map(int, line.strip("()").split(',')))
                    segment.append(coordinates)
                elif line == "" and current_lane and segment:
                    lanes[current_lane].append(segment)
                    segment = []
            
            # Add the last segment of the last lane if it exists
            if current_lane and segment:
                lanes[current_lane].append(segment)

        lanes




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