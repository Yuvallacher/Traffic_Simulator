from world.World import World

class PixelsConverter:
    @staticmethod
    def convert_speed_to_pixels_per_frames(speed : int):
        car_speed_mps = speed * 1000 / 3600
        car_speed_ppf = car_speed_mps * World.PIXELS_PER_METER / World.FPS
        