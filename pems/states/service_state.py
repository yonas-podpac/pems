from datetime import datetime
import reflex as rx
from pems.helpers.maintenance_handler import maintenance_handler
from pems.states.user_state import UserState

class ServiceState(UserState):
    # Schedule Service Form Variables
    work_order_id: str = "WO-000"
    maintenance_id: str = ""
    submitting: bool = False
    service_form_open: bool = False
    title: str = ""
    reported_by: str = ""
    created_at: datetime = datetime.today()
    external: bool = False
    assigned_to: str = ""
    one_area: bool = False
    asset_fields: list[str] = ["asset_0"]
    services: dict[str, dict[str, str]] = {
        "asset_0": {
            "location": "",
            "asset": "",
            "notes": ""
        }
    }
    additional_notes: str = ""
    service_complete: bool = False
    completed_at: datetime = datetime.today()
    downtime: float = 0
    cost: float = 0

    # Work Order Form Variables
    work_order_form_open: bool = False
    print_preview: bool = False

    @rx.var
    def form_complete(self) -> bool:
        return (
            self.title_selected and
            self.reported_by_selected and
            self.assigned_to_selected and
            self.asset_selected
        )
    
    @rx.var
    def title_selected(self) -> bool:
        return self.title != ""
    
    @rx.var
    def reported_by_selected(self) -> bool:
        return self.reported_by != ""
    
    @rx.var
    def assigned_to_selected(self) -> bool:
        return self.assigned_to != ""
    
    @rx.var
    def asset_selected(self) -> bool:
        check = True
        for field in self.asset_fields:
            service = self.services[field]
            check = service["location"] != "" and service["asset"] != ""
            if not check:
                break
        return check
    
    @rx.var
    def service_types(self) -> list[str]:
        return maintenance_handler.service_provider_types
    
    @rx.var
    def scheduled_date(self) -> str:
        return self.created_at.strftime("%Y-%m-%d")
    
    @rx.var
    def locations(self) -> list[str]:
        return maintenance_handler.locations
    
    @rx.var
    def assets(self) -> dict[str, list[str]]:
        options = {}
        for field in self.asset_fields:
            if self.services[field]["location"] == "":
                options[field] = []
            else:
                options[field] = maintenance_handler.get_assets_by_area(self.services[field]["location"])
        return options

    # --- State Functions ---
    def load(self):
        self.work_order_id = ""
        self.maintenance_id = ""
        self.submitting = False
        self.service_form_open = False
        self.asset_fields = ["asset_0"]
        self.title = ""
        self.reported_by = ""
        self.created_at = datetime.today()
        self.external = False
        self.assigned_to = ""
        self.one_area = False
        self.asset_fields = ["asset_0"]
        self.services = {
            "asset_0": {
                "location": "",
                "asset": "",
                "notes": ""
            }
        }
        self.additional_notes = ""
        self.service_complete = False
        self.completed_at = datetime.today()
        self.downtime = 0
        self.cost = 0
        self.work_order_form_open = False

    # --- Schedule Service Form Functions ---
    @rx.event
    def schedule_service(self):
        """Function for Opening the Service Form"""
        self.service_form_open = True
        maintenance_handler.build_work_order_id(service=True)
        self.work_order_id = maintenance_handler.work_order_id
        self.maintenance_id = maintenance_handler.maintenance_id

    @rx.event
    def update_title(self, title: str):
        """Function for Updating the Title"""
        self.title = title
    
    @rx.event
    def update_reported_by(self, employee: str):
        """Function for Setting Employee Name who Scheduled Service"""
        self.reported_by = employee
    
    @rx.event
    def update_created_at(self, date: str):
        """Function for Assigning Service Date"""
        if maintenance_handler.is_valid_date(date, "%Y-%m-%d"):
            self.created_at = datetime.strptime(date, "%Y-%m-%d")

    @rx.event
    def update_external(self, key: str):
        """Function for Setting External or Internal Service Provider"""
        self.external = not self.external

    @rx.event
    def update_assigned_to(self, technician: str):
        """Function for Assigning Technician / Vendor"""
        self.assigned_to = technician

    @rx.event
    def update_one_area(self, key: str):
        """Function for Setting All Locations to one Location or Not"""
        self.one_area = not self.one_area

    @rx.event
    def update_service_location(self, field: str, area: str):
        """Function for Selecting a Location for Servicing"""
        self.services[field]["location"] = area

    @rx.event
    def update_service_asset(self, field: str, asset: str):
        """Function for Selecting an Asset for Servicing"""
        self.services[field]["asset"] = asset

    @rx.event
    def update_service_note(self, field: str, note: str):
        """Function for Adding a Note to a Serviced Asset"""
        self.services[field]["notes"] = note

    @rx.event
    def add_field(self):
        """Function that Adds a new Asset Row"""
        next_idx = len(self.asset_fields)
        self.asset_fields.append("asset_{}".format(next_idx))
        self.services["asset_{}".format(next_idx)] = {"location": self.services["asset_0"]["location"] if self.one_area else "", "asset": "", "notes": ""}

    @rx.event
    def delete_field(self, field: str):
        """Function that Removes an Asset Row"""
        field_idx = int(field.split("_")[1])

        # Check if Field has been Selected
        if self.services.keys().__contains__(field):
            self.services.pop(field)

        # Check if Previous Field Indices Need to be Updated
        keys_to_update = []
        for s_field in self.services.keys():
            idx = int(s_field.split("_")[1])
            if idx > field_idx:
                keys_to_update.append(s_field)
        
        for s_field in keys_to_update:
            service = self.services.pop(s_field)
            idx = int(s_field.split("_")[1])
            self.services["asset_{}".format(idx - 1)] = service
        
        # Remove Last Field
        self.asset_fields.pop()

    @rx.event
    def update_additional_notes(self, notes: str):
        """Function for Adding Additional Notes for the Service Completed"""
        self.additional_notes = notes

    @rx.event
    def update_complete_service(self, key: str):
        """Function for Updating Service Completion"""
        self.service_complete = not self.service_complete

    @rx.event
    def update_completed_at(self, date: str):
        """Function for Updating the Service Completion Date"""
        if maintenance_handler.is_valid_date(date, "%Y-%m-%d"):
            self.completed_at = datetime.strptime(date, "%Y-%m-%d")

    @rx.event
    def update_downtime(self, time: str):
        """Function for Updating the Downtime for the Service"""
        try:
            self.downtime = float(time)
        except:
            self.downtime = 0
    
    @rx.event
    def update_cost(self, cost: str):
        """Function for Updating the Cost for the Service"""
        try:
            self.cost = float(cost)
        except:
            self.cost = 0

    @rx.event
    def toggle(self):
        """Function for Opening or Closing Service Form"""
        self.service_form_open = not self.service_form_open
        self.asset_fields = ["asset_0"]

    @rx.event
    def submit(self, form_data: dict):
        """Function for Submitting Service Form"""
        self.submitting = True
        yield
        # Build list of Asset IDs
        asset_ids = []
        for key, service in self.services.items():
            asset_ids.append(maintenance_handler.get_asset_id_by_area_and_name(service["location"], service["asset"].split(":")[1].lstrip()))
        
        # Build Closed Work Order Entry
        if self.service_complete:
            work_order = maintenance_handler.build_closed_work_order(
                work_order_id=self.work_order_id,
                asset_ids={"ids": asset_ids},
                status="complete",
                reported_by=self.reported_by,
                assigned_to=self.assigned_to,
                created_at=self.created_at,
                completed_at=self.completed_at,
                cost=self.cost,
                service=True
            )
        
        # Build Open Work Order Entry
        else:
            work_order = maintenance_handler.build_open_work_order(
                work_order_id=self.work_order_id,
                asset_ids={"ids": asset_ids},
                status="new",
                reported_by=self.reported_by,
                assigned_to=self.assigned_to,
                created_at=self.created_at,
                service=True
            )

        # Build Service Maintenance Entry
        maintenance_handler.build_service_maintenance(
            title=self.title,
            service_id=self.maintenance_id,
            work_order_id=work_order.id,
            service_type="External" if self.external else "Internal",
            vendor=self.assigned_to if self.external else "N/A",
            notes=self.additional_notes
        )
        
        # Close Form
        self.service_form_open = False
        self.load()
        return rx.redirect("/schedule")

    # --- Work Order Form Functions ---
    def open_work_order_form(self, id: str, complete: bool):
        """Function for Opening a Service Maintenance Work Order"""
        self.work_order_form_open = True
        print(f"Opening Service Work Order Form with ID: {id}")
