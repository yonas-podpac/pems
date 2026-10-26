from datetime import datetime, timedelta
from io import BytesIO, StringIO
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from pems.helpers.database import db

class OEESummariser:
    def __init__(self):
        self.__production_id: str = ""
        self.__data: dict[str, list[dict[str, any]]] = {}
        self.__parameter_size: int = 0
        self.__insert_complete = False

    @property
    def insert_complete(self) -> bool:
        return self.__insert_complete

    def initialise_data(self, production_id: str, data: dict[str, list[bytes]], logs=False, schedule=False, summary=False) -> int:
        """Function for Initialising Data for the Summariser returning size of dataset entry"""
        self.__production_id = production_id
        self.__insert_complete = False
        for key, raw in data.items():
            self.process_data(key=key, raw=raw, logs=logs, schedule=schedule, summary=summary)
        for key in self.__data.keys():
            if key == "faults" or key == "asset_settings_changes":
                key_size = 6 * len(self.__data[key])
            elif key == "production_output":
                key_size = 7 * len(self.__data[key])
            self.__parameter_size += key_size

        return self.__parameter_size

    def process_data(self, key: str, raw: list[bytes], logs=False, schedule=False, summary=False) -> int:
        """Function for Inserting Data to Supabase"""
        # Case 1: Handle Nespresso Logs
        if "Nespresso" in [p.name for p in db.locations if p.id == self.__production_id][0] and logs:
            # Case 1.A: Handle Spreafico Logs
            if key == "spreafico":
                # Find Nespresso Spreafico ID & Last Date of Entry
                asset_id = [a.id for a in db.asset_registrar if a.manufacturer == "Spreafico" and a.location_id == self.__production_id][0]
                unit_id = [u.id for u in db.production_output_units if u.unit == "RTU"][0]
                last_output_date = self.__last_date("production_output", asset_id)
                last_fault_date = self.__last_date("faults", asset_id)

                # Convert Raw Data to DataFrame
                for file in raw:
                    summary_df = pd.read_excel(BytesIO(file), engine="openpyxl")
                    alarms_df = pd.read_excel(BytesIO(file), sheet_name="Alarms", engine="openpyxl")

                    # Collect Capsule Data from Summary DataFrame
                    good_products = 0
                    rejects = 0
                    date = datetime.today()
                    accounted_for = False
                    for i, row in summary_df.iterrows():
                        if row["Unnamed: 0"] == "Start Date":
                            date = row["Unnamed: 2"]
                            if date.date() <= last_output_date.date():
                                accounted_for = True
                                continue
                        if row["Unnamed: 0"] == "Good Products":
                            good_products = row["Unnamed: 2"]
                        if row["Unnamed: 0"] == "Rejects Products":
                            rejects = row["Unnamed: 2"]
                    # print(f"{date} | Good: {good_products} | Rejects: {rejects}")
                    if not accounted_for:
                        if not self.__data.keys().__contains__("production_output"):
                            self.__data["production_output"] = [{
                                "location_id": self.__production_id,
                                "asset_id": asset_id,
                                "timestamp": date.isoformat(),
                                "total": int(np.floor((good_products + rejects) / 10)),
                                "good": int(np.floor(good_products / 10)),
                                "rejected": int(np.floor(rejects / 10)),
                                "unit_id": unit_id
                            }]
                        else:
                            self.__data["production_output"].append({
                                "location_id": self.__production_id,
                                "asset_id": asset_id,
                                "timestamp": date.isoformat(),
                                "total": int(np.floor((good_products + rejects) / 10)),
                                "good": int(np.floor(good_products / 10)),
                                "rejected": int(np.floor(rejects / 10)),
                                "unit_id": unit_id
                            })

            # Case 1.B: Handle HMPS Logs
            elif key == "hmps":
                # Find Nespresso Spreafico ID & Last Date of Entry
                asset_id = [a.id for a in db.asset_registrar if a.manufacturer == "HMPS" and a.location_id == self.__production_id][0]
                unit_id = [u.id for u in db.production_output_units if u.unit == "RTU"][0]
                for idx, key in enumerate(["faults", "runtime", "settings"]):
                    # Case 1.B.A: Handling Fault Data from the HMPS
                    if key == "faults":
                        # Initialise Last Date from Table & Convert CSV to DataFrame
                        last_date = self.__last_date("faults", asset_id)
                        df = pd.read_csv(StringIO(raw[idx].decode("utf-8", errors="ignore")))

                        # Iterate over DataFrame Rows
                        for i, row in df.iterrows():
                            d = datetime.fromisoformat(row["time"])

                            # Only Include Data after Last Upload
                            if d.date() > last_date.date():
                                if not self.__data.keys().__contains__("faults"):
                                    self.__data["faults"] = [{
                                        "location_id": self.__production_id,
                                        "asset_id": asset_id,
                                        "timestamp": row["time"],
                                        "fault_code": "",
                                        "duration_seconds": int(60 * float(self.__time_correction(row["mins"]))),
                                        "description": row["message"]
                                    }]
                                else:
                                    self.__data["faults"].append({
                                        "location_id": self.__production_id,
                                        "asset_id": asset_id,
                                        "timestamp": row["time"],
                                        "fault_code": "",
                                        "duration_seconds": int(60 * float(self.__time_correction(row["mins"]))),
                                        "description": row["message"]
                                    })

                    # Case 1.B.B: Handling Runtime Data from the HMPS
                    elif key == "runtime":
                        # Initialise Last Date from Table, Retrieve Appropriate Unit ID & Convert CSV to DataFrame
                        last_date = self.__last_date("production_output", asset_id)
                        df = pd.read_csv(StringIO(raw[idx].decode("utf-8", errors="ignore")))

                        # Iterate over DataFrame Rows
                        for i, row in df.iterrows():
                            d = datetime.fromisoformat(row["adj_time"])

                            # Only Include Data after Last Upload
                            if d.date() > last_date.date() and row["products"] > 0:
                                if not self.__data.keys().__contains__("production_output"):
                                    self.__data["production_output"] = [{
                                        "location_id": self.__production_id,
                                        "asset_id": asset_id,
                                        "timestamp": row["adj_time"],
                                        "total": int(row["products"]) / 10,
                                        "good": int(row["products"]) / 10,
                                        "rejected": 0,
                                        "unit_id": unit_id
                                    }]
                                else:
                                    self.__data["production_output"].append({
                                        "location_id": self.__production_id,
                                        "asset_id": asset_id,
                                        "timestamp": row["adj_time"],
                                        "total": int(row["products"]) / 10,
                                        "good": int(row["products"]) / 10,
                                        "rejected": 0,
                                        "unit_id": unit_id
                                    })

                    # Case 1.B.C: Handling Settings Data from the HMPS
                    elif key == "settings":
                        # Initialise Last Date from Table & Convert CSV to DataFrame
                        last_date = self.__last_date("asset_settings_changes", asset_id)
                        df = pd.read_csv(StringIO(raw[idx].decode("utf-8", errors="ignore")))

                        # Iterate over DataFrame Rows
                        for i, row in df.iterrows():
                            d = datetime.fromisoformat(row["timestamp"])

                            # Only Include Date after Last Upload
                            if d.date() > last_date.date():
                                if not self.__data.keys().__contains__("asset_settings_changes"):
                                    self.__data["asset_settings_changes"] = [{
                                        "location_id": self.__production_id,
                                        "asset_id": asset_id,
                                        "timestamp": row["timestamp"],
                                        "setting_name": row["setting"],
                                        "old_value": row["old"],
                                        "new_value": row["new"]
                                    }]
                                else:
                                    self.__data["asset_settings_changes"].append({
                                        "location_id": self.__production_id,
                                        "asset_id": asset_id,
                                        "timestamp": row["timestamp"],
                                        "setting_name": row["setting"],
                                        "old_value": row["old"],
                                        "new_value": row["new"]
                                    })

                # Return Size of Parameters to Insert to Table
                if self.__data.keys().__contains__("asset_settings_changes"):
                    return 6 * len(self.__data["asset_settings_changes"])
                return 0

        # Case 2: #TODO: implement additional cases

    def upload_data(self) -> int:
        """Function for Uploading Data to the Database, returning number of Parameters Submitted"""
        # Check if all keys are complete
        if len(self.__data.keys()) == 0:
            self.__insert_complete = True
            return 0

        # Find the Maximum number of Rows that can be Submitted
        key = list(self.__data.keys())[0]
        num_columns = len(self.__data[key][0])
        max_num_rows = int(np.floor(db.PARAMETER_MAXIMUM / num_columns))

        # Build List of Entries for Upload
        files_for_upload = []
        print(f"Number of Rows Left for {key}: {len(self.__data[key])}")
        for i in range(max_num_rows):
            if len(self.__data[key]) > 0:
                files_for_upload.append(self.__data[key].pop(0))
            else:
                break

        # Check if Key-Entries are Empty
        if len(self.__data[key]) == 0:
            self.__data.pop(key)

        # Insert Entries and Return Progress
        db.insert_multiple(key, files_for_upload)
        return num_columns * len(files_for_upload)

    def __last_date(self, table: str, asset_id: str) -> datetime:
        """Function for Getting the Last Date for a Given Table"""
        try:
            return datetime.fromisoformat(db.select(table, columns="timestamp.max()", filters={"location_id": self.__production_id, "asset_id": asset_id})[0]["max"])
        except Exception:
            return datetime.strptime("14/10/1066", "%d/%m/%Y")

    def __time_correction(self, item: any) -> float:
        """Function for Correcting Time Values"""
        # Convert NaN Values to 0
        if np.isnan(item):
            return 0
        
        return item

oee_summariser = OEESummariser()