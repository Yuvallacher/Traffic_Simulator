import Point
import sympy as sp

class Road:
    
    def __init__(self, function: str):
        self.roadFunction = function
        self.listOfRoadPoints = []
        x = sp.symbols('x')
        function_expr = sp.sympify(self.roadFunction)
        for xValue in range(1080):
            currentPoint = Point.Point(xValue, function_expr.subs(x, xValue))
            self.listOfRoadPoints.append(currentPoint)