import calendar as pycal
from datetime import datetime
import pandas as pd
from pandas.core.frame import DataFrame
from pems.helpers.database import db
from pems.components.objects import *
import time

class MaintenanceHandler:
    def __init__(self):
        # Retrieve Lists from DB
        self.__asset_registrar = db.asset_registrar
        self.__asset_statuses = db.asset_statuses
        self.__components = db.components
        self.__failure_types = db.failure_types
        self.__locations = db.locations
        self.__maintenance_frequencies = db.maintenance_frequencies
        self.__maintenance_procedures = db.maintenance_procedures
        self.__maintenance_tasks = db.maintenance_tasks
        self.__maintenance_types = db.maintenance_types
        self.__preventative_maintenance = db.preventative_maintenance
        self.__root_causes = db.root_causes
        self.__service_maintenance = db.service_maintenance
        self.__service_provider_types = db.service_provider_types
        self.__severities = db.severities
        self.__spare_parts = db.spare_parts
        self.__stations = db.stations
        self.__unplanned_events = db.unplanned_events
        self.__unplanned_maintenance = db.unplanned_maintenance
        self.__work_order_statuses = db.work_order_statuses
        self.__work_orders = db.work_orders

        # Instantiate IDs
        self.__work_order_id = "WO-"
        self.__maintenance_id = ""

    @property
    def failure_types(self) -> list[str]:
        return [fail.failure.title() for fail in self.__failure_types]

    @property
    def locations(self) -> list[str]:
        return [area.name for area in self.__locations]

    @property
    def production_rooms(self) -> list[str]:
        return [area.name for area in self.__locations if area.is_production]

    @property
    def frequencies(self) -> list[str]:
        return [freq.frequency.title() for freq in self.__maintenance_frequencies]
    
    @property
    def root_causes(self) -> list[str]:
        return [rc.cause.title() for rc in self.__root_causes]
    
    @property
    def service_provider_types(self) -> list[str]:
        return [sp_type.type.title() for sp_type in self.__service_provider_types]
    
    @property
    def severities(self) -> list[str]:
        return [s.severity.title() for s in self.__severities]
    
    @property
    def spare_parts(self) -> list[str]:
        return [part.name for part in self.__spare_parts]

    @property
    def work_order_id(self) -> str:
        return self.__work_order_id

    @property
    def maintenance_id(self) -> str:
        return self.__maintenance_id

    def get_location_by_id(self, id: str) -> str:
        """Function that Gets a Production Room Name by ID"""
        return self.__get_referenced_value(id, "locations", "id", "name")

    def get_location_id_by_name(self, name: str) -> str:
        """Function that Gets a Production Room ID by Name"""
        return self.__get_referenced_value(name, "locations", "name", "id")

    def get_asset_by_id(self, id: str) -> str:
        """Fucntion that Gets the Asset Manufacturer & Name by ID"""
        return [asset.manufacturer + ": " + asset.name for asset in self.__asset_registrar if asset.id == id][0]

    def get_station_by_id(self, id: str) -> str:
        """Function that Gets the Station by ID"""
        try:
            return [station.name for station in self.__stations if station.id == id][0]
        except:
            return ""
    
    def get_assets_by_area(self, area: str) -> list[str]:
        """Function for Getting the Assets in a Production Area"""
        location_id = self.__get_referenced_value(area, "locations", "name", "id")
        return [asset.manufacturer + ": " + asset.name for asset in self.__asset_registrar if asset.location_id == location_id and asset.operational]
    
    def get_asset_id_by_area_and_name(self, area: str, name: str) -> str:
        """Function for Getting the Asset ID for a Given Name and Area"""
        location_id = self.__get_referenced_value(area, "locations", "name", "id")
        return [asset.id for asset in self.__asset_registrar if asset.location_id == location_id and asset.name == name][0]
    
    def get_station_id_by_area_and_asset_and_name(self, area: str, asset: str, name: str) -> str:
        try:
            location_id = self.__get_referenced_value(area, "locations", "name", "id")
            asset_id = self.get_asset_id_by_area_and_name(area, asset)
            return [station.id for station in self.__stations if station.location_id == location_id and station.asset_id == asset_id and station.name == name][0]
        except:
            return ""
        
    def get_past_unplanned_maintenances(self, area: str, asset: str, station: str) -> list[str]:
        """Function for Getting a Filtered List of Past Unplanned Maintenances"""
        arr = []
        for um in self.__unplanned_maintenance:
            entry = um.unplanned_id + ": " + um.title
            if area != "":
                if um.location_id != self.__get_referenced_value(area, "locations", "name", "id"):
                    continue
            if asset != "":
                if um.asset_id != self.get_asset_id_by_area_and_name(area, asset):
                    continue
            if station != "":
                if um.station_id != self.get_station_id_by_area_and_asset_and_name(area, asset, station):
                    continue
            arr.append(entry)
        return arr

    def get_um_by_id(self, um_id: str) -> UnplannedMaintenance:
        """Function that Gets the Unplanned Maintenance Object referenced by ID"""
        return [um for um in self.__unplanned_maintenance if um.unplanned_id == um_id][0]

    def get_wo_by_id(self, wo_id: str) -> WorkOrder:
        """Function that Gets the Work Order Object referenced by ID"""
        return [wo for wo in self.__work_orders if wo.id == wo_id][0]

    def get_failure_by_id(self, id: str) -> str:
        """Function that Gets Failure Type by ID"""
        return [fail.failure for fail in self.__failure_types if fail.id == id][0]

    def get_failure_id_by_type(self, failure: str) -> str:
        """Function that Gets Failure ID by Type"""
        return [fail.id for fail in self.__failure_types if fail.failure == failure][0]

    def get_severity_by_id(self, id: str) -> str:
        """Function that Gets Severtity by ID"""
        return [sev.severity for sev in self.__severities if sev.id == id][0]

    def get_severity_id_by_name(self, name: str) -> str:
        """Function that Gets Severity ID by Name"""
        return [sev.id for sev in self.__severities if sev.severity == name][0]

    def get_status_by_id(self, id: str) -> str:
        """Function that Gets Status by ID"""
        return [state.status for state in self.__work_order_statuses if state.id == id][0]

    def get_status_id_by_status(self, status: str) -> str:
        """Function that Gets Status ID by Status"""
        return [state.id for state in self.__work_order_statuses if state.status == status.lower()][0]

    def get_root_cause_by_id(self, id: str) -> str:
        """Function that Gets Root Cause by ID"""
        return [cause.cause for cause in self.__root_causes if cause.id == id][0]

    def get_root_cause_id_by_cause(self, cause: str) -> str:
        """Function that Gets Root Cause ID by Cause"""
        return [rc.id for rc in self.__root_causes if rc.cause == cause][0]

    def get_events_by_um_id(self, id: str) -> list[UnplannedEvent]:
        """Function that Gets UnplannedEvent Object by ID"""
        return [event for event in self.__unplanned_events if event.unplanned_id == id]

    def get_spare_part_by_id(self, id: str) -> SparePart:
        """Funcrtion that Gets Spare Part Object by ID"""
        try:
            return [part for part in self.__spare_parts if part.id == id][0]
        except:
            return SparePart("", "", "", "", 0, "", "", "", 0)

    def get_spare_part_by_name(self, name: str) -> SparePart:
        """Function that Gets Spare Part Object by Name"""
        try:
            return [part for part in self.__spare_parts if part.name == name][0]
        except:
            return SparePart("", "", "", "", 0, "", "", "", 0)
        
    def are_stations_in_asset(self, area: str, asset: str) -> bool:
        """Function that Checks if Asset has Any Stations"""
        location_id = self.__get_referenced_value(area, "locations", "name", "id")
        asset_id = [a.id for a in self.__asset_registrar if a.location_id == location_id and a.name == asset.split(":")[1].lstrip()][0]
        return len([station for station in self.__stations if station.asset_id == asset_id]) > 0
    
    def get_stations_by_area_and_asset(self, area: str, asset: str) -> list[str]:
        """Function for Getting the Stations in an Asset for a given Area"""
        location_id = self.__get_referenced_value(area, "locations", "name", "id")
        asset_id = [a.id for a in self.__asset_registrar if a.location_id == location_id and a.name == asset.split(":")[1].lstrip()][0]
        return [station.name for station in self.__stations if station.location_id == location_id and station.asset_id == asset_id]

    def get_month_days(self, curr: datetime) -> list[dict[str, int]]:
        """Function for Getting the Month Days for the Calendar View"""
        # Initialise Month Days List
        month_days = []
        # Get Buffer Days
        first_day = datetime.strptime(f"1-{curr.month}-{curr.year}", "%d-%m-%Y").weekday()
        buffer, last_day_num = pycal.monthrange(curr.year, curr.month)
        last_day = datetime.strptime(f"{last_day_num}-{curr.month}-{curr.year}", "%d-%m-%Y").weekday()

        # Retrieve Previous Month Final Days
        if first_day > 0:
            buffer, prev_last_day_num = pycal.monthrange(curr.year if curr.month >= 1 else curr.year - 1, curr.month - 1 if curr.month > 1 else 12)
            month_days = [{"day": prev_last_day_num - first_day + x + 1, "month": curr.month - 1 if curr.month > 1 else 12, "year": curr.year if curr.month > 1 else curr.year - 1, "type": 0} for x in range(first_day)]

        # Fill Month Days
        for d in pycal.Calendar(firstweekday=0).itermonthdays(curr.year, curr.month):
            if d > 0:
                month_days.append({"day": d, "month": curr.month, "year": curr.year, "type": 1})

        # Retrieve Next Month First Days
        if last_day < 6:
            for x in range(6 - last_day):
                month_days.append({"day": x + 1, "month": curr.month + 1 if curr.month < 12 else 1, "year": curr.year if curr.month < 12 else curr.year + 1, "type": 2})

        return month_days
        # return [d for d in pycal.Calendar(firstweekday=0).itermonthdays(curr.year, curr.month)]
    
    def get_monthly_tasks(self, month_days: list[dict[str, int]]) -> dict[int, dict[int, list[dict[str, str]]]]:
        """Function that Builds the Tasks for each Day in the Month"""
        # Get Tasks generated for each weekday
        weekday_tasks = [[] for x in range(5)]
        previous_obj = {}
        current_obj = {}
        next_obj = {}
        for x in month_days:
            if x["type"] == 0 and len(previous_obj) == 0:
                previous_obj = x
            elif x["type"] == 1 and len(current_obj) == 0:
                current_obj = x
            elif x["type"] == 2 and len(next_obj) == 0:
                next_obj = x

        # Add Tasks
        for procedure in self.__maintenance_procedures:
            # print(procedure)
            weekday_tasks[time.strptime(procedure.repeats_on["weekday"], "%A").tm_wday].append(procedure)
                
        # Generate Monthly Task Dictionary
        monthly_tasks = {}
        for idx, d in enumerate(month_days):
            weekday_idx = idx % 7
            if weekday_idx > 4:
                continue
            if len(weekday_tasks[weekday_idx]) > 0:
                procedure_idx_to_pop = []
                for p_idx, procedure in enumerate(weekday_tasks[weekday_idx]):
                    task_title = procedure["procedure"] + ": " + procedure["title"]
                    if d["month"] in monthly_tasks.keys():
                        if d["day"] in monthly_tasks[d["month"]].keys():
                            monthly_tasks[d["month"]][d["day"]].append({
                                "title": task_title,
                                "colour": "blue", 
                                "type": "preventative",
                                "complete": False,
                                "id": procedure.procedure
                            })
                        else:
                            monthly_tasks[d["month"]] = {d["day"]: [{
                                "title": task_title,
                                "colour": "blue",
                                "type": "preventative",
                                "complete": False,
                                "id": procedure.procedure
                            }]}
                    else:
                        monthly_tasks[d["month"]] = {d["day"]: [{
                            "title": task_title, 
                            "colour": "blue", 
                            "type": "preventative", 
                            "complete": False, 
                            "id": procedure.procedure
                        }]}
                    frequency = self.__get_referenced_value(procedure["frequency_id"], "maintenance_frequencies", "id", "frequency")

                    # Keep Weekly procedures, Pop Less Regular procedures after accounted for
                    if frequency != "weekly":
                        procedure_idx_to_pop.append(p_idx)
                for i in sorted(procedure_idx_to_pop, reverse=True):
                    weekday_tasks[weekday_idx].pop(i)

        # Check if Preventative Jobs are Complete
        for preventative in self.__preventative_maintenance:
            work_order = [wo for wo in self.__work_orders if wo.id == preventative.work_order_id][0]
            date_split = work_order.created_at.split("-")
            if current_obj["year"] == int(date_split[0]) and current_obj["month"] == int(date_split[1]):
                day = int(date_split[2])
                tasks = [t for t in monthly_tasks[day] if t["type"] == "preventative" and t["id"] == preventative.procedure_id]
                if len(tasks) > 0:
                    task = tasks[0]
                    t_idx = monthly_tasks[day].index(task)
                    task["complete"] = self.__get_referenced_value(work_order.status_id, "work_order_statuses", "id", "status") == "complete"
                    task["id"] = preventative.preventative_id
                    monthly_tasks[current_obj["month"]][day][t_idx] = task
        
        # Add Service Jobs to Monthly Tasks
        for service in self.__service_maintenance:
            work_order = [wo for wo in self.__work_orders if wo.id == service.work_order_id][0]
            date_split = work_order.created_at.split("-")
            if current_obj["year"] == int(date_split[0]) and current_obj["month"] == int(date_split[1]):
                day = int(date_split[2])
                title = service.service_id + ": " + service.title
                if current_obj["month"] in monthly_tasks.keys():
                    if day in monthly_tasks[current_obj["month"]].keys():
                        monthly_tasks[current_obj["month"]][day].append({
                            "title": title, 
                            "colour": "green", 
                            "type": "service", 
                            "complete": self.__get_referenced_value(work_order.status_id, "work_order_statuses", "id", "status") == "complete",
                            "id": service.service_id
                        }) # TODO: change if task is complete
                    else:
                        monthly_tasks[current_obj["month"]] = {day: [{
                            "title": title, 
                            "colour": "green", 
                            "type": "service", 
                            "complete": self.__get_referenced_value(work_order.status_id, "work_order_statuses", "id", "status") == "complete",
                            "id": service.service_id
                        }]}
                else:
                    monthly_tasks[current_obj["month"]] = {day: [{
                        "title": title, 
                        "colour": "green",
                        "type": "service",
                        "complete": self.__get_referenced_value(work_order.status_id, "work_order_statuses", "id", "status") == "complete",
                        "id": service.service_id
                    }]}
        
        # Add Unplanned Jobs to Monthly Tasks
        for unplanned in self.__unplanned_maintenance:
            work_order = [wo for wo in self.__work_orders if wo.id == unplanned.work_order_id][0]
            for event in self.__unplanned_events:
                date_split = event.date.split("-")
                if event.unplanned_id == unplanned.id and current_obj["year"] == int(date_split[0]) and current_obj["month"] == int(date_split[1]):
                    day = int(date_split[2])
                    title = unplanned.unplanned_id + ": " + unplanned.title
                    if current_obj["month"] in monthly_tasks.keys():
                        if day in monthly_tasks[current_obj["month"]].keys():
                            monthly_tasks[current_obj["month"]][day].append({
                                "title": title, 
                                "colour": "red",
                                "type": "unplanned",
                                "complete": self.__get_referenced_value(work_order.status_id, "work_order_statuses", "id", "status") == "complete",
                                "id": unplanned.unplanned_id
                            })
                        else:
                            monthly_tasks[current_obj["month"]] = {day: [{
                                "title": title,
                                "colour": "red",
                                "type": "unplanned",
                                "complete": self.__get_referenced_value(work_order.status_id, "work_order_statuses", "id", "status") == "complete", 
                                "id": unplanned.unplanned_id
                            }]}
                    else:
                        monthly_tasks[current_obj["month"]] = {day: [{
                            "title": title, 
                            "colour": "red",
                            "type": "unplanned",
                            "complete": self.__get_referenced_value(work_order.status_id, "work_order_statuses", "id", "status") == "complete",
                            "id": unplanned.unplanned_id
                        }]}
        
        return monthly_tasks
    
    def get_service_jobs(self) -> dict[int, list[str]]:
        """Function that Builds a List of Service Jobs"""
        jobs = {}
        for service in self.__service_maintenance:
            work_order = [wo for wo in self.__work_orders if wo.id == service.work_order_id][0]
            jobs[int(work_order.created_at.split("-")[2])] = service.service_id + ": " + service.title

        return jobs

    def get_next_task_id(self, location: str, frequency: str) -> str:
        """Function that Builds the Next Task ID"""
        prefix = location[0] + frequency[0]
        return self.__get_next_id(task=True, prefix=prefix)

    def get_next_event_id(self, umid: str) -> str:
        """Function that Builds the Next Event ID"""
        return self.__get_next_id(event=True, prefix=umid)


    def get_procedure(self, id: str) -> MaintenanceProcedure:
        """Function that Returns a MaintenanceProcedure Object with a given ID"""
        return [procedure for procedure in self.__maintenance_procedures if procedure.procedure == id][0]

    def get_tasks(self, id: str) -> list[MaintenanceTask]:
        """Function that Returns a list of MaintenanceTask Objects from a given Procedure ID"""
        procedure_id = self.__get_referenced_value(id, "maintenance_procedures", "procedure", "id")
        return [task for task in self.__maintenance_tasks if task.procedure_id == procedure_id]
    
    def build_work_order_id(self, procedure: bool = False, preventative: bool = False, service: bool = False, unplanned: bool = False):
        """Function that Builds a Work Order for the User"""
        # Build a Work Order ID and associated Maintenance ID
        self.__work_order_id = self.__get_next_id(work_order=True) 
        self.__maintenance_id = self.__get_next_id(procedure=procedure, preventative=preventative, service=service, unplanned=unplanned)

    def build_open_work_order(
            self, 
            work_order_id: str, 
            asset_ids: dict[str, list[str]], 
            status: str,
            reported_by: str, 
            assigned_to: str, 
            created_at: datetime, 
            preventative: bool = False, 
            service: bool = False, 
            unplanned: bool = False
    ) -> WorkOrder:
        """Function that Builds an Incomplete Work Order Entry"""
        work_order_entry = db.insert("work_orders", {
            "work_order_id": work_order_id,
            "asset_ids": asset_ids,
            "type_id": self.__get_maintenance_type_id(preventative=preventative, service=service, unplanned=unplanned),
            "status_id": self.__get_referenced_value(status.lower(), "work_order_statuses", "status", "id"),
            "reported_by": reported_by,
            "assigned_to": assigned_to,
            "created_at": created_at.strftime("%Y-%m-%d")
        })[0]
        db.add_local_object("work_orders", work_order_entry)
        self.__work_orders = db.work_orders
        print(self.__work_orders)
        return [work_order for work_order in self.__work_orders if work_order.id == work_order_entry["id"]][0]
    
    def build_closed_work_order(
            self,
            work_order_id: str,
            asset_ids: dict[str, list[str]],
            status: str,
            reported_by: str,
            assigned_to: str,
            created_at: datetime,
            completed_at: datetime,
            cost: float,
            preventative: bool = False,
            service: bool = False,
            unplanned: bool = False,
    ) -> WorkOrder:
        """Function that Builds a Complete Work Order Entry"""
        work_order_entry = db.insert("work_orders", {
            "work_order_id": work_order_id,
            "asset_ids": asset_ids,
            "type_id": self.__get_maintenance_type_id(preventative=preventative, service=service, unplanned=unplanned),
            "status_id": self.__get_referenced_value(status.lower(), "work_order_statuses", "status", "id"),
            "reported_by": reported_by,
            "assigned_to": assigned_to,
            "created_at": created_at.strftime("%Y-%m-%d"),
            "completed_at": completed_at.strftime("%Y-%m-%d"),
            "cost": cost
        })[0]
        db.add_local_object("work_orders", work_order_entry)
        self.__work_orders = db.work_orders
        return [work_order for work_order in self.__work_orders if work_order.id == work_order_entry["id"]][0]

    def build_maintenance_procedure(self, procedure_id: str, title: str, frequency: str, repeats_weekday: str, repeats_ordinal: str, estimated_duration: int) -> MaintenanceProcedure:
        """Function that Builds a Maintenance Procedure Entry"""
        procedure_entry = db.insert("maintenance_procedures", {
            "procedure": procedure_id,
            "title": title,
            "frequency_id": self.__get_referenced_value(frequency.lower(), "maintenance_frequencies", "frequency", "id"),
            "repeats_on": {"weekday": repeats_weekday, "ordinal": repeats_ordinal},
            "estimated_duration_mins": estimated_duration
        })[0]
        db.add_local_object("maintenance_procedures", procedure_entry)
        self.__maintenance_procedures = db.maintenance_procedures
        return [procedure for procedure in self.__maintenance_procedures if procedure.id == procedure_entry["id"]][0]

    def build_maintenance_task(self, procedure_id: str, task_id: str, location: str, asset: str, job: str, station_available: bool, station: str = ""):
        """Function that Builds a Maintenance Task Entry"""
        location_id = self.__get_referenced_value(location, "locations", "name", "id")
        asset_id = self.get_asset_id_by_area_and_name(location, asset)
        station_id = self.get_station_id_by_area_and_asset_and_name(location, asset, station) if station_available else None
        task_entry = db.insert("maintenance_tasks", {
            "procedure_id": procedure_id,
            "task_id": task_id,
            "location_id": location_id,
            "asset_id": asset_id,
            "station_id": station_id,
            "job": job
        })[0]
        db.add_local_object("maintenance_tasks", task_entry)
        self.__maintenance_tasks = db.maintenance_tasks

    def build_preventative_maintenance(self, preventative_id: str, work_order_id: str, procedure: str, task_status: dict[str, dict[str, str]], notes: str):
        """Function that Builds a Preventative Maintenance Entry"""
        preventative_maintenance_entry = db.insert("preventative_maintenance", {
            "preventative_id": preventative_id,
            "work_order_id": work_order_id,
            "procedure_id": self.__get_referenced_value(procedure, "maintenance_procedures", "procedure", "id"),
            "task_status": task_status,
            "notes": notes
        })[0]
        db.add_local_object("preventative_maintenance", preventative_maintenance_entry)
        self.__preventative_maintenance = db.preventative_maintenance

    def build_service_maintenance(self, title: str, service_id: str, work_order_id: str, service_type: str, vendor: str, notes: str):
        """Function that Builds a Service Maintenance Entry"""
        service_maintenance_entry = db.insert("service_maintenance", {
            "title": title,
            "service_id": service_id,
            "work_order_id": work_order_id,
            "service_provider_id": self.__get_referenced_value(service_type.lower(), "service_provider_types", "type", "id"),
            "vendor_company_name": vendor,
            "notes": notes
        })[0]
        db.add_local_object("service_maintenance", service_maintenance_entry)
        self.__service_maintenance = db.service_maintenance

    def build_unplanned_maintenance(self, unplanned_id: str, work_order_id: str, title: str, location: str, asset: str, station: str, failure: str, severity: str, cause: str, description: str, estimated_downtime: float, station_available: bool = True) -> UnplannedMaintenance:
        """Function that Builds an Unplanned Maintenance Entry"""
        # Get IDs for Location, Asset & Station
        location_id = self.__get_referenced_value(location, "locations", "name", "id")
        asset_id = self.get_asset_id_by_area_and_name(location, asset.split(":")[1].lstrip())

        # Submit Unplanned Maintenance with Station ID
        if station_available:
            station_id = self.get_station_id_by_area_and_asset_and_name(location, asset.split(":")[1].lstrip(), station)
            unplanned_maintenance_entry = db.insert("unplanned_maintenance", {
                "unplanned_id": unplanned_id,
                "work_order_id": work_order_id,
                "title": title,
                "location_id": location_id,
                "asset_id": asset_id,
                "station_id": station_id,
                "failure_id": self.__get_referenced_value(failure.lower(), "failure_types", "failure", "id"),
                "severity_id": self.__get_referenced_value(severity.lower(), "severities", "severity", "id"),
                "cause_id": self.__get_referenced_value(cause.lower(), "root_causes", "cause", "id"),
                "description": description,
                "estimated_downtime_mins": estimated_downtime
            })[0]

        # Submit Unplanned Maintenance Without Station ID
        else:
            unplanned_maintenance_entry = db.insert("unplanned_maintenance", {
                "unplanned_id": unplanned_id,
                "work_order_id": work_order_id,
                "title": title,
                "location_id": location_id,
                "asset_id": asset_id,
                "failure_id": self.__get_referenced_value(failure.lower(), "failure_types", "failure", "id"),
                "severity_id": self.__get_referenced_value(severity.lower(), "severities", "severity", "id"),
                "cause_id": self.__get_referenced_value(cause.lower(), "root_causes", "cause", "id"),
                "description": description,
                "estimated_downtime_mins": estimated_downtime
            })[0]
        db.add_local_object("unplanned_maintenance", unplanned_maintenance_entry)
        self.__unplanned_maintenance = db.unplanned_maintenance
        return [um for um in self.__unplanned_maintenance if um.id == unplanned_maintenance_entry["id"]][0]

    def build_unplanned_event(self, unplanned_id: str, event_id: str, date: str, time: str, duration: float, action: str, part_id: str, quantity: int):
        """Function that Builds an Unplanned Event Entry"""
        unplanned_event_entry = db.insert("unplanned_events", {
            "unplanned_id": unplanned_id,
            "event_id": event_id,
            "date": date,
            "time": time,
            "duration_mins": duration,
            "action_taken": action,
            "part_id": None if quantity == 0 else part_id,
            "quantity": quantity
        })[0]
        db.add_local_object("unplanned_events", unplanned_event_entry)
        self.__unplanned_events = db.unplanned_events
        print(self.__unplanned_events)

    def update_work_order(self, entry: dict, id: str):
        """Function for Updating the Work Order by ID"""
        work_order_entry = db.update("work_orders", entry, {"id": id})
        self.__work_orders = db.work_orders

    def update_unplanned_maintenance(self, entry: dict, id: str):
        """Function for Updating the Unplanned Maintenance by ID"""
        unplanned_maintenance_entry = db.update("unplanned_maintenance", entry, {"id": id})
        self.__unplanned_maintenance = db.unplanned_maintenance

    def update_unplanned_event(self, entry: dict, id: str):
        """Function For Updating the Unplanend Event by ID"""
        unplanned_event_entry = db.update("unplanned_events", entry, {"id": id})
        self.__unplanned_events = db.unplanned_events
    def update_spare_parts_catalogue(self, part_name: str, count: int) -> SparePart:
        """Function that Updates the Spare Parts Used"""
        part = [sp for sp in self.__spare_parts if sp.name == part_name][0]
        print(f"Part to Update: {part.name}")
        entry = db.update("spare_parts", {"on_hand": part.on_hand - count}, {"name": part_name})[0]
        db.add_local_object("spare_parts", entry)
        self.__spare_parts = db.spare_parts
        part.on_hand -= count
        return part

    def is_valid_date(self, date: str, format: str) -> bool:
        """Function for Checking if Date String is Valid by the given Format"""
        try:
            return isinstance(datetime.strptime(date, format), datetime)
        except:
            return False

    def is_valid_time(self, t: str, format: str) -> bool:
        """Function for Checking if Time String is Valid by the given Format"""
        try:
            return isinstance(time.strptime(t, format), time.struct_time)
        except:
            return False

    # --- Private Functions ---
    def __get_referenced_value(self, ref_val: str, xref_table: str, xref_column: str, desired_column: str) -> str:
        """Private Function that Retrieves Referenced Values from other Tables"""
        if xref_table == "asset_registrar":
            return [asset[desired_column] for asset in self.__asset_registrar if asset[xref_column] == ref_val][0]
        if xref_table == "failure_types":
            return [failure[desired_column] for failure in self.__failure_types if failure[xref_column] == ref_val][0]
        if xref_table == "locations":
            return [area[desired_column] for area in self.__locations if area[xref_column] == ref_val][0]
        if xref_table == "maintenance_frequencies":
            return [freq[desired_column] for freq in self.__maintenance_frequencies if freq[xref_column] == ref_val][0]
        if xref_table == "maintenance_procedures":
            return [procedure[desired_column] for procedure in self.__maintenance_procedures if procedure[xref_column] == ref_val][0]
        if xref_table == "maintenance_types":
            return [m_type[desired_column] for m_type in self.__maintenance_types if m_type[xref_column] == ref_val][0]
        if xref_table == "root_causes":
            return [cause[desired_column] for cause in self.__root_causes if cause[xref_column] == ref_val][0]
        if xref_table == "service_provider_types":
            return [sp_type[desired_column] for sp_type in self.__service_provider_types if sp_type[xref_column] == ref_val][0]
        if xref_table == "severities":
            return [sev[desired_column] for sev in self.__severities if sev[xref_column] == ref_val][0]
        if xref_table == "work_order_statuses":
            return [status[desired_column] for status in self.__work_order_statuses if status[xref_column] == ref_val][0]

    def __get_next_id(self, task: bool = False, prefix: str = "", work_order: bool = False, procedure: bool = False, preventative: bool = False, service: bool = False, unplanned: bool = False, event: bool = False) -> str:
        """Private Function that Increments the desired ID"""
        # Get Current Year
        year = str(datetime.today().year)[2:]

        # Find Next Task ID
        if task:
            max_id = self.__task_max_id(prefix)
            return self.__generic_build_id(prefix, year, max_id, task=True)

        # Find Next Event ID
        if event:
            max_id = self.__event_max_id(prefix)
            return self.__generic_build_id(prefix, year, max_id, event=True)

        # Find Next Work Order ID
        if work_order:
            max_id = self.__generic_get_max_id(self.__work_orders, "work_order_id")
            return self.__generic_build_id("WO", year, max_id)

        # Find Next Procedure ID
        if procedure:
            max_id = self.__generic_get_max_id(self.__maintenance_procedures, "procedure", procedure=True)
            return self.__generic_build_id("MP", year, max_id, procedure=True)

        # Find Next Preventative ID
        if preventative:
            max_id = self.__generic_get_max_id(self.__preventative_maintenance, "preventative_id")
            return self.__generic_build_id("PM", year, max_id)

        # Find Next Service ID
        if service:
            max_id = self.__generic_get_max_id(self.__service_maintenance, "service_id")
            return self.__generic_build_id("SM", year, max_id)

        # Find Next Unplanned ID
        if unplanned:
            max_id = self.__generic_get_max_id(self.__unplanned_maintenance, "unplanned_id")
            return self.__generic_build_id("UM", year, max_id)
        
    def __generic_get_max_id(self, arr: list[dataclass], key: str, procedure: bool = False) -> int:
        """Private Generic Function to Find Max ID from list"""
        if len(arr) == 0:
            return 0
        else:
            max_id = 0
            for x in arr:
                curr_id = int(x[key].split("-")[1 if procedure else 2])
                if curr_id > max_id:
                    max_id = curr_id
            return max_id

    def __task_max_id(self, prefix: str) -> int:
        """Private Function to Find Max ID for a Task with a given Prefix"""
        max_id = 0
        for x in self.__maintenance_tasks:
            if x.task_id[:2] == prefix:
                curr_id = int(x.task_id.split("-")[1])
                if curr_id > max_id:
                    max_id = curr_id
        return max_id

    def __event_max_id(self, prefix: str) -> int:
        """Private Function to Find Max ID for an Event with a given Prefix"""
        max_id = 0
        for x in self.__unplanned_events:
            if x.event_id[:9] == prefix:
                curr_id = int(x.event_id.split("-")[3])
                if curr_id > max_id:
                    max_id = curr_id
        return max_id
        
    def __generic_build_id(self, prefix: str, year: str, id: int, procedure: bool = False, task: bool = False, event: bool = False):
        """Private Generic Function to Build the Next ID"""
        next_id = prefix + "-" + year + "-"
        if procedure or task:
            next_id = prefix + "-"
        if task or event:
            if id < 9:
                next_id += "0"
        else:
            if id < 9:
                next_id += "00"
            elif id < 99:
                next_id += "0"
        next_id += str(id + 1)
        return next_id
    
    def __get_maintenance_type_id(self, preventative: bool = False, service: bool = False, unplanned: bool = False) -> str:
        """Private Functiong that Gets the Corresponding Maintenance Type ID"""
        if preventative:
            return self.__get_referenced_value("preventative", "maintenance_types", "type", "id")
        elif service:
            return self.__get_referenced_value("service", "maintenance_types", "type", "id")
        elif unplanned:
            return self.__get_referenced_value("unplanned", "maintenance_types", "type", "id")

