import asyncio
from datetime import datetime
import reflex as rx
from pems.helpers.maintenance_handler import maintenance_handler
from pems.components.objects import UnplannedEvent, UnplannedMaintenance
import time
from pems.states.user_state import UserState

class UnplannedState(UserState):
    # Unplanned Maintenance Form Variables
    work_order_id: str = "WO-000"
    maintenance_id: str = ""
    submitting: bool = False
    unplanned_form_open: bool = False
    title: str = ""
    location: str = ""
    asset: str = ""
    station: str = ""
    show_past: bool = False
    past_not_selected: bool = True
    past_um: str = ""
    reported_by: str = ""
    assigned_to: str = ""
    created_at: datetime = datetime.today()
    failure_type: str = ""
    severity: str = ""
    resolved: bool = False
    follow_up_required: bool = False
    completed_at_selected: bool = False
    completed_at: datetime = datetime.today()
    root_cause: str = ""
    description: str = ""
    action_fields: list[str] = ["action_0"]
    incident_titles: dict[str, str] = {"action_0": "Incident 1"}
    events_selected: dict[str, dict[str, bool]] = {"action_0": {
        "event_date": False,
        "event_time": False,
        "duration": False,
        "action_taken": False,
        "spare_part": False,
        "quantity": False
    }}
    events: dict[str, dict[str, str]] = {"action_0": {
        "event_date": datetime.today().strftime("%Y-%m-%d"),
        "event_time": datetime.now().strftime("%H:%M:%S"),
        "duration": 0,
        "action_taken": "",
        "spare_part": "",
        "quantity": 0
    }}
    estimated_downtime: float = 0
    cost: float = 0
    additional_costs: float = 0
    past_um: UnplannedMaintenance = UnplannedMaintenance("", "", "", "", "", "", "", "", "", "", "", 0)
    past_events: list[UnplannedEvent] = []

    # Work Order Form Variables
    work_order_form_open: bool = False
    print_preview: bool = False

    @rx.var
    def form_complete(self) -> bool:
        return (
            self.title_selected and
            self.location_selected and
            self.asset_selected and
            self.station_selected and
            self.reported_by_selected and
            self.assigned_to_selected and 
            self.failure_type_selected and
            self.severity_selected and
            self.description_selected and
            self.completed_at_selected and
            self.root_cause_selected and
            self.event_selected
        )

    @rx.var
    def title_selected(self) -> bool:
        return self.title != ""
    
    @rx.var
    def location_selected(self) -> bool:
        return self.location != ""
    
    @rx.var
    def asset_selected(self) -> bool:
        return self.asset != ""

    @rx.var
    def stations_available(self) -> bool:
        if self.asset_selected:
            return len(self.stations) > 0
        return False
    
    @rx.var
    def station_selected(self) -> bool:
        return self.station != "" or (self.asset_selected and len(self.stations) == 0)
    
    @rx.var
    def reported_by_selected(self) -> bool:
        return self.reported_by != ""
    
    @rx.var
    def assigned_to_selected(self) -> bool:
        return self.assigned_to != ""
    
    @rx.var
    def failure_type_selected(self) -> bool:
        return self.failure_type != ""
    
    @rx.var
    def severity_selected(self) -> bool:
        return self.severity != ""
    
    @rx.var
    def description_selected(self) -> bool:
        return self.description != ""
    
    @rx.var
    def root_cause_selected(self) -> bool:
        return self.root_cause != ""
    
    @rx.var
    def event_selected(self) -> bool:
        check = True
        for field in self.action_fields:
            info = self.events_selected[field]
            check = info["event_date"] and info["event_time"] and info["duration"] and info["action_taken"]
            if not check:
                break
        return check

    @rx.var
    def additional_cost_selected(self) -> bool:
        return self.additional_costs > 0
    
    @rx.var
    def locations(self) -> list[str]:
        return maintenance_handler.locations
    
    @rx.var
    def assets(self) -> list[str]:
        if self.location_selected:
            arr = maintenance_handler.get_assets_by_area(self.location)
            return arr
        return []
    
    @rx.var
    def stations(self) -> list[str]:
        if self.asset_selected and maintenance_handler.are_stations_in_asset(self.location, self.asset):
            return maintenance_handler.get_stations_by_area_and_asset(self.location, self.asset)
        return []

    @rx.var
    def past_ums(self) -> list[str]:
        if self.asset_selected:
            return maintenance_handler.get_past_unplanned_maintenances(self.location, self.asset.split(":")[1].lstrip(), self.station)
        return maintenance_handler.get_past_unplanned_maintenances(self.location, "", self.station)
    
    @rx.var
    def failure_date(self) -> str:
        return self.created_at.strftime("%Y-%m-%d")
    
    @rx.var
    def failure_types(self) -> list[str]:
        return maintenance_handler.failure_types
    
    @rx.var
    def severities(self) -> list[str]:
        return maintenance_handler.severities

    @rx.var
    def resolution_date(self) -> str:
        return self.completed_at.strftime("%Y-%m-%d")
    
    @rx.var
    def root_causes(self) -> list[str]:
        return maintenance_handler.root_causes
    
    @rx.var
    def spare_parts(self) -> list[str]:
        return maintenance_handler.spare_parts

    @rx.var
    def downtime(self) -> str:
        return f"{self.estimated_downtime:.1f} minutes"

    @rx.var
    def cost_repr(self) -> str:
        if self.additional_costs == 0:
            return f"$ {self.cost:.2f}"
        elif self.cost == 0:
            return f"$ {self.additional_costs:.2f}"
        else:
            parts_cost = self.cost - self.additional_costs
            return f"$ {self.cost:.2f} = {parts_cost:.2f} + {self.additional_costs:.2f}"

    # --- State Functions --- 
    def load(self):
        self.work_order_id = ""
        self.maintenance_id = ""
        self.submitting = False
        self.unplanned_form_open = False
        self.title = ""
        self.location = ""
        self.asset = ""
        self.station = ""
        self.show_past = False
        self.past_not_selected = True
        self.reported_by = ""
        self.assigned_to = ""
        self.created_at = datetime.today()
        self.failure_type = ""
        self.severity = ""
        self.resolved = False
        self.follow_up_required = False
        self.completed_at_selected = False
        self.completed_at = datetime.today()
        self.root_cause = ""
        self.description = ""
        self.action_fields = ["action_0"]
        self.incident_titles = {"action_0": "Incident 1"}
        self.events_selected = {"action_0": {
            "event_date": False,
            "event_time": False,
            "duration": False,
            "action_taken": False,
            "spare_part": False,
            "quantity": False
        }}
        self.events = {"action_0": {
            "event_date": datetime.today().strftime("%Y-%m-%d"),
            "event_time": datetime.now().strftime("%H:%M:%S"),
            "duration": 0,
            "action_taken": "",
            "spare_part": "",
            "quantity": 0
        }}
        self.estimated_downtime = 0
        self.cost = 0
        self.additional_costs = 0
        self.past_um = UnplannedMaintenance("", "", "", "", "", "", "", "", "", "", "", 0)
        self.past_events = []

        self.work_order_form_open = False

    # --- Form Functions ---
    @rx.event
    def new_unplanned_maintenance(self):
        """Function for Opening the Unplanned Maintenance Form"""
        self.unplanned_form_open = True
        maintenance_handler.build_work_order_id(unplanned=True)
        self.work_order_id = maintenance_handler.work_order_id
        self.maintenance_id = maintenance_handler.maintenance_id

    @rx.event
    def update_title(self, title: str):
        """Function for Updating the Issue's Title"""
        self.title = title

    @rx.event
    def update_location(self, area: str):
        """Function for Updating the Location where Issue took place"""
        self.location = area

    @rx.event
    def update_asset(self, asset: str):
        """Function for Updating the Machine where Issue took place"""
        self.asset = asset

    @rx.event
    def update_station(self, station: str):
        """Function for Updating the Station where Issue took place"""
        self.station = station

    @rx.event
    def expand_issues(self):
        """Function that Expands Row showing Past Issues"""
        self.show_past = not self.show_past

    @rx.event
    async def update_past_um(self, um_title: str):
        """Function for Updating the Past UM that User has Selected"""
        self.past_not_selected = False

        # Update Form Info from UM
        self.past_um = maintenance_handler.get_um_by_id(um_title.split(":")[0])
        wo = maintenance_handler.get_wo_by_id(self.past_um.work_order_id)
        self.work_order_id = wo.work_order_id
        self.maintenance_id = self.past_um.unplanned_id
        self.reported_by = wo.reported_by
        self.title = self.past_um.title
        self.location = maintenance_handler.get_location_by_id(self.past_um.location_id)
        yield
        await asyncio.sleep(0.05)
        self.asset = maintenance_handler.get_asset_by_id(self.past_um.asset_id)
        yield
        await asyncio.sleep(0.05)
        self.station = maintenance_handler.get_station_by_id(self.past_um.station_id)
        self.reported_by = wo.reported_by
        self.assigned_to = wo.assigned_to
        self.created_at = datetime.strptime(wo.created_at, "%Y-%m-%d")
        self.failure_type = maintenance_handler.get_failure_by_id(self.past_um.failure_id).title()
        self.severity = maintenance_handler.get_severity_by_id(self.past_um.severity_id).title()
        self.description = self.past_um.description
        self.resolved = maintenance_handler.get_status_by_id(wo.status_id) == "complete"
        self.follow_up_required = maintenance_handler.get_status_by_id(wo.status_id) == "on hold"
        if wo.completed_at is not None:
            self.completed_at = datetime.strptime(wo.completed_at, "%Y-%m-%d")
        self.completed_at_selected = True
        self.root_cause = maintenance_handler.get_root_cause_by_id(self.past_um.cause_id).title()
        self.action_fields = []
        self.cost = 0
        for idx, event in enumerate(maintenance_handler.get_events_by_um_id(self.past_um.id)):
            field = f"action_{idx}"
            self.action_fields.append(field)
            part = maintenance_handler.get_spare_part_by_id(event.part_id)
            self.cost += part.unit_cost * event.quantity
            self.incident_titles[field] = f"Incident {idx + 1}"
            self.events_selected[field] = {
                "event_date": True,
                "event_time": True,
                "duration": True,
                "action_taken": True,
                "spare_part": part.name != "",
                "quantity": event.quantity != 0
            }
            self.events[field] = {
                "event_date": event.date,
                "event_time": event.time,
                "duration": event.duration_mins,
                "action_taken": event.action_taken,
                "spare_part": part.name,
                "quantity": event.quantity
            }
            self.past_events.append(event)

        self.estimated_downtime = self.past_um.estimated_downtime_mins
        if wo.cost is not None:
            self.cost = wo.cost
    
    @rx.event
    def update_reported_by(self, employee: str):
        """Function for Updating the Employee who Reported the Issue"""
        self.reported_by = employee
    
    @rx.event
    def update_assigned_to(self, employee: str):
        """Function for Updating the Employee who the Issue was Assigned To"""
        self.assigned_to = employee

    @rx.event
    def update_failure_date(self, date: str):
        """Function for Updating the Failure Date of the Issue"""
        if maintenance_handler.is_valid_date(date, "%Y-%m-%d"):
            self.created_at = datetime.strptime(date, "%Y-%m-%d")

    @rx.event
    def update_failure_type(self, fail: str):
        """Function for Updating the Failure Type for the Issue"""
        self.failure_type = fail

    @rx.event
    def update_severity(self, severity: str):
        """Function for Updating the Severity of the Issue"""
        self.severity = severity

    @rx.event
    def update_description(self, desc: str):
        """Function for Updating the Description of the Event"""
        self.description = desc

    @rx.event
    def update_resolved(self, key: str):
        """Function for Updating the Resolution of the Issue"""
        self.resolved = not self.resolved

    @rx.event
    def update_follow_up(self, key: str):
        """Function for Updating whether Maintenance should be Followed Up with"""
        self.follow_up_required = not self.follow_up_required

    @rx.event
    def update_resolution_date(self, date: str):
        """Function for Updating the Resolution Date"""
        if maintenance_handler.is_valid_date(date, "%Y-%m-%d"):
            self.completed_at_selected = True
            self.completed_at = datetime.strptime(date, "%Y-%m-%d")

    @rx.event
    def update_root_cause(self, cause: str):
        """Function for Updating the Root Cause of the Issue"""
        self.root_cause = cause
        print(f"Title Selected: {self.title_selected}")
        print(f"Location Selected: {self.location_selected}")
        print(f"Asset Selected: {self.asset_selected}")
        print(f"Station Selected: {self.station_selected}")
        print(f"Reported By Selected: {self.reported_by_selected}")
        print(f"Assigned To Selected: {self.assigned_to_selected}")
        print(f"Failure Type Selected: {self.failure_type_selected}")
        print(f"Severity Selected: {self.severity_selected}")
        print(f"Description Selected: {self.description_selected}")
        print(f"Completed At Selected: {self.completed_at_selected}")
        print(f"Root Cause Selected: {self.root_cause_selected}")
        print(f"Event Selected: {self.event_selected}")

    @rx.event
    def add_action_field(self):
        """Function that Adds a new Action Row"""
        next_idx = len(self.action_fields)
        self.action_fields.append("action_{}".format(next_idx))
        self.incident_titles["action_{}".format(next_idx)] = f"Incident {next_idx + 1}"
        self.events_selected["action_{}".format(next_idx)] = {
            "event_date": False,
            "event_time": False,
            "duration": False,
            "action_taken": False,
            "spare_part": False,
            "quantity": False
        }
        self.events["action_{}".format(next_idx)] = {
            "event_date": datetime.today().strftime("%Y-%m-%d"),
            "event_time": datetime.now().strftime("%H:%M:%S"),
            "duration": 0,
            "action_taken": "",
            "spare_part": "",
            "quantity": 0
        }
    
    @rx.event
    def delete_action_field(self, field):
        """Function that Removes an Action Row"""
        field_idx = int(field.split("_")[1])

        # Check if Field has been Selected
        if self.events.keys().__contains__(field):
            self.incident_titles.pop(field)
            self.events_selected.pop(field)
            event = self.events.pop(field)

            # Deduct Cost of Event from Additional Costs
            if self.cost > 0:
                part = maintenance_handler.get_spare_part_by_name(event["spare_part"])
                self.cost -= event["quantity"] * part.unit_cost

            # Deduct Downtime of Event from Total Downtime
            if self.estimated_downtime > 0:
                self.recalculate_estimated_downtime()
        
        # Check if Previous Field Indices Need to be Updated
        keys_to_update = []
        for e_field in self.events.keys():
            idx = int(e_field.split("_")[1])
            if idx > field_idx:
                keys_to_update.append(e_field)
        
        for e_field in keys_to_update:
            self.incident_titles.pop(e_field)
            selected = self.events_selected.pop(e_field)
            event = self.events.pop(e_field)
            idx = int(e_field.split("_")[1])
            self.incident_titles["action_{}".format(idx - 1)] = f"Incident {idx}"
            self.events_selected["action_{}".format(idx - 1)] = selected
            self.events["action_{}".format(idx - 1)] = event
        
        # Remove Last Field
        self.action_fields.pop()

    @rx.event
    def update_event_date(self, field: str, date: str):
        """Function for Updating the Date an Action was Taken to Resolve Issue"""
        if maintenance_handler.is_valid_date(date, "%Y-%m-%d"):
            self.events_selected[field]["event_date"] = True
            self.events[field]["event_date"] = date

    @rx.event
    def update_event_time(self, field: str, t: str):
        """Function for Updating the Time an Action was Taken to Resolve Issue"""
        if maintenance_handler.is_valid_time(t, "%H:%M:%S") or maintenance_handler.is_valid_time(t, "%H:%M"):
            self.events_selected[field]["event_time"] = True
            self.events[field]["event_time"] = t

    @rx.event
    def update_event_duration(self, field: str, duration: str):
        """Function for Updating the Duration of an Action Taken to Resolve Issue"""
        try:
            self.events_selected[field]["duration"] = True
            self.events[field]["duration"] = float(duration)

            # Add Duration for Total Downtime
            self.recalculate_estimated_downtime()
        except:
            pass

    @rx.event
    def update_event_action(self, field: str, action: str):
        """Function for Updating an Action Taken to Resolve Issue"""
        self.events_selected[field]["action_taken"] = True
        self.events[field]["action_taken"] = action

    @rx.event
    def update_event_spare(self, field: str, part: str):
        """Function for Updating a Spare Part used to Resolve Issue"""
        self.events_selected[field]["spare_part"] = True
        self.events[field]["spare_part"] = part

    @rx.event
    def update_event_quantity(self, field: str, amount: str):
        """Function for Updating Number of Spare Parts used to Resolve Issue"""
        try:
            self.events_selected[field]["quantity"] = True
            self.events[field]["quantity"] = int(amount)

            # Add Part Cost to Additional Cost
            part = maintenance_handler.get_spare_part_by_name(self.events[field]["spare_part"])
            self.cost += int(amount) * part.unit_cost
        except:
            pass

    @rx.event
    def update_cost(self, cost: str):
        """Function for Updating the Additional Cost of Resolution"""
        try:
            self.additional_costs = float(cost)
        except:
            pass

    @rx.event
    def toggle(self):
        """Function for Opening or Closing Unplanned Maintenance Form"""
        self.unplanned_form_open = not self.unplanned_form_open
        self.load()

    @rx.event
    def submit(self, form_data: dict):
        """Function for Submiting Unplanned Maintenance Form"""
        self.submitting = True
        yield
        # Handle a new Unplanned Maintenance
        if self.past_um.id == "":
            # Build Closed Work Order Entry
            if self.resolved:
                work_order = maintenance_handler.build_closed_work_order(
                    work_order_id=self.work_order_id,
                    asset_ids={"ids": maintenance_handler.get_asset_id_by_area_and_name(self.location, self.asset.split(":")[1].lstrip())},
                    status="complete",
                    reported_by=self.reported_by,
                    assigned_to=self.assigned_to,
                    created_at=self.created_at,
                    completed_at=self.completed_at,
                    cost=self.cost,
                    unplanned=True
                )
            
            # Build Open Work Order Entry
            else:
                work_order = maintenance_handler.build_open_work_order(
                    work_order_id=self.work_order_id,
                    asset_ids={"ids": maintenance_handler.get_asset_id_by_area_and_name(self.location, self.asset.split(":")[1].lstrip())},
                    status="follow up required" if self.follow_up_required else "new",
                    reported_by=self.reported_by,
                    assigned_to=self.assigned_to,
                    created_at=self.created_at,
                    unplanned=True
                )
            
            # Build Unplanned Maintenance Entry
            print(f"Work Order ID for {self.maintenance_id}: {work_order.id}")
            um = maintenance_handler.build_unplanned_maintenance(
                unplanned_id=self.maintenance_id,
                work_order_id=work_order.id,
                title=self.title,
                location=self.location,
                asset=self.asset,
                station=self.station,
                failure=self.failure_type,
                severity=self.severity,
                cause=self.root_cause,
                description=self.description,
                estimated_downtime=self.estimated_downtime,
                station_available=self.station != ""
            )

            # Build Unplanned Events
            for field in self.events.keys():
                event_id = um.unplanned_id + "-" + str(int(field.split("_")[1]) + 1)
                part = maintenance_handler.get_spare_part_by_name(self.events[field]["spare_part"])

                maintenance_handler.build_unplanned_event(
                    unplanned_id=um.id,
                    event_id=event_id,
                    date=self.events[field]["event_date"],
                    time=self.events[field]["event_time"],
                    duration=self.events[field]["duration"],
                    action=self.events[field]["action_taken"],
                    part_id=part.id,
                    quantity=self.events[field]["quantity"]
                )

                # Update Spare Parts Catalogue if Required
                if part.id != "":
                    maintenance_handler.update_spare_parts_catalogue(part.name, self.events[field]["quantity"])

        # Handle a past Unplanned Maintenance
        else:
            # Check What has been Changed
            entry = {}
            past_location = maintenance_handler.get_location_by_id(self.past_um.location_id)
            past_asset = maintenance_handler.get_asset_by_id(self.past_um.asset_id)
            past_station = maintenance_handler.get_station_by_id(self.past_um.station_id)
            past_failure = maintenance_handler.get_failure_by_id(self.past_um.failure_id)
            past_severity = maintenance_handler.get_severity_by_id(self.past_um.severity_id)
            past_cause = maintenance_handler.get_root_cause_by_id(self.past_um.cause_id)
            if self.past_um.title != self.title:
                entry["title"] = self.title
            if past_location != self.location:
                entry["location_id"] = maintenance_handler.__get_referenced_value(self.location, "locations", "name", "id")
            if past_asset != self.asset:
                entry["asset_id"] = maintenance_handler.get_asset_id_by_area_and_name(self.location, self.asset)
            if past_station != self.station:
                station_id = maintenance_handler.get_station_id_by_area_and_asset_and_name(self.location, self.asset.split(":")[1].lstrip(), self.station)
                entry["station_id"] = None if station_id == "" else station_id
            if past_failure != self.failure_type:
                entry["failure_id"] = maintenance_handler.get_failure_id_by_type(self.failure_type.lower())
            if past_severity != self.severity:
                entry["severity_id"] = maintenance_handler.get_severity_id_by_name(self.severity.lower())
            if past_cause != self.root_cause:
                entry["cause_id"] = maintenance_handler.get_root_cause_id_by_cause(self.root_cause.lower())

            # Update Past Unplanned Maintenance
            if len(entry) > 0:
                maintenance_handler.update_unplanned_maintenance(entry, self.past_um.id)

            # Update Work Order Associated with Unplanned Maintenance
            wo = maintenance_handler.get_wo_by_id(self.past_um.work_order_id)
            wo_status = maintenance_handler.get_status_by_id(wo.status_id)
            entry = {}
            if wo_status != "complete" and self.resolved:
                entry["status_id"] = maintenance_handler.get_status_id_by_status("complete")
            elif wo_status != "new" and not self.resolved:
                entry["status_id"] = maintenance_handler.get_status_id_by_status("new")
            elif wo_status != "follow up required" and self.follow_up_required:
                entry["status_id"] = maintenance_handler.get_status_id_by_status("follow up required")
            if wo.reported_by != self.reported_by:
                entry["reported_by"] = self.reported_by
            if wo.assigned_to != self.assigned_to:
                entry["assigned_to"] = self.assigned_to
            if wo.created_at != self.created_at:
                entry["created_at"] = self.created_at.strftime("%Y-%m-%d")
            if wo.completed_at != self.completed_at:
                entry["completed_at"] = self.completed_at.strftime("%Y-%m-%d")
            if wo.cost != self.cost:
                entry["cost"] = self.cost
            if len(entry) > 0:
                maintenance_handler.update_work_order(entry, wo.id)

            # Update Events if Required
            for field in self.events:
                idx = int(field.split("_")[1])
                entry = {}
                part = maintenance_handler.get_spare_part_by_name(self.events[field]["spare_part"])

                # Update Past Event
                if idx < len(self.past_events):
                    past_event = self.past_events[idx]
                    if past_event.date != self.events[field]["event_date"]:
                        entry["date"] = self.events[field]["event_date"]
                    if past_event.time != self.events[field]["event_time"]:
                        entry["time"] = self.events[field]["event_time"]
                    if past_event.duration_mins != self.events[field]["duration"]:
                        entry["duration_mins"] = self.events[field]["duration"]
                    if past_event.action_taken != self.events[field]["action_taken"]:
                        entry["action_taken"] = self.events[field]["action_taken"]
                    if past_event.part_id != part.id:
                        entry["part_id"] = None if part.id == "" else part.id
                    if past_event.quantity != self.events[field]["quantity"]:
                        entry["quantity"] = self.events[field]["quantity"]
                    if len(entry) > 0:
                        maintenance_handler.update_unplanned_event(entry, past_event.id)

                # Add a New Event to a Past Unplanned Maintenance
                else:
                    new_event_id = self.past_um.unplanned_id + "-" + str(int(field.split("_")[1]) + 1)
                    maintenance_handler.build_unplanned_event(
                        unplanned_id=self.past_um.id,
                        event_id=new_event_id,
                        date=self.events[field]["event_date"],
                        time=self.events[field]["event_time"],
                        duration=self.events[field]["duration"],
                        action=self.events[field]["action_taken"],
                        part_id=part.id,
                        quantity=self.events[field]["quantity"]
                    )

                # Update Spare Parts Catalogue
                if part.id != "":
                    maintenance_handler.update_spare_parts_catalogue(part.name, self.events[field]["quantity"])
        # Close Form
        self.unplanned_form_open = False
        self.load()
        return rx.redirect("/schedule")

    # --- Work Order Form Functions ---
    def open_work_order_form(self, id: str, complete: bool):
        """Function for Opening an Unplanned Maintenance Work Order"""
        self.work_order_form_open = True
        print(f"Opening Unplanned Work Order Form with ID: {id}")

    # --- Helper Functions ---
    def recalculate_estimated_downtime(self):
        """Function for Recalculating the Estimated Downtime"""
        estimated_downtime = 0
        for field in self.events.keys():
            estimated_downtime += self.events[field]["duration"]

        self.estimated_downtime = estimated_downtime
