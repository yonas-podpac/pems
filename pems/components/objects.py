from dataclasses import dataclass
import time

@dataclass
class Asset:
    id: str
    location_id: str
    name: str
    serial_number: str
    manufacturer: str
    is_automated: bool
    model: str
    operational: bool
    status_id: str

    # Allows for Asset['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "location_id", "name", "serial_number", "manufacturer", "is_automated", "model", "operational", "status_id"]

@dataclass
class AssetSettingsChange:
    id: str
    location_id: str
    asset_id: str
    timestamp: str
    setting_name: str
    old_value: float
    new_value: float

    # Allows for AssetSettingChange['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self) -> list[str]:
        return ["id", "location_id", "asset_id", "timestamp", "setting_name", "old_value", "new_value"]

@dataclass
class AssetStatus:
    id: str
    status: str

    # Allows for AssetStatus['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "status"]
    
@dataclass
class ComponentConditions:
    id: str
    condition: str

    # Allows for ComponentCondition['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "condition"]

@dataclass
class ComponentType:
    id: str
    type: str

    # Allows for ComponentType['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "type"]

@dataclass
class Component:
    id: str
    location_id: str
    asset_id: str
    station_id: str
    component_id: str
    condition_id: str
    name: str
    part_id: str
    manufacturer: str

    # Allows for Component['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "location_id", "asset_id", "station_id", "component_id", "condition_id", "name", "part_id", "manufacturer"]
    
@dataclass
class ExtractionAnalysisHistory:
    id: str
    created_at: str
    research_id: str
    analysis_type: str
    capsule_group: int
    capsule_type: str
    lid_material: str
    coffee_profile: str
    dose_weight: float
    grind_setting: float
    pack_date: str
    grind_date: str
    path: str
    plot_paths: dict[str, str]

    # Allows for ExtractionAnalysisHistory['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "created_at", "research_id", "analysis_type", "capsule_group", "capsule_type", "lid_material", "coffee_profile", "dose_weight", "grind_setting", "pack_date", "grind_date", "path", "plot_paths"]

@dataclass
class FailureType:
    id: str
    failure: str

    # Allows for FailureType['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "failure"]

@dataclass
class Fault:
    id: str
    location_id: str
    asset_id: str
    timestamp: str
    fault_code: str
    duration_seconds: int
    description: str

    # Allows for Fault['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self) -> list[str]:
        return["id", "location_id", "asset_id", "timestamp", "fault_code", "duration_seconds", "description"]

@dataclass
class Location:
    id: str
    name: str
    is_production: bool

    # Allows for Location['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "name", "is_production"]
    
@dataclass
class MaintenanceFrequency:
    id: str
    frequency: str

    # Allows for MaintenanceFrequency['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "frequency"]

@dataclass
class MaintenanceProcedure:
    id: str
    procedure: str
    title: str
    frequency_id: str
    repeats_on: dict[str, str]
    estimated_duration_mins: int

    # Allows for MaintenanceProcedure["key"] to be called
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self) -> list[str]:
        return ["id", "procedure", "title", "frequency_id", "repeats_on", "estimated_duration_mins"]

@dataclass
class MaintenanceTask:
    id: str
    procedure_id: str
    task_id: str
    location_id: str
    asset_id: str
    station_id: str
    job: str

    # Allows for MaintenanceTask['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "procedure_id", "task_id", "location_id", "asset_id", "station_id", "job"]

@dataclass
class MaintenanceType:
    id: str
    type: str

    # Allows for MaintenanceTask['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self) -> list[str]:
        return ["id", "type"]

@dataclass
class PreventativeMaintenance:
    id: str
    preventative_id: str
    work_order_id: str
    procedure_id: str
    task_status: dict[str, dict[str, str]]
    notes: str
 
    # Allows for PreventativeMaintenance['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self) -> list[str]:
        return ["id", "preventative_id", "work_order_id", "procedure_id", "task_status", "notes"]

