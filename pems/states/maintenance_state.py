import calendar as pycal
from datetime import datetime
import reflex as rx
from pems.helpers.database import db
from pems.helpers.maintenance_handler import maintenance_handler
from pems.states.user_state import UserState
from pems.components.objects import WorkOrder, UnplannedMaintenance, MaintenanceProcedure, MaintenanceTask

class MaintenanceState(UserState):
    # Calendar States
    current_date: datetime = datetime.today()
    month_shift: int = 0
    day_jobs_title: str = ""
    selected_day: int = 0
    selected_date: str = ""
    selected_day_jobs: list[dict[str, str]] = []
    day_jobs: dict[int, dict[int, list[dict[str, str]]]] = {}
    is_day_jobs_open: bool = False

    # Work Order Form States
    work_order_id: str = "WO-000"
    maintenance_id: str = ""
    current_work_orders: list[WorkOrder] = []
    selected_work_order: WorkOrder = None
    selected_work_order_id: str = ""
    preventative: bool = True
    associated_procedure: MaintenanceProcedure = None
    selected_title: str = ""
    work_area: str = ""
    assets: list[str] = []
    statuses = []
    job_statuses = []
    asset_jobs: dict[str, list[dict[str, str]]] = {}
    associated_tasks: list[MaintenanceTask] = []
    tech_notes: str = ""
    is_work_order_form_open: bool = False

    # Admin Form States
    is_new_entry_form_open: bool = False

    # --- State Functions ---
    def load(self):
        self.current_date = datetime.today()
        self.is_day_jobs_open = False
        self.is_new_entry_form_open = False
        self.statuses = [] # TODO: create DB function to get possible statuses for work order
        self.job_statuses = []
        for status in self.statuses:
            if status != "sign off required":
                self.job_statuses.append(status)
        self.month_shift = 0
        self.day_jobs = maintenance_handler.get_monthly_tasks(self.month_days)

    # --- Calendar Functions ---
    @rx.var
    def month(self) -> str:
        return self.current_date.strftime("%B %Y")
    
    @rx.var
    def current_month(self) -> bool:
        return self.month_shift == 0

    @rx.var
    def month_days(self) -> list[dict[str, int]]:
        """Variable for the Grid Layout array"""
        return maintenance_handler.get_month_days(self.current_date)

    @rx.event
    def change_month(self, shift: int):
        """Function for Shifting the Month Forwards / Backwards"""
        month = 0
        year = 0
        # Handle Forward Shift
        if shift == 1:
            # Check if Year needs to be Updated
            self.month_shift += 1
            if self.current_date.month == 12 or self.current_date.month + self.month_shift == 12:
                month = 1
                year = self.current_date.year + 1
            else:
                month = self.current_date.month + 1
                year = self.current_date.year

        # Handle Backward Shift
        elif shift == -1:
            # Check if Year Needs to be Updated
            self.month_shift -= 1
            if self.current_date.month == 1 or self.current_date.month - self.month_shift == 1:
                month = 12
                year = self.current_date.year - 1
            else:
                month = self.current_date.month - 1
                year = self.current_date.year
        
        # Update Date
        try:
            self.current_date = self.current_date.replace(year=year, month=month)
        except ValueError:
            # Edge Case: end of month
            import calendar
            _, last_day = calendar.monthrange(year, month)
            self.current_date = self.current_date.replace(year=year, month=month, day=last_day)

        # Update Monthly Tasks
        self.day_jobs = maintenance_handler.get_monthly_tasks(self.current_date)

        return

    @rx.event
    def open_day_details(self, day_num: int):
        self.selected_day = day_num
        self.selected_date = "{}-{}-{}".format(self.current_date.year, self.current_date.month, day_num)
        reformatted_date = datetime.strftime(datetime.strptime(self.selected_date, "%Y-%m-%d"), "%Y-%b-%d")
        self.day_jobs_title = "Job List for " + reformatted_date
        self.selected_day_jobs = self.day_jobs[day_num]
        self.is_day_jobs_open = True

    @rx.event
    def close_day_details(self):
        self.is_day_jobs_open = False

    # --- Form Functions ---
    @rx.event
    def open_work_order_form(self, day: int, job: str):
        self.is_day_jobs_open = False
        self.is_work_order_form_open = True
        self.selected_day = day
        print(job)

    @rx.event
    def toggle_work_order_form(self, work_order: WorkOrder):
        self.selected_work_order = work_order
        self.selected_work_order_id = work_order.work_order_id
        self.associated_procedure = MaintenanceProcedure # TODO: create DB function for getting associated procedure
        self.selected_title = self.associated_procedure.title
        # TODO: create DB function for getting associated tasks
        for task in self.associated_tasks:
            # Get Work Area
            if self.work_area == "":
                self.work_area = "" # TODO: create DB function for getting location by ID

            # Get Asset
            asset = "" # TODO: create DB function for getting asset by ID
            if not asset in self.assets:
                self.assets.append(asset)

            # Get Job
            if not asset in self.asset_jobs.keys():
                self.asset_jobs[asset] = [{
                    "task_id": task.task_id,
                    "asset": asset,
                    "station": "", # TODO: create DB function for getting station by ID
                    "job": task.job,
                    "status": "in progress"
                }]
            else:
                self.asset_jobs[asset].append({
                    "task_id": task.task_id,
                    "asset": asset,
                    "station": "", # TODO: create DB function for getting station by ID
                    "job": task.job,
                    "status": "In Progress"
                })
        self.tech_notes = work_order.notes
        self.is_work_order_form_open = True

    @ rx.event
    def handle_submit(self, form_data: dict):
        # 1. Update Work Orders
        # TODO: Create DB Update function
        
        # 2. Refresh the Calendar Data
        # TODO: Create refreseh function

        # 3. Close Form
        self.is_work_order_form_open = False

    # --- Admin Form Functions ---
    def toggle_new_entry_form(self):
        """Function for Opening or Closing the New Entry Form"""
        self.is_new_entry_form_open = not self.is_new_entry_form_open

    def handle_add_click(self):
        """Function to Open a New Entry Form"""
        self.is_new_entry_form_open = True
