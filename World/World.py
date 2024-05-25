class World:
    PIXELS_PER_METER = 5
    FPS = 60
    def __init__(self, maxSpeed, frequency, politeness):
        self.maxSpeed = maxSpeed
        self.frequency = frequency
        self.politeness = politeness
        