@dataclass
class ProductionOutput:
    id: str
    location_id: str
    asset_id: str
    timestamp: str
    total: float
    good: float
    rejected: float
    unit_id: str

    # Allows for ProductionOutput['key'] to be called
    def __getitem__(self, key):
        return getattr(key)

    def keys(self) -> list[str]:
        return ["id", "location_id", "asset_id", "timestamp", "total", "good", "rejected", "unit_id"]

@dataclass
class ProductionOutputUnit:
    id: str
    unit: str

    # Allows for ProductionOutputUnit['key'] to be called
    def __getitem__(self, key):
        return getattr(key)

    def keys(self) -> list[str]:
        return ["id", "unit"]
    
@dataclass
class Role:
    id: str
    role: str

    # Allows for Roles["key"] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "role"]

@dataclass
class RootCause:
    id: str
    cause: str

    # Allows for RootCause['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "cause"]
    
@dataclass
class ServiceMaintenance:
    id: str
    service_id: str
    title: str
    work_order_id: str
    service_provider_id: str
    vendor_company_name: str
    notes: str

    # Allows for ServiceMaintenance['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "service_id", "title", "work_order_id", "service_provider_id", "vendor_company_name", "notes"]

@dataclass
class ServiceProviderType:
    id: str
    type: str

    # Allows for ServiceProviderType['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "type"]

@dataclass
class Severity:
    id: str
    severity: str

    # Allows for Severity['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "severity"]

@dataclass
class SparePart:
    id: str
    component_id: str
    name: str
    part_number: str
    on_hand: int
    condition_id: str
    manufacturer: str
    supplier: str
    unit_cost: float

    # Allows for SparePart['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "component_id", "name", "part_number", "on_hand", "condition_id", "manufacturer", "supplier", "unit_cost"]

@dataclass
class Station:
    id: str
    location_id: str
    asset_id: str
    name: str
    description: str

    # Allows for Station['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "location_id", "asset_id", "name", "description"]

@dataclass
class UnplannedEvent:
    id: str
    unplanned_id: str
    event_id: str
    date: str
    time: str
    duration_mins: float
    action_taken: str
    part_id: str
    quantity: int

    # Allows for UnplannedTask['key'] to be called
    def __getattr__(self, name):
        return getattr(self, name)

    def keys(self) -> list[str]:
        return ["id", "unplanned_id", "event_id", "date", "time", "duration_mins", "action_taken", "part_id", "quantity"]
    
@dataclass
class UnplannedMaintenance:
    id: str
    unplanned_id: str
    work_order_id: str
    title: str
    location_id: str
    asset_id: str
    station_id: str
    failure_id: str
    severity_id: str
    cause_id: str
    description: str
    estimated_downtime_mins: float

    # Allows for UnplannedMaintenance['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "unplanned_id", "work_order_id", "title", "location_id", "asset_id", "station_id", "failure_id", "severity_id", "cause_id", "description", "event_ids", "estimated_downtime_mins"]

@dataclass
class UserProfile:
    id: str
    username: str
    email_address: str
    name: str
    role_id: str

    # Allows for UserProfiles["key"] to be called
    def __getitem__(self, key):
        return getattr(self, key)
    
    def keys(self) -> list[str]:
        return ["id", "username", "email_address", "name", "role_id"]

@dataclass
class WorkOrderStatus:
    id: str
    status: str

    # Allows for WorkOrderStatus['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self) -> list[str]:
        return ["id", "status"]

@dataclass
class WorkOrder:
    id: str
    work_order_id: str
    asset_ids: dict[str, list[str]]
    type_id: str
    status_id: str
    reported_by: str
    assigned_to: str
    created_at: str
    completed_at: str
    cost: float

    # Allows for WorkOrder['key'] to be called
    def __getitem__(self, key):
        return getattr(self, key)

    def keys(self) -> list[str]:
        return ["id", "work_order_id", "asset_ids", "type_id", "status_id", "reported_by", "assigned_to", "created_at", "completed_at", "cost"]
