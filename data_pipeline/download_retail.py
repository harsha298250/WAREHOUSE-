import os
import zipfile
import httpx
import pandas as pd
from data_pipeline.registry import DATASET_METADATA, ensure_directories

def download_and_convert_retail():
    meta = DATASET_METADATA["online_retail_ii"]
    raw_path = meta["local_raw_path"]
    ensure_directories()
    
    zip_path = os.path.join(raw_path, "online_retail_ii.zip")
    excel_path = os.path.join(raw_path, "online_retail_II.xlsx")
    csv_path = os.path.join(raw_path, "online_retail_II.csv")
    
    if os.path.isfile(csv_path):
        print(f"Online Retail II CSV already exists at {csv_path}. Skipping download.")
        return
        
    print("Downloading UCI Online Retail II dataset (zip format, ~45MB)...")
    url = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
    
    with httpx.Client(timeout=120.0) as client:
        r = client.get(url)
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            f.write(r.content)
            
    print("Extracting zip archive...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(raw_path)
        
    # Find extracted xlsx file
    extracted_xlsx = None
    for f in os.listdir(raw_path):
        if f.endswith(".xlsx"):
            extracted_xlsx = os.path.join(raw_path, f)
            break
            
    if not extracted_xlsx:
        print("Error: Could not find extracted Excel file in raw directory.")
        return
        
    print(f"Converting Excel file {extracted_xlsx} to CSV {csv_path}...")
    # Read both sheets and combine them
    excel_file = pd.ExcelFile(extracted_xlsx)
    sheets = []
    for sheet_name in excel_file.sheet_names:
        print(f"Reading sheet: {sheet_name}...")
        df = pd.read_excel(extracted_xlsx, sheet_name=sheet_name)
        sheets.append(df)
        
    df_combined = pd.concat(sheets, ignore_index=True)
    df_combined.to_csv(csv_path, index=False)
    print("Conversion complete. Cleaned raw file saved to CSV format successfully.")
    
    # Clean up zip and Excel to save space
    if os.path.isfile(zip_path):
        os.remove(zip_path)
    if os.path.isfile(extracted_xlsx):
        os.remove(extracted_xlsx)

if __name__ == "__main__":
    download_and_convert_retail()
