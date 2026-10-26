import csv
from io import BytesIO, StringIO
import pandas as pd
from pandas.core.frame import DataFrame
from pems.components.objects import ExtractionAnalysisHistory
from pems.helpers.database import db
from PIL import Image

class ExtractionHandler:
    def __init__(self):
        self.__extraction_analysis_history = db.extraction_analysis_history
    
    @property
    def extraction_analysis_history(self) -> list[dict[str, any]]:
        results = []
        for eah in self.__extraction_analysis_history:
            entry = {}
            for k in eah.keys():
                entry[k] = eah[k]
            results.append(entry)
        return results

    # --- Table & Filter Functions ---
    def columns(self) -> list[dict[str, str]]:
        """Function for Retrieving Form Details by Columns"""
        return [
            {"label": "Research ID", "key": "research_id", "placeholder": "Enter the research ID", "type": "text", "step": ""},
            {"label": "Analysis Type", "key": "analysis_type", "placeholder": "", "type": "select", "step": ""},
            {"label": "Capsule Group", "key": "capsule_group", "placeholder": "1", "type": "number", "step": "1"},
            {"label": "Capsule Type", "key": "capsule_type", "placeholder": "Choose the type of the capsule being analysed", "type": "text", "step": ""},
            {"label": "Lid Material", "key": "lid_material", "placeholder": "Choose the lid material being analysed", "type": "text", "step": ""},
            {"label": "Coffee Profile", "key": "coffee_profile", "placeholder": "Choose the coffee profile being analysed", "type": "text", "step": ""},
            {"label": "Dose Weight (g)", "key": "dose_weight", "placeholder": "5.0", "type": "number", "step": "0.1"},
            {"label": "Grind Setting", "key": "grind_setting", "placeholder": "18.0", "type": "number", "step": "0.1"},
            {"label": "Pack Date", "key": "pack_date", "placeholder": "", "type": "date", "step": ""},
            {"label": "Grind Date", "key": "grind_date", "placeholder": "", "type": "date", "step": ""}
        ]
    
    def options(self) -> dict[str, list[str]]:
        """Function for Retrieving Filter Options by Columns"""
        results = {}
        for key in ["research_id", "analysis_type", "capsule_type", "lid_material", "coffee_profile", "grind_setting"]:
            for eah in self.__extraction_analysis_history:
                entry = eah[key]
                if results.keys().__contains__(key):
                    if not results[key].__contains__(entry):
                        results[key].append(entry)
                else:
                    results[key] = [entry]
        
        return results
    
    def params(self) -> list[dict[str, str]]:
        """Function for Retrieving Filter Parameters by Columns"""
        return [
            {"key": "research_id", "label": "Research ID"}, 
            {"key": "analysis_type", "label": "Analysis Type"}, 
            {"key": "capsule_type", "label": "Capsule Type"}, 
            {"key": "lid_material", "label": "Lid Material"}, 
            {"key": "coffee_profile", "label": "Coffee Profile"}, 
            {"key": "grind_setting", "label": "Grind Setting"}
        ]

    def reset(self):
        """Function for Re-retrieving DB Data"""
        self.__extraction_analysis_history = db.extraction_analysis_history
    
    # --- Conversion Functions ---
    def handle_testo_data(self, data: bytes) -> DataFrame:
        """Function for Handling Teso Analyser Data and converting to Pandas DataFrame object"""
        raw_text = data.decode("utf-8", errors="ignore")
        rows = raw_text.splitlines()

        # Testo Data closes with rows with additional columns, find data column count
        col_count = len(rows[0].split(","))
        results = []
        for row in rows:
            if len(row.split(",")) == col_count:
                results.append(row)

        fixed_data = "\n".join(results)
        return pd.read_csv(StringIO(fixed_data))

    def dict_to_csv(self, data: dict) -> bytes:
        """Function for Converting Dict to CSV File"""
        return pd.DataFrame(data).to_csv(index=False).encode("utf-8")

    def csv_from_bytes(self, data: bytes) -> list[dict]:
        """Function for Converting Bytes into CSV File"""
        csv_string = data.decode("utf-8")
        return list(csv.DictReader(StringIO(csv_string)))
    
    def img_bytes_to_image(self, data: bytes) -> Image.Image | None:
        """Function for Converting Bytes into an Image"""
        try:
            return Image.open(BytesIO(data))
        except Exception as e:
            print(f"[ERROR] Could not load image bytes: {e}")
            return None

extraction_handler = ExtractionHandler()