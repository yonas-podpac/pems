from pems.components.objects import Asset
from pems.helpers.database import db

class AssetHandler:
    def __init__(self):
        # Retrieve Lists from DB
        self.__asset_registrar = db.asset_registrar
        self.__asset_statuses = db.asset_statuses
        self.__locations = db.locations
        self.__stations = db.stations

    def insert(self, entry: dict, assets=False) -> bool:
        """Function for Inserting an Entry for a Given Table"""
        new_entry = {}
        # Build New Entry for Asset Registrar
        if assets:
            for k in entry.keys():
                if k == "location":
                    new_entry["location_id"] = self.__get_referenced_value(entry[k], "locations", "name", "id")
                elif k == "status":
                    new_entry["status_id"] = self.__get_referenced_value(entry[k], "asset_statuses", "status", "id")
                else:
                    new_entry[k] = entry[k]
            
            # Check if Entry already exists
            exists = False
            for asset in self.__asset_registrar:
                if new_entry["serial_number"] == asset.serial_number:
                    exists = False
                    break
            # TODO: raise error message?

            # Insert Entry if it is Unique
            if exists:
                return False
            else:
                new_row = db.insert("asset_registrar", new_entry)[0]
                self.__asset_registrar.append(Asset(**new_row))
                return True
        
        # TODO: build new entry for other tables?

        return False

    def update(self, index: int, entry: dict, filters=dict[str, str], assets=False) -> bool:
        """Function for Updating an Entry for a Given Table"""
        new_entry = {}
        # Build New Entry for Asset Registrar
        if assets:
            asset = self.__find_asset_by_idx(index, filters=filters)
            new_entry["id"] = asset.id
            for k in entry.keys():
                if k == "location":
                    new_entry["location_id"] = self.__get_referenced_value(entry[k], "locations", "name", "id")
                elif k == "status":
                    new_entry["status_id"] = self.__get_referenced_value(entry[k], "asset_statuses", "status", "id")
                else:
                    new_entry[k] = entry[k]
            
            # Check if there are any changes to New Entry
            change_check = False
            for k in asset.keys():
                if asset[k] != new_entry[k]:
                    change_check = True
                    break
            
            # Update Database if there is Change
            if change_check:
                new_row = db.update("asset_registrar", new_entry, {"id": asset.id})[0]
                self.__asset_registrar[index] = Asset(**new_row)
                return True
            return False
        
        # TODO: implement for other tables?
        return False
    
    def delete(self, index: int, filters=dict[str, str], assets=False) -> bool:
        """Function for Deleting an Entry from a Given Table"""
        # Delete Entry in Asset Registrar
        if assets:
            asset = self.__find_asset_by_idx(index, filters=filters)
            print(asset)
            db.delete("asset_registrar", {"id": asset.id})
            self.__asset_registrar.pop(index)
            return True
        
        # TODO: delete entry for other tables?
        return False

    def columns(self, assets: bool = False, stations: bool = False) -> list[dict[str, str]]:
        """Function for retrieving Form Details by Columns"""
        details = []
        # Build Form Details for Asset Registrar
        if assets:
            details = [
                {"label": "Location", "key": "location", "placeholder": "", "type": "select", "step": ""}, 
                {"label": "Asset Name", "key": "name", "placeholder": "Enter the name of the asset", "type": "text", "step": ""}, 
                {"label": "Serial Number", "key": "serial_number", "placeholder": "Enter the serial number", "type": "text", "step": ""}, 
                {"label": "Manufacturer", "key": "manufacturer", "placeholder": "Enter the manufacturers name", "type": "text", "step": ""}, 
                {"label": "Automated?", "key": "is_automated", "placeholder": "Is it automated?", "type": "checkbox", "step": ""}, 
                {"label": "Model", "key": "model", "placeholder": "Enter the model of the asset", "type": "text", "step": ""}, 
                {"label": "Operational?", "key": "operational", "placeholder": "Operational?", "type": "checkbox", "step": ""}, 
                {"label": "Status", "key": "status", "placeholder": "", "type": "select", "step": ""}
            ]

        # Build Form Details for Stations
        if stations:
            details = [
                {"label": "Location", "key": "location", "placeholder": "", "type": "select", "step": ""}, 
                {"label": "Asset", "key": "asset", "placeholder": "", "type": "select", "step": ""}, 
                {"label": "Name", "key": "name", "placeholder": "Enter the station name", "type": "text", "step": ""}, 
                {"label": "Description", "key": "description", "placeholder": "Enter a description of the station", "type": "text", "step": ""}
            ]

        # TODO: build form details for other tables?

        return details
    
    def entries(self, assets: bool = False, stations: bool = False, asset_id: str = "") -> list[dict[str, any]]:
        """Function for Converting ID Columns in Entries to Cross-Referenced Column & Boolean Entries to Appropriate Value"""
        vals = []
        # Build Entries for Asset Registrar
        if assets:
            for asset in self.__asset_registrar:
                entry = {}
                for k in asset.keys():
                    if k == "id":
                        continue
                    elif k == "location_id":
                        entry["location"] = [area.name for area in self.__locations if area.id == asset.location_id][0]
                    elif k == "is_automated":
                        entry["is_automated"] = "Automated" if asset.is_automated else "Manual"
                    elif k == "operational":
                        entry["operational"] = "Operational" if asset.operational else "Decommissioned"
                    elif k == "status_id":
                        entry["status"] = [state.status for state in self.__asset_statuses if state.id == asset.status_id][0].capitalize()
                    else:
                        entry[k] = asset[k]
                vals.append(entry)

        # Build Entries for Stations
        if stations and asset_id != "":
            for station in self.__stations:
                if station.asset_id == asset_id:
                    entry = {}
                    for k in station.keys():
                        if k == "id":
                            continue
                        elif k == "location_id":
                            entry["location"] = [area.name for area in self.__locations if area.id == station.location_id][0]
                        elif k == "asset_id":
                            entry["manufacturer"] = [asset.manufacturer for asset in self.__asset_registrar if asset.id == station.asset_id][0]
                        else:
                            entry[k] = station[k]
                    vals.append(entry)

        # TODO: build entries for other tables?

        return vals

    def options(self, assets: bool = False) -> dict[str, list[str]]:
        """Function for retrieving Select Options for a Given Table"""
        options = {}
        # Build Options for Asset Registrar Columns
        if assets:
            options["location"] = [room.name for room in self.__locations]
            options["status"] = [status.status.capitalize() for status in self.__asset_statuses]
        
        # TODO: build options for other tables?

        return options
    
    def toggles(self, assets: bool = False) -> dict[str, list[str]]:
        """Function for retrieving Toggle Entries for a Given Table"""
        toggles = {}
        # Build Toggles for Asset Registrar Columns
        if assets:
            toggles["is_automated"] = ["Automated", "Manual"]
            toggles["operational"] = ["Operational", "Decommissioned"]
        
        # TODO: build toggles for other tables?

        return toggles
    
    def filters(self, assets: bool = False) -> dict[str, list[str]]:
        """Function for Rtrieving the Filter Options for a Given Table"""
        filters = {}
        # Build Filters for Asset Registrar Columns
        if assets:
            filters["location"] = [area.name for area in self.__locations]
            filters["manufacturer"] = self.__unique_options("manufacturer", assets=True)
            filters["is_automated"] = ["Automated", "Manual"]
            filters["operational"] = ["Operational", "Decommissioned"]
            filters["status"] = self.__unique_options("status", assets=True)
        
        # TODO: build filters for other tables?

        return filters
    
    def params(self, assets: bool = False) -> list[dict[str, str]]:
        """Function for Retrieving Filter UI Parameters for a Given Table"""
        params = []
        # Build Filter Parameters for Asset Registrar Columns
        if assets:
            params = [
                {"label": "Location", "key": "location"},
                {"label": "Manufacturer", "key": "manufacturer"},
                {"label": "Automated", "key": "is_automated"},
                {"label": "Operational", "key": "operational"},
                {"label": "Status", "key": "status"}
            ]

        # TODO: build filter parmeters for other tables?

        return params

    def find_asset(self, name: str, serial: str) -> Asset:
        """Function for Finding an Asset by Name and Serial Number"""
        return [asset for asset in self.__asset_registrar if asset.name == name and asset.serial_number == serial][0]

    # --- Private Functions ---
    def __find_asset_by_idx(self, index: int, filters=dict[str, str]) -> Asset:
        """Private Function for Finding the Asset ID given the location and the name"""
        if not filters:
            return [asset for asset in self.__asset_registrar][index]
        # Filter Assets
        key_len = len(filters.keys())
        i = 0
        filtered_assets = []
        while (i < key_len):
            buff_assets = []
            if i == 0:
                filtered_assets = self.__asset_registrar
            filter_key = list(filters.keys())[i]
            filter_val = ""
            if filter_key == "location":
                filter_key = "location_id"
                filter_val = self.__get_referenced_value(filters["location"], "locations", "name", "id")
            elif filter_key == "status":
                filter_key = "status_id"
                filter_val = self.__get_referenced_value(filters["status"], "asset_statuses", "status", "id")
            else:
                filter_val = filters[filter_key]
            for asset in filtered_assets:
                if asset[filter_key] == filter_val:
                    buff_assets.append(asset)
            filtered_assets = buff_assets
            i += 1
        return [asset for asset in filtered_assets][index]

    def __unique_options(self, column: str, assets: bool = False) -> list[str]:
        """Private Function to Find the Unique Values for a Given Table"""
        unique_values = []
        # Find Unique Values in Asset Registrar
        if assets:
            for asset in self.__asset_registrar:
                if column == "status":
                    val = self.__get_referenced_value(asset["status_id"], "asset_statuses", "id", "status", capitalise=True)
                    if not val in unique_values:
                        unique_values.append(val)
                elif not asset[column] in unique_values:
                    unique_values.append(asset[column])
        
        # TODO: find unique values for other tables?

        return unique_values
    
    def __get_referenced_value(self, ref_val: str, xref_table: str, xref_column: str, desired_column: str, capitalise=False) -> str:
        if xref_table == "locations":
            val = [area[desired_column] for area in self.__locations if area[xref_column] == ref_val][0]
            return val
        if xref_table == "asset_statuses":
            val = [state[desired_column] for state in self.__asset_statuses if state[xref_column] == ref_val.lower()][0]
            # print(val)
            return val.capitalize() if capitalise else val

asset_handler = AssetHandler()