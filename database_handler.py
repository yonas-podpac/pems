import toml
from supabase import create_client

### Database Handler Class ###
# Class used for selecting, inserting and deleting data from the
# supabase tables tied top PEMS.
class DatabaseHandler:
    def __init__(self, url: str, key: str):
        # Collect Table Names from Config File
        self.__config = toml.load("config.toml")

        # Create Supabase Client
        self.__client = create_client(url, key)

        # Assign Table Data to Local Variable
        self.__select_tables()
    
    # Select Tables Method
    # Private method used to select data from supabase given the
    # table names in the config file and store data in a local
    # variable.
    def __select_tables(self):
        self.__tables = {}
        for name in self.__config["tables"]["names"]:
            self.__tables[name] = self.__client.table(name).select("*").execute().data

    # Get Tables Method
    # Public method used to get the local variable with Supabase
    # data stored therein.
    def get_tables(self) -> dict:
        return self.__tables
    
    def insert_data(self, form_key: str, data: dict):
        spec = [x for x in self.__config["form_entries"] if x["key"] == form_key][0]
        if spec["cross_reference_tables"][0] != "":
            tables = spec["cross_reference_tables"]
            columns = spec["cross_reference_columns"]
            labels = spec["cross_reference_labels"]
            conditions = spec["cross_reference_conditions"]
            for idx, table in enumerate(tables):
                val = data.pop(table)
                data[labels[idx]] = [x[columns[idx]] for x in self._tables[table] if x[conditions[idx]] == val][0]
        self.__client.table(spec["table"]).insert(data).execute()
