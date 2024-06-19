from simulation.world.Point import Point

class Road:
    def __init__(self, starting_position : Point, ending_position : Point, number_of_lanes : int, lane_width):
        self.starting_position = starting_position
        self.ending_position = ending_position
        self.numer_of_lanes = number_of_lanes
        self.lanes = []
        for i in range(number_of_lanes):
            lane_y = self.starting_position.y + 10 + (20 * i)
            self.lanes.append(Road.Lane(lane_width, Point(0, lane_y), Point(self.ending_position.x, lane_y)))
        
    def addLane(self):
        lane_y = self.starting_position.y + 10 + (20 * self.numer_of_lanes)
        self.lanes.append(Road.Lane(20, Point(0, lane_y), Point(self.ending_position, lane_y)))
        self.numer_of_lanes += 1
        
    def removeLane(self):
        self.lanes.remove(self.lanes[self.numer_of_lanes - 1])
        self.numer_of_lanes -= 1
        #TODO: delete cars on the removed lane
    
    def getLane(self, coordinates : Point):
        lane_y = coordinates.y
        for lane in self.lanes:
            if lane_y == lane.y:
                return self.lanes.index(lane)
        return -1
    
    class Lane:
        def __init__(self, lane_width, starting_position : Point, ending_position : Point):
            self.lane_width = lane_width
            self.starting_position = starting_position
            self.ending_position = ending_position
            self.y = starting_position.y