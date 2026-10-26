import reflex as rx
from pems.helpers.database import db

class TableState(rx.State):
    """State for tracking changes to table structures"""
    # Define State Variables
    is_loaded: bool = False
    is_new_entry_form_open: bool = False
    is_curr_entry_form_open: bool = False
    is_delete_entry_window_open: bool = False
    selected_row_index: int = -1
    # is_form_open: bool = False                  # Dialog control flag
    form_options: dict[str, list[str]] = {}
    form_toggles: dict[str, bool] = {}
    form_toggle_on_vals: dict[str, str] = {}
    form_toggle_off_vals: dict[str, str] = {}
    form_toggle_vals: dict[str, str] = {}
    default_options: dict[str, str] = {}
    filter_options: dict[str, list[str]] = {}   # Filter options paired to filter key
    filter_params: list[dict[str, str]] = []    # List of filter parameters
    current_filters: dict[str, str] = {}        # Filter tracking dictionary
    columns: list[dict] = []                    # Column data for header
    entries: list[dict] = []                    # Entry data for table population
    
    # --- Form functions ---
    # def toggle_form(self):
    #     """Function for opening or closing the form dialog box"""
    #     self.is_form_open = not self.is_form_open

    def toggle_new_entry_form(self):
        """Function for Opening or Closing the New Entry Form"""
        self.is_new_entry_form_open = not self.is_new_entry_form_open
    
    def toggle_curr_entry_form(self):
        """Function for Opeing or Closing the Current Entry Form"""
        self.is_curr_entry_form_open = not self.is_curr_entry_form_open
    
    def handle_add_click(self):
        """Function to Open the New Entry Form"""
        # self.is_form_open = True
        self.is_new_entry_form_open = True

    @rx.event
    def handle_toggle(self, key: str):
        """Function to handle toggle switches on forms"""
        curr = self.form_toggles[key]
        self.form_toggles[key] = not curr
        toggled_on = self.form_toggle_on_vals[key]
        toggled_off = self.form_toggle_off_vals[key]
        self.form_toggle_vals[key] = toggled_on if curr else toggled_off

    # --- Table functions ---
    def handle_edit_click(self, index: int):
        """Function to Edit a Row from the Table"""
        self.is_curr_entry_form_open = True
        self.selected_row_index = index
        entry = self.entries[index]
        print(entry)
        for k in entry:
            self.default_options[k] = entry[k]
            if k in self.form_toggles.keys():
                self.form_toggles[k] = self.form_toggle_on_vals[k] == entry[k]

    @rx.event
    async def handle_csv_upload(self, files: list[rx.UploadFile]):
        """Event handler for CSV file parser ingestion"""
        for file in files:
            # Ensure file is strictly CSV
            if not file.filename.lower().endswith(".csv"):
                print(f"[REJECTED]: '{file.filename}' is not a valid CSV file")
                continue
            print(f"\n--- Ingesting Stream Target: {file.filename} ---")
            
            # Extract Binary Payload from Memory Stream Buffer
            file_bytes = await file.read()

            try:
                success = db.insert_by_csv_dump(file.filename.split(".")[0], file_bytes.decode("utf-8"))
            except UnicodeDecodeError:
                print(f"[ERROR]: Failed to decode '{file.filename}'. File content may be corrupted or binary.")
