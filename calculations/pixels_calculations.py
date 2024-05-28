from world.World import World

class PixelsConverter:
    @staticmethod
    def convert_speed_to_pixels_per_frames(speed : float):
        car_speed_mps = speed * 1000 / 3600
        car_speed_ppf = car_speed_mps * World.PIXELS_PER_METER / World.FPS
        return car_speed_ppf
        
    
    @staticmethod
    def convert_pixels_per_frames_to_speed(car_speed_ppf: float):
        car_speed_mps = car_speed_ppf * World.FPS / World.PIXELS_PER_METER
        car_speed_kph = car_speed_mps * 3600 / 1000
        return car_speed_kph