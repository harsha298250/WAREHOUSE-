import os
import zipfile

def extract_archive():
    zip_path = "c:/Users/harsh/Downloads/archive.zip"
    dest_dir = "c:/Users/harsh/Downloads/warehouse_project_v3/warehouse_v3/data/raw/retail_sales_forecasting"
    
    if not os.path.exists(zip_path):
        print(f"Error: {zip_path} not found.")
        return
        
    print(f"Extracting {zip_path} to {dest_dir}...")
    os.makedirs(dest_dir, exist_ok=True)
    
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
        
    print("Extraction completed successfully.")

if __name__ == "__main__":
    extract_archive()