maintenance_handler = MaintenanceHandler()

def dump_tasks(df: DataFrame) -> bool:
    """Function used for dumping tasks from a CSV file"""
    # data = df.to_dict("list")
    divided_tasks = __divide_tasks(db.maintenance_tasks)
    task_ids = []
    location_ids = []
    asset_ids = []
    station_ids = []
    for idx, task in df.iterrows():
        location = __get_room_by_name(task["location"])
        location_ids.append(location.id)
        asset = __get_asset_by_manufacturer(location.id, task["asset"])
        asset_ids.append(asset.id)
        station = __get_station_by_name(location.id, asset.id, task["station"])
        station_ids.append(station.id)
        for freq in divided_tasks.keys():
            if task["frequency"] == freq.capitalize():
                if len(divided_tasks[freq]) == 0:
                    next_id = idx + 1
                    # next_id = __next_idx_for_room_and_asset(location, asset, divided_tasks[freq])
                    task_ids.append(location.name[0].capitalize() + freq[0].capitalize() + f"-{next_id:02d}")
                else:
                    # TODO: implement
                    pass
    df = df.drop(columns=["location", "asset", "station"])
    df["task_id"] = task_ids
    df["location_id"] = location_ids
    df["asset_id"] = asset_ids
    df["station_id"] = station_ids
    print(df)
    
    state = db.insert_by_df("maintenance_tasks", df)
    if state:
        print(f"[SUCCESS] Inserted {df.size} tasks to maintenance tasks table")
    else:
        print("[ERROR] Failed to insert maintenance tasks to table")
    return state

def __divide_tasks(tasks: list[MaintenanceTask]) -> dict[str, list[MaintenanceTask]]:
    """Function used for splitting list of tasks into weekly, monthly, quarterly and annual tasks"""
    divided_tasks = {"weekly": [], "monthly": [], "quarterly": [], "annually": []}
    for task in tasks:
        for k in divided_tasks.keys():
            if task.frequency == k.capitalize():
                divided_tasks[k].append(task)
    
    return divided_tasks

def __get_room_by_name(name: str) -> Location:
    """Function used for getting the Location Object by a given name"""
    return [room for room in db.locations if room.name == name][0]

def __get_asset_by_manufacturer(room_id: str, manufacturer: str) -> Asset:
    """Function used for getting the Asset Object by a given manufacturer"""
    return [asset for asset in db.asset_registrar if asset.manufacturer == manufacturer and asset.location_id == room_id][0]

def __get_station_by_name(room_id: str, asset_id: str, name: str) -> Station:
    """Function Used for getting the Station Object by a given name"""
    print(name)
    return [station for station in db.stations if station.name == name and station.location_id == room_id and station.asset_id == asset_id][0]
