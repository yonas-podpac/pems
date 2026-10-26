from datetime import datetime
import reflex as rx
from pems.helpers.database import db
from pems.helpers.extraction_handler import extraction_handler
from pems.helpers.extraction_analysis import analyser
from pems.helpers.data_handler import csv_to_df
# from pems.helpers.data_handler import dict_to_csv
from pems.states.table_state import TableState
from PIL import Image

class ExtractionState(TableState):
    """State for Tracking Changes to the Extractions Structure"""
    table: str = "extraction_analysis_history"
    is_processing: bool = False
    is_extraction_form_open: bool = False
    research_id: str = ""
    analysis_type: str = "Empty Extraction"
    capsule_type: str = ""
    lid_material: str = ""
    capsule_group: int = 0
    coffee_profile: str = "None"
    dose_weight: float = 0
    grind_setting: float = 0
    pack_selected: bool = False
    pack_date: datetime = datetime.today()
    grind_selected: bool = False
    grind_date: datetime = datetime.today()
    pending: bool = False
    filename: str = ""
    file: bytes = b""
    analysis_title: str = ""
    analysis_entry: dict = {}
    analysis_columns: list[dict] = []
    analysis_entries: list[dict] = []
    img: Image.Image
    img_label: str = ""

    @rx.var
    def form_complete(self) -> bool:
        return (
            self.research_id_selected and
            self.capsule_type_selected and
            self.lid_material_selected and
            self.capsule_group_selected and
            self.coffee_profile_selected and
            self.dose_weight_selected and
            self.grind_setting_selected and
            self.pack_date_selected and
            self.pack_date_selected and
            self.pending
        )
    
    @rx.var
    def research_id_selected(self) -> bool:
        return self.research_id != ""
    
    @rx.var
    def analysis_options(self) -> list[str]:
        return ["Empty Extraction", "Filled Extraction"]
    
    @rx.var
    def coffee_selected(self) -> bool:
        return self.analysis_type == "Filled Extraction"
    
    @rx.var
    def capsule_type_selected(self) -> bool:
        return self.capsule_type != ""
    
    @rx.var
    def lid_material_selected(self) -> bool:
        return self.lid_material != ""
    
    @rx.var
    def capsule_group_selected(self) -> bool:
        return self.capsule_group > 0
    
    @rx.var
    def coffee_profile_selected(self) -> bool:
        if self.coffee_selected:
            return self.coffee_profile != "None"
        return True

    @rx.var
    def dose_weight_selected(self) -> bool:
        if self.coffee_selected:
            return self.dose_weight > 0
        return True
    
    @rx.var
    def grind_setting_selected(self) -> bool:
        if self.coffee_selected:
            return self.grind_setting > 0
        return True

    @rx.var
    def pack_date_selected(self) -> bool:
        return self.pack_selected
    
    @rx.var
    def grind_date_selected(self) -> bool:
        if self.coffee_selected:
            return self.grind_selected
        return True
    
    # --- Extraction Filter Functions --- 
    @rx.event
    def set_filter_value(self, key: str, value: str):
        """Function for setting a specified filter value"""
        self.current_filters[key] = value
    
    @rx.event
    def apply_filter(self):
        """Function for Applying the Given Filters"""
        # TODO: implement

    @rx.event
    def delete_filter(self, key: str):
        """Function for deleting a filter"""
        self.current_filters.pop(key)
        self.load()
        self.apply_filter()

    # --- Form Functions ---
    @rx.event
    def load(self):
        """Function for Loading the Extraction State"""
        self.is_processing = False
        self.is_new_entry_form_open = False # TODO: is this variable required?
        self.is_extraction_form_open = False
        self.research_id = ""
        self.analysis_type = "Empty Extraction"
        self.capsule_type = ""
        self.lid_material = ""
        self.capsule_group = 0
        self.coffee_profile = "None"
        self.dose_weight = 0
        self.grind_setting = 0
        self.pack_selected = False
        self.pack_date = datetime.today()
        self.grind_selected = False
        self.grind_date = datetime.today()
        self.pending = False
        self.filename = ""
        self.file = b""

        extraction_handler.reset()
        self.columns = extraction_handler.columns()
        self.entries = extraction_handler.extraction_analysis_history
        self.filter_options = extraction_handler.options()
        self.filter_params = extraction_handler.params()

    @rx.event
    def open_extraction_form(self):
        """Function for Opening the Extraction Analysis Form"""
        self.is_extraction_form_open = True

    @rx.event
    def update_research_id(self, id: str):
        """Function for Updating the Research ID"""
        self.research_id = id

    @rx.event
    def update_analysis_type(self, a_type: str):
        """Function for Updating the Analysis Type"""
        self.analysis_type = a_type

    @rx.event
    def update_capsule_type(self, c_type: str):
        """Function for Updating the Capsule Type"""
        self.capsule_type = c_type

    @rx.event
    def update_lid_material(self, material: str):
        """Function for Updating the Lid Material"""
        self.lid_material = material

    @rx.event
    def update_capsule_group(self, group: str):
        """Function for Updating the Capsule Test Group"""
        self.capsule_group = int(group)

    @rx.event
    def update_coffee_profile(self, profile: str):
        """Function for Updating the Coffee Profile"""
        self.coffee_profile = profile

    @rx.event
    def update_dose_weight(self, weight: str):
        """Function for Updating the Dose Weight"""
        self.dose_weight = float(weight)
    
    @rx.event
    def update_grind_setting(self, grind: str):
        """Function for Updating the Grind Setting"""
        self.grind_setting = float(grind)

    @rx.event
    def update_pack_date(self, date: str):
        """Function for Updating the Pack Date"""
        self.pack_selected = True
        self.pack_date = datetime.strptime(date, "%Y-%m-%d")
    
    @rx.event
    def update_grind_date(self, date: str):
        """Function for Updating the Grind Date"""
        self.grind_selected = True
        self.grind_date = datetime.strptime(date, "%Y-%m-%d")

    @rx.event
    def delete_file(self):
        """Function for Deleting a File"""
        self.pending = False
        self.filename = ""
        self.file = b""
    
    @rx.event
    async def update_file(self, files: list[rx.UploadFile]):
        """Function for Uploading a CSV File"""
        file = files[0]
        # Ensure File is Strictly CSV
        if not file.filename.lower().endswith(".csv"):
            print(f"[REJECTED] '{file.filename}' is not a valid CSV file")
            return

        self.filename = file.filename
        self.pending = True
        self.file = await file.read()

    @rx.event
    def toggle(self):
        """Function for Toggling the Form"""
        self.is_extraction_form_open = not self.is_extraction_form_open

    @rx.event
    def submit_form(self, form_data: dict):
        """Function for Submitting new Extraction Analysis"""
        self.is_processing = True
        yield
        # TODO: Exception happening below
        if analyser.upload_data(self.file, not self.coffee_selected):
            analyser.upload_analysis_data(self.research_id, self.capsule_type, self.lid_material, self.capsule_group, self.grind_setting)
            analysis_csv = extraction_handler.dict_to_csv(analyser.analysis)

            db.store_to_bucket(
                bucket="raw-extraction-files",
                path=analyser.path,
                is_image=False,
                data=self.file
            )
            db.store_to_bucket(
                bucket="extraction-analysis-files",
                path=analyser.path,
                is_image=False,
                data=analysis_csv
            )
            img_paths = {}
            for p in analyser.plots.keys():
                db.store_to_bucket(
                    bucket="extraction-plots",
                    path=analyser.plot_paths[p],
                    is_image=True,
                    data=analyser.plots[p]
                )
                img_paths[p] = analyser.plot_paths[p]
            entry = {}
            for k in form_data.keys():
                if k!= "csv_uploader":
                    entry[k] = form_data[k]
            entry["path"] = analyser.path
            entry["plot_paths"] = img_paths
            extraction_entry = db.insert(self.table, entry)[0]
            db.add_local_object(self.table, extraction_entry)

        else:
            self.is_processing = False
        
        # Reset Variables
        self.load()
        
    # --- Analysis Functions ---
    @rx.event
    def link_data(self, index: int):
        """Function for Redirecting to Desired Extraction Analysis"""
        self.analysis_entry = self.entries[index]
        # Build Title for Analysis
        if self.analysis_entry["research_id"] == "RD-26-000-1":
            self.analysis_title = self.analysis_entry["research_id"] + ": " + self.analysis_entry["capsule_type"] + " with " + self.analysis_entry["lid_material"] + " Group " + str(self.analysis_entry["capsule_group"]) + " G" + str(self.analysis_entry["grind_setting"]) + " dosed at " + str(self.analysis_entry["dose_weight"]) + "g"
        elif self.analysis_entry["research_id"] == "RD-26-000-2":
            self.analysis_title = self.analysis_entry["research_id"] + ": " + self.analysis_entry["capsule_type"] + " with " + self.analysis_entry["lid_material"] + " Group " + str(self.analysis_entry["capsule_group"]) + " Empty"
        elif self.analysis_entry["research_id"] == "RD-26-000-i":
            self.analysis_title = self.analysis_entry["research_id"] + ": " + "Unofficial Research"
        elif self.analysis_entry["research_id"] == "RD-26-000-4":
            self.analysis_title = self.analysis_entry["research_id"] + ": " + self.analysis_entry["capsule_type"] + " with " + self.analysis_entry["lid_material"] + " Group " + str(self.analysis_entry["capsule_group"]) + " G" + str(self.analysis_entry["grind_setting"]) + " dosed at " + str(self.analysis_entry["dose_weight"]) + "g"

        # Retrieve Full Plot 
        curr_path = self.analysis_entry["plot_paths"]["full-plot"]
        img_bytes = db.retrieve_bytes_from_bucket("extraction-plots", curr_path)
        self.img = extraction_handler.img_bytes_to_image(img_bytes)
        self.img_label = "Full Plot"

        # Retrieve Capsule Extraction Data
        csv_bytes = db.retrieve_bytes_from_bucket("extraction-analysis-files", self.analysis_entry["path"])
        analysis_entries = extraction_handler.csv_from_bytes(csv_bytes)
        first_row = analysis_entries[0]
        self.analysis_entries = []
        self.analysis_columns = []

        # Build Column Information
        for k in first_row.keys():
            arr = k.split(" ")
            key = ""
            for idx, a in enumerate(arr):
                key += a if not "(" in a else ""
                if idx < len(arr) - 1:
                    key += "_"
            self.analysis_columns.append({"key": key, "label": k})
        
        # Build Entry Information
        for ae in analysis_entries:
            e = {}
            for k in ae:
                val: any
                try:
                    val = round(float(ae[k]), 0)
                except ValueError:
                    val = ae[k]
                e[[col["key"] for col in self.analysis_columns if col["label"] == k][0]] = val
            self.analysis_entries.append(e)

        # Redirect to Analysis Page
        return rx.redirect("/analysis")

    def display_plot(self, index: int):
        """Function for Displaying the Desired Analysis Plot"""
        curr_path = self.analysis_entry["plot_paths"][f"capsule-plot-{index + 1}"]
        img_bytes = db.retrieve_bytes_from_bucket("extraction-plots", curr_path)
        self.img = extraction_handler.img_bytes_to_image(img_bytes)
        self.img_label = f"Capsule Plot {index + 1}"

    def display_full_plot(self):
        """Function for Displaying the Full Plot"""
        curr_path = self.analysis_entry["plot_paths"]["full-plot"]
        img_bytes = db.retrieve_bytes_from_bucket("extraction-plots", curr_path)
        self.img = extraction_handler.img_bytes_to_image(img_bytes)
        self.img_label = "Full Plot"
