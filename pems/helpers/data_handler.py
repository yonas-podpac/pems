import pandas as pd
from pandas.core.frame import DataFrame
from pems.helpers.database import db

def csv_to_df(file: bytes) -> DataFrame:
    """Function for converting a CSV into a Dataframe"""
    raw_text = file.decode("utf-8", errors="ignore")
    rows = raw_text.splitlines()
    new_upload = {}
    for header in rows[0].split(","):
        new_upload[header] = []
    for idx, row in enumerate(rows):
        if idx == 0:
            continue
        entries = row.split(",")
        headers = list(new_upload.keys())
        for jdx, entry in enumerate(entries):
            header = headers[jdx]
            new_upload[header].append(entry)

    return pd.DataFrame(new_upload)

def dump_insert(table: str, data: str) -> bool:
    """Function for Inserting Entries to Supabase via CSV Dump"""
    # mapping = [m for m in db.mapping if m["name"] == table][0]
    # TODO: fix this function
    mapping = []
    columns = [""]
    xref_tables = mapping["xref_tables"]
    xref_columns = mapping["xref_columns"]

    # Convert CSV File to DataFrame
    df = csv_to_df(data)

    # Iterate over CSV Rows
    successful_insertion = True
    for i, row in df.iterrows():
        entry = {}
        for k in row.keys():
            rephrased = ""
            k_arr = k.split("_")
            for idx, s in enumerate(k_arr):
                rephrased += s
                if idx < len(k_arr) - 1:
                    rephrased += " "
            
            # Check if entry is mapped to a different column in Supabase
            if columns.__contains__(rephrased):
                m_idx = mapping["columns"].index(rephrased)
                # Check if entry exists in cross-referenced table
                if self.__exists(row[k], xref_tables[m_idx], xref_columns[m_idx]):
                    print(f"{row[k]} exists in {xref_tables[m_idx]}")
                # Avoid inserting in tables with many cross-referenced columns
                elif xref_tables[m_idx] == "locations" or xref_tables[m_idx] == "component_types":
                    print(f"{row[k]} does not exist in {xref_tables[m_idx]}")
                    self.insert(xref_tables[m_idx], {xref_columns[m_idx]: row[k]})
                # Failed to successfully insert into desired table
                else:
                    successful_insertion = False
            entry[k] = row[k]
        
        # Only insert to table if no issues with cross-referencing
        if successful_insertion:
            db.insert(table, entry)
        
        return successful_insertion
