from io import BytesIO
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from datetime import datetime
import matplotlib.pyplot as plt
from pems.helpers.extraction_handler import extraction_handler
# from pems.helpers.data_handler import fix_csv_to_df
# from scipy.signal import find_peaks, peak_widths

class ExtractionAnalyser:
    def __init__(self):
        self.__plots = {}
        self.__plot_paths = {}
        self.__analysis = {}
        self.__dir = ""
        self.__filename = ""

    @property
    def plots(self) -> dict[str, BytesIO]:
        return self.__plots
    
    @property
    def plot_paths(self) -> dict[str, str]:
        return self.__plot_paths
    
    @property
    def analysis(self) -> dict[str, list]:
        return self.__analysis

    @property
    def path(self) -> str:
        return self.__dir + "/" + self.__filename

    def upload_data(self, data: bytes, empty: bool) -> bool:
        # df = extraction_handler.handle_testo_data(data)
        try:
            df = self.__clean_data(extraction_handler.handle_testo_data(data))
            capsules = self.__extract_each_capsule(df)
            print(f"Number of Capsules Analysed: {len(capsules)}")
            self.__plots = {
                "full-plot": self.__generate_plot(df)
            }
            self.__analysis = {
                "Peak Pressure (kPa)": [],
                "Extraction Time (s)": [],
                "Profile": []    
            }
            for idx, capsule in enumerate(capsules):
                peak_data = self.__empty_peak_finder(capsule) if empty else self.__peak_finder(capsule)
                self.__analysis["Peak Pressure (kPa)"].append(peak_data["peak"])
                self.__analysis["Extraction Time (s)"].append(peak_data["extraction_time"])
                self.__analysis["Profile"].append(peak_data["classification"])
                self.__plots[f"capsule-plot-{idx + 1}"] = self.__generate_plot(capsule)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to process extraction data: {e}")
            return False

    def upload_analysis_data(
            self,
            research_id: str,
            capsule_type: str,
            lid_material: str,
            capsule_group: str,
            grind_setting: float
    ):
        """Function for Setting up Local Variables"""
        self.__dir = research_id
        self.__filename = "g" + str(grind_setting)

        # Handle Capsule Types
        if "bisio" in capsule_type.lower():
            self.__filename += "bic" if "industrial" in capsule_type.lower() else "bhc"
            self.__filename += "v9" if "v9" in capsule_type.lower() else ""
        elif "biocaps" in capsule_type.lower():
            self.__filename += "bc"
        elif "vegecaps" in capsule_type.lower():
            self.__filename += "vc"

        # Handle Lid Material
        if "faux" in lid_material.lower():
            self.__filename += "fk"
        elif "white" in lid_material.lower():
            self.__filename += "wk"
        else:
            self.__filename += "al"

        # Handle Capsule Group
        self.__filename += str(capsule_group)

        # Handle Plots
        for p in self.__plots.keys():
            self.__plot_paths[p] = self.__dir + "/" + self.__filename + "-" + p

    def __generate_plot(self, df: DataFrame) -> bytes:
        plt.figure()
        df["pressure"].plot()
        plt.xlabel("Time (s)")
        plt.ylabel("Pressure (kPa)")
        img_buf = BytesIO()
        plt.savefig(img_buf, format="png")
        img_buf.seek(0)
        plt.close()

        return img_buf.getvalue()

    def __extract_each_capsule(self, data: DataFrame) -> list[DataFrame]:
        _list = []
        _new_df = []
        for i, row in data.iterrows():
            if row["pressure"] == 0:
                if len(_new_df) > 0:
                    df = []
                    for i, pressure in enumerate(_new_df):
                        df.append({"time": i + 1, "pressure": pressure})
                    _list.append(pd.DataFrame(df))
                    _new_df = []
            elif row["pressure"] > 0:
                _new_df.append(row["pressure"])
        
        return _list
    
    def __peak_finder(self, df: DataFrame) -> dict:
        # 1. Extract Fundamental Metrics
        time_data = df["time"].to_numpy()
        pressure_data = df["pressure"].to_numpy()
        area = np.trapezoid(y=pressure_data, x=time_data) 
        slopes = np.gradient(pressure_data, time_data)   

        max_rise_slope = np.max(slopes)
        max_drop_slope = np.min(slopes)
        peak_pressure = np.max(pressure_data)

        # Calculate asymmetry of the slopes
        # Overloads drop gradually, meaning magnitude of the drop is much less than the rise
        slope_ratio = max_rise_slope / abs(max_drop_slope)

        # 2. Track the Plateau behaviour near the peak
        # Find the points that are within 5% of the absolute peak for filled capsules
        near_peak_mask = pressure_data >= (peak_pressure * 0.95)
        peak_duration = time_data[near_peak_mask][-1] - time_data[near_peak_mask][0] if any(near_peak_mask) else 0

        # 3. Dynamic Thresholds
        # A standard plateau stays at the peak for a meaningful duration
        PLATEAU_DURATION_THRESHOLD = (np.max(time_data) - np.min(time_data)) * 0.15
        OVERLOAD_SLOPE_RATIO_THRESHOLD = 2.0 # Rise is at least twice as steep as the drop

        # 4. Classifcation Logic
        classification = ""
        if peak_duration > PLATEAU_DURATION_THRESHOLD:
            classification = "PLATEAU"
        elif slope_ratio > OVERLOAD_SLOPE_RATIO_THRESHOLD:
            classification = "OVERLOAD"
        else:
            classification = "ABNORMAL"
        
        return {
            "classification": classification,
            "extraction_time": int(df.size / 2),
            "peak": peak_pressure
        }
    
    def __empty_peak_finder(self, df: DataFrame) -> dict:
        # 1. Gather Baseline Metrics
        pressure_data = df["pressure"].to_numpy()
        time_data = df["time"].to_numpy()
        peak_pressure = np.max(pressure_data)
        peak_idx = np.argmax(pressure_data)
        slopes = np.gradient(pressure_data, time_data)

        # 2. Establish context-aware dynamic threshold
        HIGH_PRESSURE_CEILING = 1000
        SLOPE_FLAT_THRESHOLD = 0.05

        classification = "ABNORMAL"
        
        # 3. Classify Prodiles
        # High Pressure Profile Check
        # Condition: Absolute Value is extremely high, and plateaus near maximum
        if peak_pressure >= HIGH_PRESSURE_CEILING:
            classification = "HIGH PRESSURE EXTRACTION"
            # near_max_mask = pressure_data >= (peak_pressure * 0.92)
            # plateau_duration = time_data[near_max_mask][-1] - time_data[near_max_mask[0]] if any(near_max_mask) else 0
            # print(plateau_duration)
            # print(f"Time Data Length: {len(time_data)}")

            # # If it holds that high point for more than 10% of total runtime, it's high pressure
            # if plateau_duration > (np.max(time_data) - np.min(time_data)) * 0.10:
            #     classification = "HIGH PRESSURE EXTRACTION"
        # Regular Profile Check
        # Condition: It hits a minor peak
        if peak_pressure < HIGH_PRESSURE_CEILING:
            classification = "REGULAR"
        
        # 4. Get Extraction Time
        irregular = classification != "REGULAR"
        e_time = 0
        for idx, row in df.iterrows():
            if not irregular and row["pressure"] > 50:
                e_time += 1
        
        return {
            "classification": classification,
            "extraction_time": int(df.size / 2) if irregular else e_time,
            "peak": peak_pressure
        }

    def __clean_data(self, data: DataFrame) -> DataFrame:
        columns = list(data.columns.values)
        datetimeCol, pressureCol = columns[0], columns[1]
        df = []

        for i, row in data.iterrows():
            if self.__is_valid_datetime(str(row[datetimeCol])):
                df.append({"datetime": row[datetimeCol], "pressure": float(row[pressureCol]) * 100 if float(row[pressureCol]) >= 0 else 0})

        return pd.DataFrame(df)

    def __is_valid_datetime(self, date: str) -> bool:
        try:
            return bool(datetime.strptime(date, "%d/%m/%Y %H:%M:%S"))
        except ValueError:
            try:
                return bool(datetime.strptime(date, "%d/%m/%Y %H:%M"))
            except ValueError:
                return False

analyser = ExtractionAnalyser()