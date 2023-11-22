import pandas as pd

def concat_excels(output_file, *input_files):
    if not input_files:
        print("No input files")
        return
    combined_df = pd.DataFrame()
    for file in input_files:
        try:
            df= pd.read_excel(file)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        except FileNotFoundError:
            print(f"{file} not found")
    
    combined_df.to_excel(output_file, index=False)
    return combined_df





   