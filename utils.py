import requests
import pandas as pd
import os
# add your filter values in params.py
from params import inputs

def download_xlsx_file(target_date):
    url = f'https://www.enexgroup.gr/documents/20126/200106/{target_date}_EL-DAM_Results_EN_v01.xlsx'
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'data/{target_date}.xlsx', 'wb') as file:
            file.write(response.content)
            #  print('ok')
        return f'data/{target_date}.xlsx'
    else:
        raise Exception(f"Failed to download file for {target_date}.")



def fill_empty_cells(data_frame, empty_cells):

    column_names = data_frame.columns
    for column_name in column_names[empty_cells]:
        df_column = data_frame[column_name]
        df_type = df_column.dtypes

        for index, value in df_column.items():
            if pd.isna(data_frame.loc[index, column_name]):

                if df_type == str:
                    data_frame.at[index, column_name] = 'NULL'
                elif df_type == float:
                    data_frame.at[index, column_name] = 'NaN'
                elif df_type == int:
                    data_frame.at[index, column_name] = 'NaN'
                elif df_type == object:
                    data_frame.at[index, column_name] = 'NaN'
                else:
                    data_frame.at[index, column_name] = 'NaN'
                
    return data_frame

# Save the modified DataFrame to a new Excel file
def save_new_file(df):
    new_file_name = 'data/new.xlsx'
    df.to_excel(new_file_name, index=False)


def open_file(path):
    # check if file exists in given path
    if os.path.exists(path):
        try:
            df = pd.read_excel(path)
            return df
        except Exception as e:
            return f"Error reading file: {str(e)}"
    else:
        return f"File '{path}' does not exist."


def find_headers(df, search_value):
    header_list = {}
    for value in search_value:
        # after find the  first header that contains 'search_value', breaks loop
        for column in df:
            if value in df[column].values:
                header_list[column] = value
                break

    return header_list



def parse_and_aggregate_data(file_path):
    df = open_file(file_path)

    # if not a DataFrame, return error
    if not isinstance(df, pd.DataFrame):
        return df

    data_frame = pd.DataFrame(df)

    # checks if DataFrame contains empty cells
    empty_cells = data_frame.isna().any()

    # If columns contain empty cells, iterate through the corresponding column and fill it with NULL if String or Nan if something else.
    if not empty_cells.any():

        data_frame = fill_empty_cells(data_frame, empty_cells)
        save_new_file(data_frame)

    # find the headers of the columns which contains 'Sell' and 'Imports' records
    if len(inputs):
        header_list = find_headers(data_frame, inputs)
    else:
        return 'Please insert filter params in params.py and try again!'
        
    
    # transform to this --> filtered_df = data_frame[(data_frame['SIDE_DESCR'] == "Sell") & (data_frame['CLASSIFICATION'] == "Imports")]
    mask = None
    for key, value in header_list.items():
        if mask is None:
            mask = (data_frame[key] == value)
        else:
            mask = mask & (data_frame[key] == value)

    # Apply the filter to the DataFrame
    filtered_df = data_frame[mask]

    # Group by "SORT" and compute the sum of "TOTAL_TRADES"
    aggregated_df = filtered_df.groupby('SORT').agg({"TOTAL_TRADES": "sum"}).reset_index()
    # print(aggregated_df)

    # Convert the result to a list of dictionaries
    result = aggregated_df.to_dict(orient="records")

    # print(result)
    return result
    # print(filtered_data)