from pygame import Vector2
import json

class Junction:
    def __init__(self, junction_dict : dict[int,dict[int,list[Vector2]]]):
        self.junctionDict = junction_dict
        


    def get_possible_junction_turns(self, laneId : int):
        return self.junctionDict[laneId]

    def check_if_target_position_is_start_of_junction_turn(self, laneId : int, targetPos : Vector2):
        turnsList = []
        possibleTurns = self.junctionDict.get(laneId)
        if possibleTurns is not None:
            for coordinateList in possibleTurns.values:
                if coordinateList[0] == targetPos: # first index of a junction turn is a vehicle target pos
                    turnsList.append(coordinateList)
                
        return turnsList
             








class JunctionBuilder:
    # dictionary of lane id keys to dictionaries of lane id keys and their list of coordinates
    @staticmethod
    def create_junction_from_file(roadName : str) -> dict[int,dict[int,list[Vector2]]]: 
        with open("jsons\\road.json", 'r') as file:
            data = json.load(file)
            road_data = data[roadName]
            junction_data = road_data['roads_junction']
            junction_dict = {}
            
            for key, value in junction_data.items():
                main_key, sub_key = map(int, key.strip("()").split(","))
                if main_key not in junction_dict:
                    junction_dict[main_key] = {}
                
                junction_dict[main_key][sub_key] = value[1]
                
            return junction_dict