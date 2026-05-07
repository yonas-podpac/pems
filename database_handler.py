import toml
from supabase import create_client

class DatabaseHandler:
    def __init__(self, url: str, key: str):
        self.__config = toml.load("config.toml")
        self.__client = create_client(url, key)
        self.__create_tables()
    
    def __create_tables(self):
        self._tables = {}
        for k in self.__config.keys():
            self._tables[k] = self.__client.table(self.__config[k]["name"]).select("*").execute().data

    def get_tables(self) -> dict:
        return self._tables
