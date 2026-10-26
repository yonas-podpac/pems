import reflex as rx
from pems.helpers.asset_handler import asset_handler
from pems.helpers.data_handler import csv_to_df
from pems.states.table_state import TableState
from pems.helpers.database import db
from pems.components.objects import Asset, Station

class AssetState(TableState):
    """State for Tracking Changes to the Assets Structure"""
    table: str = "asset_registrar"
    asset_entry: dict = {}
    asset: Asset = None
    asset_title: str = ""
    asset_subtitle: str = ""
    asset_columns: list[dict] = []
    asset_entries: list[dict] = []
    pending_files: list[str] = []
    csv_bytes: bytes = b""

    # --- Asset Registrar State Variables ---
    @rx.var
    def file_pending(self) -> bool:
        return len(self.pending_files) == 1
    
    @rx.var
    def pending_file(self) -> str:
        if len(self.pending_files) == 1:
            return self.pending_file[0]
        return ""
    
    # --- Asset Registrar Action Bar Functions ---
    async def handle_file_select(self, files: list[rx.UploadFile]):
        """Event Handler for CSV Parser"""
        self.pending_files = []
        for file in files:
            # Ensure File is Strictly CSV
            if not file.filename.lower().endswith(".csv"):
                print(f"[REJECTED] '{file.filename}' is not a valid CSV file")
                continue

            self.pending_files.append(file.filename)
        
        self.csv_bytes = await files[0].read()

    def clear_pending_files(self):
        """Event Handler to delete pending files"""
        self.pending_files = []
        self.csv_bytes = b""

    def handle_upload_file(self):
        """Event Handler for uploading file"""
        df = csv_to_df(self.csv_bytes)

    # --- Asset Registrar Functions ---
    def load(self):
        self.is_loaded = True
        self.is_curr_entry_form_open = False
        self.is_new_entry_form_open = False
        self.is_delete_entry_window_open = False
        self.selected_row_index = -1
        self.current_filters = {}
        self.columns = asset_handler.columns(assets=True)
        self.entries = asset_handler.entries(assets=True)
        self.form_options = asset_handler.options(assets=True)
        toggles = asset_handler.toggles(assets=True)
        self.form_toggles = {}
        for k in toggles.keys():
            self.form_toggle_on_vals[k] = toggles[k][0]
            self.form_toggle_off_vals[k] = toggles[k][1]
            self.form_toggles[k] = False
        self.filter_options = asset_handler.filters(assets=True)
        self.filter_params = asset_handler.params(assets=True)

    def submit_new_entry_form(self, form_data:dict):
        """Function to save New Entry to Table & Update Supabase"""
        asset_handler.insert(form_data, assets=True)
        self.load()

    def submit_curr_entry_form(self, form_data: dict):
        """Function to save Current Entry to Table & Update Supabase"""
        asset_handler.update(self.selected_row_index, form_data, filters=self.current_filters, assets=True)
        self.load()

    def handle_delete_click(self, index):
        """Function to remove selected row entry from table & supabase"""
        self.selected_row_index = index
        self.is_delete_entry_window_open = True
        self.asset_title = self.entries[index]["manufacturer"] + ": " + self.entries[index]["name"]
    
    def cancel_delete_click(self):
        """Function for Stopping the Entry Delete"""
        self.selected_row_index = -1
        self.is_delete_entry_window_open = False
        self.asset_title = ""

    def confirm_delete_click(self):
        """Function for Deleting Entry from Table & Supabase"""
        asset_handler.delete(self.selected_row_index, filters=self.current_filters, assets=True)
        self.load()

    def link_data(self, index: int):
        self.asset_entry = self.entries[index]
        self.asset = asset_handler.find_asset(self.asset_entry["name"], self.asset_entry["serial_number"])
        self.asset_title = self.asset_entry["location"] + ": " + self.asset_entry["manufacturer"]
        self.asset_subtitle = "Tracking stations for the " + self.asset.name + "; Model: " + self.asset.model + "; Serial Number: " + self.asset.serial_number
        self.asset_entries = asset_handler.entries(stations=True, asset_id=self.asset.id)
        self.asset_columns = asset_handler.columns(stations=True)

        return rx.redirect("/stations")
    
    #  --- Asset-Stations Functions ---
    def handle_station_add(self):
        """Function to add a new station to the asset"""
        pass
    
    def handle_station_edit(self, idx: int):
        """Function to Edit the Station Selected"""
        print(self.asset_entries[idx])

    def handle_station_delete(self, idx: int):
        """Function to Delete the Station Selected"""
        print(self.asset_entries[idx])

    # --- Asset-Stations Filter Functions ---
    def set_filter_value(self, key: str, value: str):
        """Function to set the value for a specified fitler key"""
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
        self.load()
        self.apply_filter()
