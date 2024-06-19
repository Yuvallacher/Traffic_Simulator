from datetime import datetime
import threading
import time
import pandas as pd
pd.set_option('display.precision', 2)
from calculations.pixels_calculations import PixelsConverter

class DataManager:
    def __init__(self, filename='simulation_data.xlsx', export_interval=5):
        self.filename = filename
        self.export_interval = export_interval
        self.stats_data = pd.DataFrame(columns=['Time Stamp', 'Average Speed', 'Density'])
        self.accidents_data = pd.DataFrame(columns=['Time Stamp', 'Vehicle Types', 'Speeds At Crash Time (km\h)'])
        self._start_export_thread()

    def _start_export_thread(self):
        self.export_thread = threading.Thread(target=self._export_data_periodically)
        self.export_thread.daemon = True  # Daemonize thread so it automatically dies when main program ends
        self.export_thread.start()

    def _export_data_periodically(self):
        while True:
            time.sleep(self.export_interval)
            self.export_to_excel()

    def update_stats(self, vehicles):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        avg_speed = sum(PixelsConverter.convert_pixels_per_frames_to_speed(vehicle.speed) for vehicle in vehicles) / len(vehicles) if vehicles else 0
        density = len(vehicles)
        new_data = pd.DataFrame({
            'Time Stamp': [current_time],
            'Average Speed': [avg_speed],
            'Density': [density]
        })
        self.stats_data = pd.concat([self.stats_data, new_data], ignore_index=True)

    def log_accident(self, vehicle_1_Type : str, vehicle_2_Type : str, vehicle_1_Speed : float, vehicle_2_Speed : float):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        vehicle_types = f"{vehicle_1_Type} and {vehicle_2_Type}"
        speeds = "{:.2f} and {:.2f}".format(vehicle_1_Speed, vehicle_2_Speed)
        new_data = pd.DataFrame({
            'Time Stamp': [current_time],
            'Vehicle Types': [vehicle_types],
            'Speeds At Crash Time (km\h)': [speeds]
        })
        self.accidents_data = pd.concat([self.accidents_data, new_data], ignore_index=True)

    def export_to_excel(self):
        with pd.ExcelWriter(self.filename, engine='openpyxl') as writer:
            self.stats_data.to_excel(writer, sheet_name='Statistics', index=False)
            self.accidents_data.to_excel(writer, sheet_name='Accidents', index=False)