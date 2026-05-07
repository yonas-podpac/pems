import streamlit as st
from PIL import Image
from database_handler import DatabaseHandler

class PEMS:
    def __init__(self):
        self.__secrets = st.secrets
        self.__tables = self.load_db(self.__secrets["supabase"]["url"], self.__secrets["supabase"]["key"])
        # self.__db = DatabaseHandler(self.__secrets["supabase"]["url"], self.__secrets["supabase"]["key"])
        st.set_page_config(page_title="PEMS", page_icon=Image.open("images/favicon.ico"), layout="wide")
        st.title("Podpac Engineering & Maintenance System")

    @st.cache_data
    def load_db(_self, url: str , key: str) -> dict:
        db = DatabaseHandler(url, key)
        return db.get_tables()

    def __render_sidebar(self):
        navigation_data = self.__secrets["navigation_data"]
        navigation_list = [x["item"] for x in navigation_data]
        self.__menu = st.sidebar.selectbox("Navigation", navigation_list)

        return next(obj for obj in navigation_data if obj["item"] == self.__menu)
    
    def __render_table(self, table: list[dict], name_replace="") -> list[dict]:
        new_table = []
        for row in table:
            d = {}
            for k in row.keys():
                if k == "id":
                    continue
                elif k == "name":
                    d[k if name_replace == "" else name_replace] = row[k]
                else:
                    d[k] = row[k]
            new_table.append(d)

        return new_table
    
    def __render_button_name(self, action: str) -> str:
        words = action.split("-")
        btn = ""
        for idx, word in enumerate(words):
            btn += word.capitalize()
            if idx != words.__len__() - 1:
                btn += " "
        return btn

    def run(self):
        active_component = self.__render_sidebar()
        st.header(active_component["header"])
        if active_component["table"] != "":
            st.table(
                self.__render_table(
                    self.__tables[f"{active_component["table"]}_table"], 
                    name_replace=active_component["name_column"]
                ), width="content"
            )
        if active_component["actions"][0] != "none":
            cols = st.columns(len(active_component["actions"]))
            for i, action in enumerate(active_component["actions"]):
                with cols[i]:
                    st.button(self.__render_button_name(action))
