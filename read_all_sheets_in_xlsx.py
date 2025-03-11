from pathlib import Path

import pandas as pd

icloud_folder = Path().home() / 'Library/Mobile Documents/com~apple~CloudDocs/Documents'
# Read the Excel file
excel_file = pd.ExcelFile(f'{icloud_folder}/TASS/all_years_report.xlsx')
# excel_file = pd.ExcelFile('files_/dataframe_test.xlsx')

# Get all sheet names
sheet_names = excel_file.sheet_names
# print(sheet_names)
# print(len(sheet_names))

# empty DataFrames
all_dfs = pd.DataFrame(columns=['photo_id'])

# Read each sheet into a DataFrame
for i in range(len(sheet_names)):
    # for i in range(2):
    print(sheet_names[i])
    df = pd.read_excel(excel_file, sheet_name=sheet_names[i])
    print(len(df))
    # all_dfs = df.merge(all_dfs, df, on='photo_id', how='outer')
    all_dfs = pd.concat([all_dfs, df], ignore_index=True)

all_dfs = all_dfs.groupby('photo_id', as_index=False).sum()

# Now you have all sheets as DataFrames in the all_dfs dictionary
print(all_dfs)
all_dfs.to_excel('files_/tass_two_years_report.xlsx', index=False)
