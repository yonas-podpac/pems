from gotrue.errors import AuthApiError
from io import BytesIO
from pems.components.objects import *
from postgrest.exceptions import APIError
from supabase import create_client, Client, PostgrestAPIResponse
import toml

class DatabaseHandler:
    """Handler for Supabase Database"""
    PARAMETER_MAXIMUM = 65535

    def __init__(self):
        self.__secrets = toml.load("./secrets.toml")
        self.__config = toml.load("./config.toml")
        self.__client: Client = create_client(self.__secrets["SUPABASE_URL"], self.__secrets["SUPABASE_KEY"])
        self.__connection = False
        self.__asset_registrar = []
        self.__asset_settings_changes = []
        self.__asset_statuses = []
        self.__component_types = []
        self.__components = []
        self.__extraction_analysis_history = []
        self.__failure_types = []
        self.__faults = []
        self.__locations = []
        self.__maintenance_frequencies = []
        self.__maintenance_procedures = []
        self.__maintenance_tasks = []
        self.__maintenance_types = []
        self.__preventative_maintenance = []
        self.__production_output = []
        self.__production_output_units = []
        self.__roles = []
        self.__root_causes = []
        self.__service_maintenance = []
        self.__service_provider_types = []
        self.__severities = []
        self.__spare_parts = []
        self.__stations = []
        self.__unplanned_events = []
        self.__unplanned_maintenance = []
        self.__user_profiles = []
        self.__work_order_statuses = []
        self.__work_orders = []
        self.__connection_status = self.__build_local_objects(self.__config["tables"])

    @property
    def connection(self) -> bool:
        return self.__connection
    
    @property
    def connection_status(self) -> str:
        return self.__connection_status
    
    @property
    def filters(self) -> dict[str, any]:
        return self.__config["filters"]

    @property
    def tables(self) -> list[str]:
        return self.__config["tables"]
    
    @property
    def asset_registrar(self) -> list[Asset]:
        return self.__asset_registrar

    @property
    def asset_settings_changes(self) -> list[AssetSettingsChange]:
        return self.__asset_settings_changes
    
    @property
    def asset_statuses(self) -> list[AssetStatus]:
        return self.__asset_statuses
    
    @property
    def component_types(self) -> list[ComponentType]:
        return self.__component_types
    
    @property
    def components(self) -> list[Component]:
        return self.__components
    
    @property
    def extraction_analysis_history(self) -> list[ExtractionAnalysisHistory]:
        return self.__extraction_analysis_history
    
    @property
    def failure_types(self) -> list[FailureType]:
        return self.__failure_types

    @property
    def faults(self) -> list[Fault]:
        return self.__faults
    
    @property
    def locations(self) -> list[Location]:
        return self.__locations
    
    @property
    def maintenance_frequencies(self) -> list[MaintenanceFrequency]:
        return self.__maintenance_frequencies
    
    @property
    def maintenance_procedures(self) -> list[MaintenanceProcedure]:
        return self.__maintenance_procedures
    
    @property
    def maintenance_tasks(self) -> list[MaintenanceTask]:
        return self.__maintenance_tasks
    
    @property
    def maintenance_types(self) -> list[MaintenanceType]:
        return self.__maintenance_types
    
    @property
    def preventative_maintenance(self) -> list[PreventativeMaintenance]:
        return self.__preventative_maintenance

    @property
    def production_output(self) -> list[ProductionOutput]:
        return self.__production_output

    @property
    def production_output_units(self) -> list[ProductionOutputUnit]:
        return self.__production_output_units
    
    @property
    def roles(self) -> list[Role]:
        return self.__roles
    
    @property
    def root_causes(self) -> list[RootCause]:
        return self.__root_causes
    
    @property
    def service_maintenance(self) -> list[ServiceMaintenance]:
        return self.__service_maintenance
    
    @property
    def service_provider_types(self) -> list[ServiceProviderType]:
        return self.__service_provider_types
    
    @property
    def severities(self) -> list[Severity]:
        return self.__severities
    
    @property
    def spare_parts(self) -> list[SparePart]:
        return self.__spare_parts
    
    @property
    def stations(self) -> list[Station]:
        return self.__stations

    @property
    def unplanned_events(self) -> list[UnplannedEvent]:
        return self.__unplanned_events
    
    @property
    def unplanned_maintenance(self) -> list[UnplannedMaintenance]:
        return self.__unplanned_maintenance
    
    @property
    def user_profiles(self) -> list[UserProfile]:
        return self.__user_profiles
    
    @property
    def work_order_statuses(self) -> list[WorkOrderStatus]:
        return self.__work_order_statuses
    
    @property
    def work_orders(self) -> list[WorkOrder]:
        return self.__work_orders

    # --- Public Functions ---
    def select(self, table: str, columns: str = "*", filters: dict[str, any] = {}) -> list[dict[str, any]]:
        """Function performing the SQL Select Function"""
        query = self.__client.table(table).select(columns)

        # Apply Filers if Required
        if len(filters) > 0:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        # Execute Query
        response = query.execute()
        return response.data
    
    def insert(self, table: str, data: dict[str, any]) -> list[dict[str, any]]:
        """Function performing the SQL Insert Function"""
        query = self.__client.table(table).insert(data)
        response = query.execute()
        self.__build_local_objects([table])
        # print(response)
        return response.data

    def insert_multiple(self, table: str, data: list[dict[str, any]]) -> list[dict[str, any]]:
        """Function performing multiple SQL Insert Functions"""
        session = self.__client.auth.get_session()
        if session is None:
            print("Session expired or missing! User is operating as anon.")
        else:
            print("User authenticated:", session.user.id)
        query = self.__client.table(table).insert(data)
        response = query.execute()
        self.__build_local_objects([table])
        return response.data
    
    def update(self, table: str, data: dict[str, any], filters: dict[str, any]) -> list[dict[str, any]]:
        """Function perfoming the SQL Update Function"""
        if not filters:
            print("[ERROR] Update query must include filters to avoid updating all rows")
            return []

        query = self.__client.table(table).update(data)
        for key, value in filters.items():
            query = query.eq(key, value)
        
        response = query.execute()

        # Rebuild Local List
        self.__build_local_objects([table])
        return response.data
    
    def delete(self, table: str, filters: dict[str, any]) -> list[dict[str, any]]:
        """Function performing the SQL Delete Function"""
        if not filters:
            print("[ERROR] Delete query must include filters to avoid wiping the whole table")
            return []
        # session = self.__client.auth.get_session()
        # if session is None:
        #     print("Session expired or missing! User is operating as anon.")
        # else:
        #     print("User authenticated:", session.user.id)
        
        query = self.__client.table(table).delete()
        for key, value, in filters.items():
            query = query.eq(key, value)
        response = query.execute()
        print(response)
        # TODO: delete query is not executing properly
        return response.data
    
    def login(self, username: str, password: str) -> bool:
        """Function for Logging In to PEMS using Supabase's Authenication"""
        try:
            email = ""
            if "@podpac.com.au" in username:
                email = username
            else:
                email = [user.email_address for user in self.__user_profiles if user.username == username][0]

            response = self.__client.auth.sign_in_with_password({
                "email": email.strip(),
                "password": password.strip()
            })

            if response.session:
                print(f"[SUCCESS] {username} logged in")
                return True
            print(f"[ERROR] Login credentials wrong for {username}")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to login for {username}: {e}")
            return False
        
    def logout(self) -> bool:
        """Function for Logging Out of PEMS using Supabase's Authentication"""
        try:
            self.__client.auth.sign_out()
            print(f"[SUCCESS] Current user has been logged out")
            return True
        except Exception as e:
            print(f"[ERROR] An unexpected error has occurred: {e}")
            return False
        
    def check_active_session(self) -> str:
        """"Function for Checking if there is a User currently logged into PEMS"""
        try:
            response = self.__client.auth.get_user()

            if response and response.user:
                email = response.user.user_metadata.get("username", response.user.email)
                print(f"[SUCCESS] User with email {email} is logged in")
                return email
            else:
                print(f"[SUCCESS] No active user")
                return ""
        except Exception as e:
            print(f"[WARNING] Session check failed or no user logged in: {e}")
            return ""

    def signup(self, email: str, password: str) -> bool:
        """Function for Signing Up a new User to PEMS using Supabase's Authentication"""
        try:
            response = self.__client.auth.sign_up({
                "email": email,
                "password": password
            })
            if response.user:
                print(f"[SUCCESS] verification email sent to {email}")
                return True
            print(f"[ERROR] Something went wrong for signing up {email}")
            return False
        except AuthApiError as e:
            print(f"[ERROR] Supabase API Authentication error: {e.message}")
            return False
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred: {e}")
            return False
        
    def request_reset_password(self, username: str) -> bool:
        """Function for Reseting User's Password using Supabase's Authentication"""
        try:
            email = ""
            if "@podpac.com.au" in username:
                email = username
            else:
                email = [user.email_address for user in self.__user_profiles if user.username == username][0]

            self.__client.auth.reset_password_for_email(
                email,
                {"redirect_to": "http://localhost:3000/reset-password"}
            )
            print(f"[SUCCESS] Email sent to {email} for password reset")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to reset password for {username}: {e}")
            return False
        
    def reset_password(self, username: str, password: str) -> bool:
        try:
            self.__client.auth.update_user({"password": password})
            print(f"[SUCCESS] Password updated for {username}")
            return True
        except Exception as e:
            print(f"[ERROR] Reset password failed: {e}")
            return False
        
    def store_to_bucket(self, bucket: str, path: str, is_image: bool = False, data: bytes = b""):
        """Function for Storing Data or Image to a Supabase Bucket"""
        self.__client.storage.from_(bucket).upload(
            path=path,
            file=data,
            file_options={"content-type": "image/png" if is_image else "text/csv", "upsert": "true"}
        )
    
    def retrieve_bytes_from_bucket(self, bucket: str, path: str) -> list[dict]:
        return self.__client.storage.from_(bucket).download(path)
        
    def add_local_object(self, table: str, obj: dict[str, any]):
        """Function for Adding a Local Object"""
        if table == "asset_registrar":
            self.__asset_registrar.append(Asset(**obj))
        if table == "asset_settings_changes":
            self.__asset_settings_changes.append(AssetSettingsChange(**obj))
        if table == "asset_statuses":
            self.__asset_statuses.append(AssetStatus(**obj))
        if table == "component_types":
            self.__component_types.append(ComponentType(**obj))
        if table == "components":
            self.__components.append(Component(**obj))
        if table == "extraction_analysis_history":
            self.__extraction_analysis_history.append(ExtractionAnalysisHistory(**obj))
        if table == "failure_types":
            self.__failure_types.append(FailureType(**obj))
        if table == "faults":
            self.__faults.append(Fault(**obj))
        if table == "locations":
            self.__locations.append(Location(**obj))
        if table == "maintenance_frequencies":
            self.__maintenance_frequencies.append(MaintenanceFrequency(**obj))
        if table == "maintenance_procedures":
            self.__maintenance_procedures.append(MaintenanceProcedure(**obj))
        if table == "maintenance_tasks":
            self.__maintenance_tasks.append(MaintenanceTask(**obj))
        if table == "maintenance_types":
            self.__maintenance_types.append(MaintenanceType(**obj))
        if table == "preventative_maintenance":
            self.__preventative_maintenance.append(PreventativeMaintenance(**obj))
        if table == "production_output":
            self.__production_output.append(ProductionOutput(**obj))
        if table == "production_output_units":
            self.__production_output_units.append(ProductionOutputUnit(**obj))
        if table == "roles":
            self.__roles.append(Role(**obj))
        if table == "root_causes":
            self.__root_causes.append(RootCause(**obj))
        if table == "service_maintenance":
            self.__service_maintenance.append(ServiceMaintenance(**obj))
        if table == "service_provider_types":
            self.__service_provider_types.append(ServiceProviderType(**obj))
        if table == "severities":
            self.__severities.append(Severity(**obj))
        if table == "spare_parts":
            self.__spare_parts.append(SparePart(**obj))
        if table == "stations":
            self.__stations.append(Station(**obj))
        if table == "unplanned_events":
            self.__unplanned_events.append(UnplannedEvent(**obj))
        if table == "unplanned_maintenance":
            self.__unplanned_maintenance.append(UnplannedMaintenance(**obj))
        if table == "user_profiles":
            self.__user_profiles.append(UserProfile(**obj))
        if table == "work_order_statuses":
            self.__work_order_statuses.append(WorkOrderStatus(**obj))
        if table == "work_orders":
            self.__work_orders.append(WorkOrder(**obj))

    # --- Private Functions ---
    def __build_local_objects(self, tables: list[str]) -> str:
        """Function for building lists of objects from Supabase Tables"""
        try:
            # Build Local Objects Lists
            for table in tables:
                data = self.select(table)
                if table == "asset_registrar":
                    self.__asset_registrar = [Asset(**row) for row in data]
                if table == "asset_settings_changes":
                    self.__asset_settings_changes = [AssetSettingsChange(**row) for row in data]
                if table == "asset_statuses":
                    self.__asset_statuses = [AssetStatus(**row) for row in data]
                if table == "component_types":
                    self.__component_types = [ComponentType(**row) for row in data]
                if table == "components":
                    self.__components = [Component(**row) for row in data]
                if table == "extraction_analysis_history":
                    self.__extraction_analysis_history = [ExtractionAnalysisHistory(**row) for row in data]
                if table == "failure_types":
                    self.__failure_types = [FailureType(**row) for row in data]
                if table == "fault":
                    self.__faults = [Fault(**row) for row in data]
                if table == "locations":
                    self.__locations = [Location(**row) for row in data]
                if table == "maintenance_frequencies":
                    self.__maintenance_frequencies = [MaintenanceFrequency(**row) for row in data]
                if table == "maintenance_procedures":
                    self.__maintenance_procedures = [MaintenanceProcedure(**row) for row in data]
                if table == "maintenance_tasks":
                    self.__maintenance_tasks = [MaintenanceTask(**row) for row in data]
                if table == "maintenance_types":
                    self.__maintenance_types = [MaintenanceType(**row) for row in data]
                if table == "preventative_maintenance":
                    self.__preventative_maintenance = [PreventativeMaintenance(**row) for row in data]
                if table == "production_output":
                    self.__production_output = [ProductionOutput(**row) for row in data]
                if table == "production_output_units":
                    self.__production_output_units = [ProductionOutputUnit(**row) for row in data]
                if table == "roles": 
                    self.__roles = [Role(**row) for row in data]
                if table == "root_causes":
                    self.__root_causes = [RootCause(**row) for row in data]
                if table == "service_maintenance":
                    self.__service_maintenance = [ServiceMaintenance(**row) for row in data]
                if table == "service_provider_types":
                    self.__service_provider_types = [ServiceProviderType(**row) for row in data]
                if table == "severities":
                    self.__severities = [Severity(**row) for row in data]
                if table == "spare_parts":
                    self.__spare_parts = [SparePart(**row) for row in data]
                if table == "stations":
                    self.__stations = [Station(**row) for row in data]
                if table == "unplanned_events":
                    self.__unplanned_events = [UnplannedEvent(**row) for row in data]
                if table == "unplanned_maintenance":
                    self.__unplanned_maintenance = [UnplannedMaintenance(**row) for row in data]
                if table == "user_profiles":
                    self.__user_profiles = [UserProfile(**row) for row in data]
                if table == "work_order_statuses":
                    self.__work_order_statuses = [WorkOrderStatus(**row) for row in data]
                if table == "work_orders":
                    self.__work_orders = [WorkOrder(**row) for row in data]

            # Set Connection Variables
            self.__connection = True
            return "Connected to Supabase"
        except APIError as e:
            self.__connection = False
            return f"API Error (check table / row name): {e}"
        except Exception as e:
            self.__connection = False
            return f"Connection Failed; check your URL, keys, or network: {e}"
        
# Create Static Database Handler
db = DatabaseHandler()