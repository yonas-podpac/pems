import streamlit as st
import tomllib
from PIL import Image
from database_handler import DatabaseHandler
from form_manager import FormManager
import os

### PEMS Class ###
# Class used to generate the PEMS UI.
class PEMS:
    def __init__(self):
        # Extract Secrets for Supabase Access
        self.__secrets = st.secrets
        # self.__tables = self.__load_db(self.__secrets["supabase"]["url"], self.__secrets["supabase"]["key"])
        self.__tables = self.__load_db(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

        # Extract UI-Content
        with open("ui_content.toml", "rb") as f:
            self.__ui_data = tomllib.load(f)

        # Initialise Form Manager
        self.__form_manager = FormManager(self.__tables)

        # Setup Session State Variables
        if "active_form" not in st.session_state:
            st.session_state.active_form = None
        
        # Set Page Configuration
        st.set_page_config(page_title="PEMS", page_icon=Image.open("images/favicon.ico"), layout="wide")
        st.title("Podpac Engineering & Maintenance System")

    # Load DB Method
    # Private method used to load database tables. Method uses cache_data 
    # decorator to store results from database to avoid repetitive calls to
    # supabase.
    @st.cache_data
    def __load_db(_self, url: str , key: str) -> dict:
        db = DatabaseHandler(url, key)
        return db.get_tables()
    
    def __render_table(self, name: str, entries: list[dict]) -> list[dict]:
        arr = []
        print(name)
        table_render_data = [x for x in self.__ui_data["table_render"] if x["name"] == name][0]
        for entry in entries:
            d = {}
            for key in entry.keys():
                print(key)
                xref = self.__check_xref(key)
                if key == "id":
                    continue
                elif xref != "":
                    ref = [x for x in self.__ui_data["table_render"] if x["name"] == xref][0]
                    d[
                        self.__rename_column(key, table_render_data["orig_cols"], table_render_data["rename_cols"])
                    ] = [x[ref["xref_column"]] for x in self.__tables[xref] if x[ref["reference"]] == entry[key]][0]
                else:
                    d[self.__rename_column(key, table_render_data["orig_cols"], table_render_data["rename_cols"])] = entry[key]
            arr.append(d)
        return arr
    
    def __check_xref(self, key: str) -> str:
        xref = ""
        for ref in self.__ui_data["table_render"]:
            if ref["foreign_key"] == key:
                xref = ref["name"]
                break

        return xref
    
    def __rename_column(self, column: str, orig_cols=[], rename_cols=[]) -> str:
        val = ""
        if orig_cols.__contains__(column):
            return rename_cols[orig_cols.index(column)]
        arr = column.split("_")
        for idx, s in enumerate(arr):
            val += s.capitalize()
            if idx < column.__len__() - 1:
                val += " "

        return val

    # Render Sidebar
    # Private method used to generate the sidebar for PEMS extracting 
    # data from the UI-Content.
    def __render_sidebar(self):
        # Extract Navigation Bar Data
        navigation_data = self.__ui_data["navigation_data"]
        navigation_list = [x["item"] for x in navigation_data]

        # Generate Streamlit Selectbox from Navigation Items
        self.__menu = st.sidebar.selectbox("Navigation", navigation_list)

        # Return User-Selected item
        return next(obj for obj in navigation_data if obj["item"] == self.__menu)
    
    # Render Name Method
    # Private method used to change the names given from toml files
    # to a human-readable string.
    def __render_name(self, action: str) -> str:
        # Delimit string by hyphen
        words = action.split("-")
        new_str = ""

        # Add capitalised words to new string and return
        for idx, word in enumerate(words):
            new_str += word.capitalize()
            if idx != words.__len__() - 1:
                new_str += " "
        return new_str
    
    # Run Method
    # Public method to run the PEMS app.
    def run(self):
        # Initialise Sidebar
        active_component = self.__render_sidebar()
        st.header(active_component["header"])
        if active_component["table"] != "":
            st.table(self.__render_table(active_component["table"], self.__tables[active_component["table"]]))
        if active_component["actions"][0] != "none":
            cols = st.columns(len(active_component["actions"]))
            for i, action in enumerate(active_component["actions"]):
                with cols[i]:
                    if st.button(self.__render_name(action)):
                        st.session_state.active_form = action
        
        if st.session_state.active_form:
            active_form = st.session_state.active_form
            form_output = self.__form_manager.render_form(st.session_state.active_form)
            if form_output:
                # st.session_state.submitted_data = form_output
                db = DatabaseHandler(self.__secrets["supabase"]["url"], self.__secrets["supabase"]["key"])
                db.insert_data(active_form, form_output)
                st.session_state.active_form = None
                self.__load_db.clear()
                st.rerun()
