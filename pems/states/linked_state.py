import reflex as rx
from pems.helpers.database import db
from pems.helpers.extraction_analysis import analyser
from pems.helpers.data_handler import dict_to_csv
from PIL import Image

class LinkedState(rx.State):
    """"""
    # Define State Variables
    table: str = ""
    analysis_title: str = ""
    is_form_open: bool = False              # Dialog control flag
    is_processing: bool = False             # Processing CSV data flag
    current_record: dict[str, str] = {}     # Form tracking string-dictionary
    current_value: dict[str, float] = {}    # Form tracking number-dictionary
    current_check: dict[str, bool] = {}     # Form tracking boolean-dictionary
    pending_files: list[str] = []           # List of pending files
    csv_bytes: bytes = b""             # List of csv files in bytes
    filter_options: dict[str, list[str]] = {}
    filter_params: list[dict[str, str]] = []
    current_filters: dict[str, str] = {}
    columns: list[dict] = []
    entries: list[dict] = []
    analysis_entry: dict = {}
    analysis_columns: list[dict] = []
    analysis_entries: list[dict] = []
    img: Image.Image
    img_label: str = ""

    # --- Form Functions ---
    def set_record_field(self, key: str, value: any, input_type: str):
        """Function to safely mutate specific dynamic fields inside the active record proxy"""
        if input_type == "number":
            self.current_value[key] = value
        elif input_type == "checkbox":
            self.current_check[key] = value
        else:
            self.current_record[key] = value

    def toggle_form(self):
        """Function for opening or closing the form dialog box"""
        self.is_form_open = not self.is_form_open
        self.is_processing = False
        if not self.is_form_open:
            self.current_record = {} # Clears inputs on close
    
    def handle_add_click(self):
        """"""
        self.current_record = {col["key"]: "" for col in self.columns}
        self.is_form_open = True

    def set_filter_value(self, key: str, value: str):
        self.current_filters[key] = value

    def apply_filter(self):
        """Function to apply the given filters"""
        current_filtered_entries = []
        buffer = []
        if len(self.current_filters.keys()) > 0:
            for idx, filter in enumerate(self.current_filters.keys()):
                column = [col for col in self.columns if col["key"] == filter][0]
                if len(current_filtered_entries) == 0 and idx > 0:
                    current_filtered_entries = []
                    break
                elif len(current_filtered_entries) > 0 and idx > 0:
                    buffer = [e for e in current_filtered_entries if e[column["key"]] == self.current_filters[filter]]
                    current_filtered_entries = buffer
                elif len(current_filtered_entries) == len(self.entries) or idx == 0:
                    buffer = [e for e in self.entries if e[column["key"]] == self.current_filters[filter]]
                    current_filtered_entries = buffer
            self.entries = current_filtered_entries

    def delete_filter(self, key: str):
        self.current_filters.pop(key)
        self.load(self.table)
        self.apply_filter()

    def load(self, table: str):
        self.table = table
        self.columns = db.columns(table)
        self.entries = db.select(table)
        self.filter_options = db.filter_options(table)
        self.filter_params = db.filter_params(table)

    async def handle_file_select(self, files: list[rx.UploadFile]):
        """Event handler for CSV bulk parser ingestion"""
        self.pending_files = []
        for file in files:
            # Ensure file is strictly csv
            if not file.filename.lower().endswith(".csv"):
                print(f"[REJECTED]: '{file.filename}' is not a valid csv file")
                continue
                
            self.pending_files.append(file.filename)
        self.csv_bytes = await files[0].read()

    def clear_pending_files(self):
        """Event handler to delete pending files"""
        self.pending_files = []
        self.csv_bytes = b""

    def submit_form(self, form_data: dict):
        if self.table == "extraction_analysis_history":
            if analyser.upload_data(self.csv_bytes, "empty" in form_data["analysis_type"].lower()):
                self.is_processing = True
                analyser.upload_form_data(form_data)
                analysis_csv = dict_to_csv(analyser.analysis)
                
                db.store_csv_to_bucket(
                    bucket="raw-extraction-files",
                    path=analyser.path,
                    data=self.csv_bytes
                )
                db.store_csv_to_bucket(
                    bucket="extraction-analysis-files",
                    path=analyser.path,
                    data=analysis_csv
                )
                img_paths = {}
                for p in analyser.plots.keys():
                    db.store_image_to_bucket(
                        path=analyser.plot_paths[p],
                        img=analyser.plots[p]
                    )
                    img_paths[p] = analyser.plot_paths[p]
                entry = {}
                for k in form_data.keys():
                    if k!= "csv_uploader":
                        entry[k] = form_data[k]
                entry["path"] = analyser.path
                entry["plot_paths"] = img_paths
                db.insert(self.table, entry)
        self.is_form_open = False
        self.csv_bytes = b""
        self.load(self.table)
        
    def link_data(self, index: int):
        self.analysis_entry = self.entries[index]
        # print(self.analysis_entry)
        if self.table == "extraction_analysis_history":
            if self.analysis_entry["research_id"] == "RD-26-000-1":
                self.analysis_title = self.analysis_entry["research_id"] + ": " + self.analysis_entry["capsule_type"] + " with " + self.analysis_entry["lid_material"] + " Group " + str(self.analysis_entry["capsule_group"]) + " G" + str(self.analysis_entry["grind_setting"]) + " dosed at " + str(self.analysis_entry["dose_weight"]) + "g"
            elif self.analysis_entry["research_id"] == "RD-26-000-2":
                self.analysis_title = self.analysis_entry["research_id"] + ": " + self.analysis_entry["capsule_type"] + " with " + self.analysis_entry["lid_material"] + " Group " + str(self.analysis_entry["capsule_group"]) + " Empty"
            self.img = db.retrieve_image_from_bucket(self.analysis_entry["plot_paths"]["full-plot"])
            self.img_label = "Full Plot"
            analysis_entries = db.retrieve_csv_from_bucket("extraction-analysis-files", self.analysis_entry["path"])
            first_row = analysis_entries[0]
            self.analysis_entries = []
            self.analysis_columns = []
            for k in first_row.keys():
                arr = k.split(" ")
                key = ""
                for idx, a in enumerate(arr):
                    key += a if not "(" in a else ""
                    if idx < len(arr) - 1:
                        key += "_"
                self.analysis_columns.append({"key": key, "label": k})
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
            return rx.redirect("/analysis")

    def display_plot(self, index: int):
        curr_path = self.analysis_entry["plot_paths"][f"capsule-plot-{index + 1}"]
        self.img = db.retrieve_image_from_bucket(curr_path)
        self.img_label = f"Capsule Plot {index + 1}"

    def display_full_plot(self):
        self.img = db.retrieve_image_from_bucket(self.analysis_entry["plot_paths"]["full-plot"])
        self.img_label = "Full Plot"
