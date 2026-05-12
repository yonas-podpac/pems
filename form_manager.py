import streamlit as st
import tomllib

class FormManager:
    def __init__(self, tables):
        self.__tables = tables
        # Load the config once when the class is instantiated
        try:
            with open("form.toml", "rb") as f:
                self.__config = tomllib.load(f)
        except FileNotFoundError:
            st.error(f"Config file 'form.toml' not found!")
            self.config = {}

    def render_form(self, form_key):
        if st.session_state.get("active_form") != form_key:
            return None

        spec = [x for x in self.__config["form"] if x["key"] == form_key][0]
        # print(spec)
        with st.form(form_key):
            results = {}
            options = []
            if spec["selectbox_tables"][0] != "":
                tables = spec["selectbox_tables"]
                columns = spec["selectbox_columns"]
                x_ref_tables = spec["selectbox_cross_reference_tables"]
                x_ref_columns = spec["selectbox_cross_reference_columns"]
                chosen_tables = spec["selectbox_chosen_reference_tables"]
                chosen_columns = spec["selectbox_chosen_reference_columns"]
                for idx, table in enumerate(tables):
                    if x_ref_tables.__contains__(table):
                        options.append(x[columns[idx]] for x in self.__tables[table] if [].__contains__(x[x_ref_columns[idx]]))
                    options.append([x[spec["selectbox_columns"][idx]] for x in self.__tables[table]])
                    print(options)
                for idx, col in enumerate(spec["text_input_columns"]):
                    results[col] = st.text_input(spec["text_input_labels"][idx])
            if spec["number_input_columns"][0] != "":
                for idx, col in enumerate(spec["number_input_columns"]):
                    results[col] = st.number_input(spec["number_input_labels"][idx])
            if spec["radio_columns"][0] != "":
                for idx, col in enumerate(spec["radio_columns"]):
                    results[col] = st.radio(spec["radio_labels"][idx], spec["radio_options"][idx])
            
            cols = st.columns(2)
            with cols[0]:
                if st.form_submit_button("Submit"):
                    st.session_state.active_form = None
                    return results
            with cols[1]:
                if st.form_submit_button("Cancel"):
                    return None
