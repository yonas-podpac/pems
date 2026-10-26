import calendar
from datetime import datetime
import reflex as rx
import numpy as np
import os
from pems.helpers.maintenance_handler import maintenance_handler
from pems.states.user_state import UserState

class PreventativeState(UserState):
    # New Procedure Form Variables
    submitting: bool = False
    maintenance_id: str = ""
    new_procedure_form_open: bool = False
    title: str = ""
    location: str = ""
    estimated_duration: int = 0
    frequency: str = ""
    weekly: bool = False
    ordinal: str = "1st"
    ordinal_selected: bool = False
    weekday_selected: bool = False
    weekday: str = "Monday"
    month_selected: bool = False
    month_updated: bool = False
    selected_month: str = datetime.today().strftime("%B")
    asset_fields: list[str] = ["asset_0"]
    selected_assets: dict[int, str] = {}
    station_available: dict[str, bool] = {"asset_0": False}
    station_fields: dict[str, list[str]] = {"asset_0": []}
    selected_stations: dict[int, dict[int, str]] = {}
    selected_tasks: dict[int, dict[int, str]] = {}

    # Work Order Form Variables
    work_order_form_open: bool = False
    maintenance_complete: bool = False
    print_preview: bool = False
    editable: bool = False
    work_order_id: str = ""
    preventative_id: str = ""
    procedure_id: str = ""
    name: str = ""
    date: datetime = datetime.today()
    wo_assets: list[str] = []
    tasks: dict[str, list[dict[str, str]]] = {}
    task_completed: dict[str, bool] = {}
    task_notes: dict[str, str] = {}
    additional_notes: str = ""
    
    # --- New Procedure Form Reflex Variables ---
    @rx.var
    def form_complete(self) -> bool:
        return (
            self.title_selected and
            self.location_selected and 
            self.estimated_duration_selected and
            self.frequency_selected and
            self.ordinal_selected and
            self.weekday_selected and
            self.month_selected and
            self.asset_selected and
            self.station_selected and
            self.task_selected
        )

    @rx.var
    def title_selected(self) -> bool:
        return self.title != ""

    @rx.var
    def location_selected(self) -> bool:
        return self.location != ""

    @rx.var
    def estimated_duration_selected(self) -> bool:
        return self.estimated_duration > 0

    @rx.var
    def frequency_selected(self) -> bool:
        return self.frequency != ""

    @rx.var
    def asset_selected(self) -> bool:
        return len(self.selected_assets) > 0

    @rx.var
    def station_selected(self) -> bool:
        check = True
        for field in self.station_available.keys():
            a_idx = int(field.split("_")[1])
            if self.station_available[field]:
                check = len(self.selected_stations[a_idx]) > 0
            if not check:
                break
        return check

    @rx.var
    def task_selected(self) -> bool:
        check = True
        for idx in self.selected_tasks.keys():
            check = len(self.selected_tasks[idx]) > 0
            if not check:
                break
        return check

    @rx.var
    def locations(self) -> list[str]:
        return maintenance_handler.production_rooms

    @rx.var
    def frequencies(self) -> list[str]:
        return maintenance_handler.frequencies

    @rx.var
    def weekdays(self) -> list[str]:
        return ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

    @rx.var
    def ordinals(self) -> list[str]:
        curr_year = datetime.today().year
        selected_month_dt = datetime.strptime("{}-{}".format(curr_year, self.selected_month), "%Y-%B")
        selected_month_repr = selected_month_dt.strftime("%Y-%m")
        next_month = selected_month_dt.month % 12 + 1
        next_month_repr = datetime.strptime("{}-{}".format(curr_year, next_month), "%Y-%m").strftime("%Y-%m")
        weekday_counts = {}
        for day in self.weekdays:
            weekday_counts[day] = np.busday_count(selected_month_repr, next_month_repr, weekmask=day[:3])

        ordinals = ["1st", "2nd", "3rd", "4th"]
        if self.weekday_selected:
            if weekday_counts[self.weekday] == 5:
                ordinals.append("5th")
        else:
            if max(weekday_counts.values()) == 5:
                ordinals.append("5th")

        return ordinals

    @rx.var
    def day_of_month(self) -> str:
        idx = int(self.ordinal[0]) - 1
        if self.weekday == "Monday":
            cal_weekday = calendar.MONDAY
        elif self.weekday == "Tuesday":
            cal_weekday = calendar.TUESDAY
        elif self.weekday == "Wednesday":
            cal_weekday = calendar.WEDNESDAY
        elif self.weekday == "Thursday":
            cal_weekday = calendar.THURSDAY
        elif self.weekday == "Friday":
            cal_weekday = calendar.FRIDAY
        year = datetime.today().year
        month = datetime.strptime(self.selected_month, "%B").month
        monthcal = calendar.Calendar(firstweekday=calendar.MONDAY).monthdatescalendar(year, month)

        try:
            return str([day for week in monthcal for day in week if day.weekday() == cal_weekday and day.month == month][idx].day)
        except IndexError:
            print("[ERROR] Ordinal needs to be reselected")
            self.ordinal_selected = False
            return str([day for week in monthcal for day in week if day.weekday() == cal_weekday and day.month == month][idx - 1].day)

    @rx.var
    def months(self) -> list[str]:
        return ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    @rx.var
    def year(self) -> str:
        return str(datetime.today().year)

    @rx.var
    def assets(self) -> list[str]:
        if self.location_selected:
            return maintenance_handler.get_assets_by_area(self.location)
        return []

    @rx.var
    def stations(self) -> dict[str, list[str]]:
        asset_stations = {}
        for a_field in self.asset_fields:
            a_idx = int(a_field.split("_")[1])
            if self.selected_assets.__contains__(a_idx):
                asset = self.selected_assets[a_idx]
                asset_stations[a_field] = maintenance_handler.get_stations_by_area_and_asset(self.location, asset)
                self.station_available[a_field] = len(asset_stations[a_field]) > 0
        return asset_stations

    # --- Work Order Reflex Variables ---
    @rx.var
    def work_order_complete(self) -> bool:
        return (
            self.name_selected and
            self.all_task_complete
        )

    @rx.var
    def name_selected(self) -> bool:
        return self.name != ""

    @rx.var
    def all_task_complete(self) -> bool:
        complete = True
        for t_key in self.task_completed:
            if not self.task_completed[t_key]:
                complete = False
                break
        return complete

    @rx.var
    def date_repr(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    # --- State Functions ---
    def load(self):
        self.submitting = False
        self.new_procedure_form_open = False
        self.title = ""
        self.location = ""
        self.estimated_duration = 0
        self.frequency = ""
        self.weekly = False
        self.ordinal = "1st"
        self.ordinal_selected = False
        self.weekday = "Monday"
        self.weekday_selected = False
        self.selected_month = datetime.today().strftime("%B")
        self.month_selected = False
        self.month_updated = False
        self.asset_fields = ["asset_0"]
        self.selected_assets = {}
        self.station_available = {"asset_0": False}
        self.station_fields = {"asset_0": []}
        self.selected_stations = {}
        self.selected_tasks = {}
        self.work_order_form_open = False
        self.maintenance_complete = False
        self.editable = False
        self.work_order_id = ""
        self.preventative_id = ""
        self.procedure_id = ""
        self.name = ""
        self.date = datetime.today()
        self.wo_assets = []
        self.tasks = {}
        self.task_completed = {}
        self.task_notes = {}
        self.additional_notes = ""

    # --- New Procedure Form Functions ---
    @rx.event
    def new_procedure(self):
        """Function for Opening the New Procedure Form"""
        self.new_procedure_form_open = True
        maintenance_handler.build_work_order_id(procedure=True)
        self.maintenance_id = maintenance_handler.maintenance_id

    @rx.event
    def update_title(self, title: str):
        """Function for Updating the Procedure Title"""
        self.title = title

    @rx.event
    def update_location(self, area: str):
        """Function for Updating the Production Room"""
        self.location = area

    @rx.event
    def update_estimated_duration(self, duration: str):
        """Function for Updating the Estimated Duration for the Maintenance"""
        try:
            self.estimated_duration = int(duration)
        except:
            self.estimated_duration = 0

    @rx.event
    def update_frequency(self, freq: str):
        """Function for Updating the Frequency for Preventative Maintenance""" 
        self.frequency = freq
        self.weekly = freq == "Weekly"
        self.ordinal_selected = self.weekly

    @rx.event
    def update_ordinal(self, ordinal: str):
        """Function for Updating the Ordinal"""
        self.ordinal = ordinal
        self.ordinal_selected = True

    @rx.event
    def update_month(self, month: str):
        """Function for Updating the Selected Month"""
        self.selected_month = month
        self.month_selected = True
        self.month_updated = True

    @rx.event
    def update_weekday(self, weekday: str):
        """Function for Updating the Weekday for Maintenance"""
        self.weekday = weekday
        self.weekday_selected = True

    @rx.event
    def add_asset_field(self):
        """Function that Adds a New Asset Field"""
        next_idx = len(self.asset_fields)
        self.asset_fields.append("asset_{}".format(next_idx))
        self.station_fields["asset_{}".format(next_idx)] = []

    @rx.event
    def delete_asset_field(self, field: str):
        """Function that Removes an Asset"""
        field_idx = int(field.split("_")[1])

        # Check if Field has been Selected
        if self.selected_assets.keys().__contains__(field_idx):
            self.selected_assets.pop(field_idx)

        # Check if Previous Field Indices Need to be Updated
        asset_keys_to_update = []
        for idx in self.selected_assets.keys():
            if idx > field_idx:
                asset_keys_to_update.append(idx)
        for idx in asset_keys_to_update:
            asset = self.selected_assets.pop(idx)
            self.selected_assets[idx - 1] = asset

        # Remove Last Field
        self.asset_fields.pop()

        # Update Stations where required
        station_availablity_check = False
        selected_station_check = False
        selected_task_check = False
        if self.station_fields.keys().__contains__(field):
            self.station_fields.pop(field)
        if self.station_available.keys().__contains__(field):
            station_availablity_check = True
            self.station_available.pop(field)
        if self.selected_stations.keys().__contains__(field_idx):
            selected_station_check = True
            self.selected_stations.pop(field_idx)
        if self.selected_tasks.keys().__contains__(field_idx):
            selected_task_check = True
            self.selected_tasks.pop(field_idx)

        station_keys_to_update = []
        for k in self.station_fields.keys():
            k_idx = int(k.split("_")[1])
            if k_idx > field_idx:
                station_keys_to_update.append(k_idx)
        for idx in station_keys_to_update:
            stat_field = self.station_fields.pop("asset_{}".format(idx))
            self.station_fields["asset_{}".format(idx - 1)] = stat_field
            if station_availablity_check:
                stat_avail = self.station_available.pop("asset_{}".format(idx))                
                self.station_available["asset_{}".format(idx - 1)] = stat_avail
            if selected_station_check:
                selected_station = self.selected_stations.pop(idx)
                self.selected_stations[idx - 1] = selected_station
            if selected_task_check:
                selected_task  = self.selected_tasks.pop(idx)
                self.selected_tasks[idx - 1] = selected_task

    @rx.event
    def update_asset(self, field: str, asset: str):
        """Function for Selecting the Asset for Maintenance"""
        field_idx = int(field.split("_")[1])
        self.selected_assets[field_idx] = asset

        # Update Stations
        self.station_available[field] = False
        self.station_fields[field] = []
        self.selected_stations[field_idx] = {}
        self.selected_tasks[field_idx] = {}

    @rx.event
    def add_station_field(self, asset_field: str):
        """Function that Adds a New Station Field"""
        next_idx = len(self.station_fields[asset_field])
        self.station_fields[asset_field].append("station_{}".format(next_idx))

    @rx.event
    def delete_station_field(self, asset_field: str, station_field: str):
        """Function that Deletes a Station Field"""
        a_field_idx = int(asset_field.split("_")[1])
        s_field_idx = int(station_field.split("_")[1])

        # Check if Field has been Selected
        if self.selected_stations[a_field_idx].keys().__contains__(s_field_idx):
            self.selected_stations[a_field_idx].pop(s_field_idx)
            self.selected_tasks[a_field_idx].pop(s_field_idx)

        # Check if Previous Field Indices Need to be Updated
        keys_to_update = []
        for idx in self.selected_stations[a_field_idx].keys():
            if idx > s_field_idx:
                keys_to_update.append(idx)
        for idx in keys_to_update:
            station = self.selected_stations[a_field_idx].pop(idx)
            task = self.selected_tasks[a_field_idx].pop(idx)
            self.selected_stations[a_field_idx][idx - 1] = station
            self.selected_tasks[a_field_idx][idx - 1] = task

        # Remove Last Field
        self.station_fields[asset_field].pop()
    
    @rx.event
    def update_station(self, a_field: str, s_field: str, station: str):
        """Function for Selecting the Station for Maintenance"""
        a_field_idx = int(a_field.split("_")[1])
        s_field_idx = int(s_field.split("_")[1])
        self.selected_stations[a_field_idx][s_field_idx] = station
        self.selected_tasks[a_field_idx][s_field_idx] = ""

    @rx.event
    def update_task(self, a_field: str, s_field: str, task: str):
        """Function for Assiging a Task for a given station"""
        a_field_idx = int(a_field.split("_")[1])
        s_field_idx = int(s_field.split("_")[1])
        self.selected_tasks[a_field_idx][s_field_idx] = task

    @rx.event
    def toggle(self):
        """Function for Toggling the New Procedure Form"""
        self.new_procedure_form_open = not self.new_procedure_form_open

    @rx.event
    def submit(self, form_data: dict):
        """Function for Submitting a New Procedure"""
        self.submitting = True
        yield
        # Build Maintenance Procedure Entry
        procedure = maintenance_handler.build_maintenance_procedure(
            procedure_id=self.maintenance_id,
            title=self.title,
            frequency=self.frequency,
            repeats_weekday=self.weekday.lower(),
            repeats_ordinal=self.ordinal,
            estimated_duration=self.estimated_duration
        )

        # Build Maintenance Task Entries
        for asset_field in self.asset_fields:
            a_field_idx = int(asset_field.split("_")[1])
            for station_field in self.station_fields[asset_field]:
                s_field_idx = int(station_field.split("_")[1])
                task_id = maintenance_handler.get_next_task_id(self.location, self.frequency)
                print(f"New Task ID: {task_id}")
                if self.station_available[asset_field]:
                    print(f"Asset: {self.selected_assets[a_field_idx]}; Station: {self.selected_stations[a_field_idx][s_field_idx]}")
                    maintenance_handler.build_maintenance_task(
                        procedure_id=procedure.id,
                        task_id=task_id,
                        location=self.location,
                        asset=self.selected_assets[a_field_idx].split(":")[1].lstrip(),
                        job=self.selected_tasks[a_field_idx][s_field_idx],
                        station_available=True,
                        station=self.selected_stations[a_field_idx][s_field_idx]
                    )
                else:
                    print(f"Asset: {self.selected_assets[a_field_idx]}; Station: None")
                    maintenance_handler.build_maintenance_task(
                        procedure_id=procedure.id,
                        task_id=task_id,
                        location=self.location,
                        asset=self.selected_assets[a_field_idx].split(":")[1].lstrip(),
                        job=self.selected_tasks[a_field_idx][s_field_idx],
                        station_available=False
                    )

        # Close Form
        self.new_procedure_form_open = False
        self.load()

    # --- Work Order Form Functions ---
    def open_work_order_form(self, id: str, complete: bool):
        """Function for Opening a Preventative Maintenance Work Order"""
        self.load()
        self.work_order_form_open = True
        print(f"Opening Preventative Work Order Form with ID: {id}")

        # Generate Completed Preventative Maintenance Work Order
        if complete:
            self.maintenance_complete = True
            # TODO: implement
            pass
        
        # Generate New Preventative Maintenance Work Order
        else:
            # Generate Relevant IDs
            maintenance_handler.build_work_order_id(preventative=True)
            self.work_order_id = maintenance_handler.work_order_id
            self.preventative_id = maintenance_handler.maintenance_id
            self.procedure_id = id

            # Get Procedure Data
            maintenance_procedure = maintenance_handler.get_procedure(id)
            self.title = maintenance_procedure.title
            self.estimated_duration = maintenance_procedure.estimated_duration_mins

            # Get Task Data
            maintenance_tasks = maintenance_handler.get_tasks(id)
            sorted_tasks = sorted(maintenance_tasks, key=lambda d: d["task_id"])
            self.location = maintenance_handler.get_location_by_id(sorted_tasks[0].location_id)
            asset_ids = list(dict.fromkeys([task.asset_id for task in sorted_tasks]))
            self.wo_assets = [maintenance_handler.get_asset_by_id(a_id) for a_id in asset_ids]

            # Build Task-related Dictionaries
            for task in sorted_tasks:
                a_idx = asset_ids.index(task.asset_id)
                asset = self.wo_assets[a_idx]
                if self.tasks.keys().__contains__(asset):
                    self.tasks[asset].append({"asset_id": task.asset_id, "id": task.task_id, "job": task.job})
                else:
                    self.tasks[asset] = [{"asset_id": task.asset_id, "id": task.task_id, "job": task.job}]
                self.task_completed[task.task_id] = False
                self.task_notes[task.task_id] = ""

            # Set Editable
            self.editable = True

    @rx.event
    def update_name(self, employee: str):
        """Function for Updating the Employee Creating the Work Order"""
        self.name = employee

    @rx.event
    def update_date(self, date: str):
        """Function for Updating the Creation Date for the Work Order"""
        if maintenance_handler.is_valid_date(date, "%Y-%m-%d"):
            self.date = datetime.strptime(date, "%Y-%m-%d")

    @rx.event
    def update_task_complete(self, task_id: str, complete: bool):
        """Function for Updating Completion of a Task"""
        self.task_completed[task_id] = not self.task_completed[task_id]

    @rx.event
    def update_task_notes(self, task_id: str, note: str):
        """Function for Updating Task Notes"""
        self.task_notes[task_id] = note

    @rx.event
    def update_additional_notes(self, note: str):
        """Function for Updating Additional Notes for Work Order"""
        self.additional_notes = note

    @rx.event
    def edit(self):
        """Function for Editting the Work Order"""
        self.editable = True

    @rx.event
    def work_order_submit(self):
        """Function for Submitting the Work Order"""
        self.submitting = True
        yield

        # Build list of Asset IDs
        asset_ids = []
        task_status = {}
        # print(self.tasks)
        for asset_name in self.tasks.keys():
            for task in self.tasks[asset_name]:
                if not asset_ids.__contains__(task["asset_id"]):
                    asset_ids.append(task["asset_id"])
                task_status[task["id"]] = {
                    "complete": "yes" if self.task_completed[task["id"]] else "no",
                    "notes": self.task_notes[task["id"]]
                }
        # for key, task in self.tasks.items():
        #     asset_ids.append(task["asset_id"])
        #     task_status[task["id"]] = {
        #         "complete": "yes" if self.task_completed[task["id"]] else "no",
        #         "notes": self.task_notes[task["id"]]
        #     }

        # Build Closed Work Order Entry
        work_order = maintenance_handler.build_closed_work_order(
            work_order_id=self.work_order_id,
            asset_ids={"ids": asset_ids},
            status="complete",
            reported_by=self.name,
            assigned_to=self.name,
            created_at=self.date,
            completed_at=self.date,
            cost=0,
            preventative=True
        )

        # Build Preventative Maintenance Entry
        maintenance_handler.build_preventative_maintenance(
            preventative_id=self.preventative_id,
            work_order_id=work_order.id,
            procedure=self.procedure_id,
            task_status=task_status,
            notes=self.additional_notes
        )
        
        # Close Window
        self.work_order_form_open = False
        self.editable = False

    @rx.event
    def print_work_order(self):
        """Function for Redirecting to a Print Page"""
        self.print_preview = True
        return rx.redirect("/preview")

    @rx.event
    def cancel(self):
        """Function for Cancelling the Work Order"""
        self.work_order_form_open = False
        self.editable = False
        self.work_order_id = ""
        self.preventative_id = ""
        self.procedure_id = ""
        self.name = ""
        self.date = datetime.today()
        self.wo_assets = []
        self.tasks = {}
        self.task_completed = {}
        self.task_notes = {}
        self.additional_notes = ""
