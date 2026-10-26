from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from enum import Enum
from pems.components.objects import Location, Asset
from pems.helpers.database import db
from pems.helpers.oee_summariser import oee_summariser
import reflex as rx

class Production(Enum):
    NESPRESSO = 1
    KFEE = 2
    ROASTING = 3

class FormType(Enum):
    LOG = 1
    SCHEDULE = 2
    SUMMARY = 3

class OEEFormState(rx.State):
    # Parameters for Submission
    form_open: bool = False
    submitting: bool = False
    production: Production = Production.NESPRESSO
    form_type: FormType = FormType.LOG
    production_room: Location = Location("", "", False)
    start_date: datetime = datetime.today()
    end_date: datetime = datetime.today()
    message: str = ""

    # File Variables
    current_key: str = ""
    file_keys: list[str] = []
    key_titles: dict[str, str] = {}
    file_indices: dict[str, list[int]] = {}
    file_names: dict[str, list[str]] = {}
    file_raw: dict[str, list[bytes]] = {}
    upload_status: dict[str, list[bool]] = {}

    # Page Variables
    current_step: int = 0

    # --- State Variables ---
    @rx.var
    def total_steps(self) -> int:
        return len(self.file_keys) + 2 # Plus 2 pages for parameters and submission

    @rx.var
    def is_nespresso(self) -> bool:
        return self.production == Production.NESPRESSO

    @rx.var
    def is_kfee(self) -> bool:
        return self.production == Production.KFEE

    @rx.var
    def is_roasting(self) -> bool:
        return self.production == Production.ROASTING

    @rx.var
    def is_logs(self) -> bool:
        return self.form_type == FormType.LOG

    @rx.var
    def is_schedule(self) -> bool:
        return self.form_type == FormType.SCHEDULE

    @rx.var
    def is_summary(self) -> bool:
        return self.form_type == FormType.SUMMARY

    @rx.var
    def production_rooms(self) -> list[str]:
        return [room.name for room in db.locations if room.is_production]

    @rx.var
    def production_room_repr(self) -> str:
        return self.production_room.name

    @rx.var
    def start_date_repr(self) -> str:
        return self.start_date.strftime("%Y-%m-%d")

    @rx.var
    def end_date_repr(self) -> str:
        return self.end_date.strftime("%Y-%m-%d")
    
    @rx.var
    def upload_complete(self) -> bool:
        if len(self.file_keys) == 0:
            return False
        check = True
        for k in self.file_keys:
            if not self.upload_status[k]:
                check = False
                break
        return check

    @rx.var
    def status_repr(self) -> str:
        count = 0
        total = 0
        for k in self.file_keys:
            for status in self.upload_status[k]:
                total += 1
                if status:
                    count += 1
        return f"{count} of {total} files uploaded"

    # --- State Functions ---
    def load(self):
        """Function for Loading the State Variables"""
        # Reload Parameters for Submission
        self.form_open = False
        self.submitting = False
        self.production = Production.NESPRESSO
        self.form_type = FormType.LOG
        self.production_room = Location("", "", False)
        self.start_date = self.get_default_start_date()
        self.end_date = self.get_default_end_date()
        self.message = ""

        # Reload File Variables
        self.current_key = ""
        self.file_keys = []
        self.key_titles = {}
        self.file_indices = {}
        self.file_names = {}
        self.file_raw = {}
        self.upload_status = {}

        # Reload Page Variables
        self.current_step = 0

    def set_variables(self):
        """Function for Setting the Upload File Variables based on the State"""
        num_days = self.get_num_days()
        # Manage Variables for Machine Log Uploads
        if self.is_logs:
            # Handle Nespresso HMPS Upload Variables
            if "Nespresso" in self.production_room.name:
                self.production = Production.NESPRESSO
                self.current_key = "spreafico"
                self.file_keys = ["spreafico", "hmps"]
                self.key_titles = {"spreafico": f"Upload Spreafico OEE files between {self.start_date.strftime("%d/%m/%y")} and {self.end_date.strftime("%d/%m/%y")}", "hmps": "Upload HMPS Faults, Runtime & Settings Files"}
                self.file_indices = {"spreafico": [x for x in range(num_days)], "hmps": [x for x in range(3)]}
                self.file_names = {"spreafico": self.get_name_fillers("spreafico"), "hmps": self.get_name_fillers("hmps")}
                self.file_raw = {"spreafico": [b"" for x in range(num_days)], "hmps": [b"" for x in range(3)]}
                self.upload_status = {"spreafico": [False for x in range(num_days)], "hmps": [False for x in range(3)]}
            # TODO: handle more machine logs
        
        # Manage Variables for Production Schedule Uploads
        elif self.is_schedule:
            # TODO: handle scheduling
            pass
        
        # Manage Variables for Output Summary Uploads
        elif self.is_summary:
            # TODO: handle output
            pass

    def get_default_start_date(self) -> datetime:
        """Function for Getting the Default Start Date"""
        start = datetime.today() + relativedelta(weeks=-1)
        if start.weekday() == 0:
            return start
        return start + relativedelta(days=(-1*start.weekday()))

    def get_default_end_date(self) -> datetime:
        """Function for Getting the Default End Date"""
        end = datetime.today() + relativedelta(weeks=-1)
        if end.weekday() == 4:
            return end
        return end + relativedelta(days=(4 - end.weekday()))

    def get_num_days(self) -> int:
        """Function for Getting the Number of Days between the Start and End Dates"""
        return (self.end_date - self.start_date).days + 1

    def get_name_fillers(self, key: str) -> list[str]:
        """Function for Getting the Filler Names for Files yet to be Uploaded"""
        arr = []
        # Case 1: Nespresso Logs
        if self.is_nespresso and self.is_logs:
            # Case 1.A: Spreafico Fillers
            if key == "spreafico":
                day = self.start_date
                step = timedelta(days=1)
                while day <= self.end_date:
                    arr.append(f"OEE File for date {day.strftime("%d/%m/%y")}")
                    day += step
            # Case 1.B: HMPS Fillers
            elif key == "hmps":
                arr.append("Faults File")
                arr.append("Runtime File")
                arr.append("Settings File")
            
        return arr

    def is_valid_date(self, date: str, format: str) -> bool:
        """Function for Checking if Date String is Valid by the given Format"""
        try:
            return isinstance(datetime.strptime(date, format), datetime)
        except:
            return False

    # --- Event Handlers ---
    @rx.event
    def open(self):
        """Function for Opening the Form"""
        self.form_open = True

    @rx.event
    def next(self):
        """Function for Navigating to the Next Page of the Form"""
        if self.current_step < self.total_steps - 1:
            self.current_step += 1

            # Update Current Key
            if self.current_key != "" and self.current_step < self.total_steps - 1:
                self.current_key = self.file_keys[self.current_step - 1]
            elif self.upload_complete:
                self.current_key = ""

    @rx.event
    def previous(self):
        """Function for Navigating to the Previous Page of the Form"""
        if self.current_step > 0:
            self.current_step -= 1

            # Update Current Key
            if self.current_key != "" and self.current_step > 0:
                self.current_key = self.file_keys[self.current_step - 1]
            elif self.current_step == 0:
                self.current_key = ""

    @rx.event
    def update_form_type(self, form_type: str):
        """Function for Setting the Form Type"""
        if form_type == "log":
            self.form_type = FormType.LOG
        elif form_type == "schedule":
            self.form_type = FormType.SCHEDULE
        elif form_type == "summary":
            self.form_type = FormType.SUMMARY

    @rx.event
    def update_production_room(self, room: str):
        """Function for Updating the Production Room"""
        self.production_room = [area for area in db.locations if area.name == room][0]
        self.set_variables()

    @rx.event
    def update_start_date(self, date: str):
        """Function for Updating the Start Date"""
        if self.is_valid_date(date, "%Y-%m-%d"):
            self.start_date = datetime.strptime(date, "%Y-%m-%d")

    @rx.event
    def update_end_date(self, date: str):
        """Function for Updating the End Date"""
        if self.is_valid_date(date, "%Y-%m-%d"):
            self.end_date = datetime.strptime(date, "%Y-%m-%d")

    @rx.event
    async def update_file(self, files: list[rx.UploadFile]):
        """Function for Uploading a CSV File"""
        # Case 1: File Uploads for Nespresso Logs
        if self.is_nespresso and self.is_logs:
            # Case 1.A: File Uploads for the Spreafico
            if self.current_key == "spreafico":
                date_reprs = []
                step = timedelta(days=1)
                day = self.start_date
                while day < self.end_date:
                    date_reprs.append(day.strftime("%d.%m.%Y"))
                    day += step
                for file in files:
                    for repr in date_reprs:
                        if repr in file.name:
                            idx = date_reprs.index(repr)
                            self.file_names[self.current_key][idx] = file.name
                            self.file_raw[self.current_key][idx] = await file.read()
                            self.upload_status[self.current_key][idx] = True
            # Case 1.B: File Uploads for the HMPS
            elif self.current_key == "hmps":
                reprs = ["faults", "runtime", "settings"]
                for file in files:
                    for repr in reprs:
                        if repr in file.name:
                            idx = reprs.index(repr)
                            self.file_names[self.current_key][idx] = file.name
                            self.file_raw[self.current_key][idx] = await file.read()
                            self.upload_status[self.current_key][idx] = True

    @rx.event
    def delete_file(self, key: str, idx: int):
        """Fuction for Deleting the File"""
        fillers = self.get_name_fillers(key)
        self.file_names[key][idx] = fillers[idx]
        self.file_raw[key][idx] = b""
        self.upload_status[key][idx] = False

    @rx.event
    def cancel(self):
        """Function for Cancelling the Form"""
        self.load()

    @rx.event
    def submit(self):
        """Function for Submitting the Form"""
        self.submitting = True
        yield

        # Initialise Data for Upload
        parameter_size = oee_summariser.initialise_data(
            production_id=self.production_room.id,
            data=self.file_raw,
            logs=self.is_logs,
            schedule=self.is_schedule,
            summary=self.is_summary
        )

        # Update Message
        self.message = f"Number of Parameters to Upload to DB: {parameter_size}"
        yield

        # Upload Data
        if parameter_size > 0:
            while not oee_summariser.insert_complete:
                uploaded_parameters = oee_summariser.upload_data()
                self.message = f"Upload Progress: {float(uploaded_parameters * 100 / parameter_size):.1f}%"
                yield

        self.load()
