import pandas as pd
import easyocr  
from io import BytesIO


def image_to_excel_converter_function(image_path, output_path):
    reader = easyocr.Reader(['en'])
    
    easyocr_result = reader.readtext(image_path)

    if not easyocr_result:
        empty_df = pd.DataFrame()
        empty_df.to_excel(output_path, index=False, header=False)
        return
    
    easyocr_result.sort(key=lambda x: x[0][0][1])

    rows = []
    current_row = []
    current_y = None

    for result in easyocr_result:
        top_left_y = result[0][0][1]
        if current_y is None or abs(top_left_y - current_y) <= 10:
            current_row.append(result)
            current_y = top_left_y
        else:
            rows.append(current_row)
            current_row = [result]
            current_y = top_left_y
    
    if current_row:
        rows.append(current_row)
    
    num_columns = len(rows[0])
    
    data_matrix = []
    for row in rows:
        row.sort(key=lambda x: x[0][0][0])
        row_data = [text for _, text, _ in row]
        if len(row_data) < num_columns:
            row_data.extend([''] * (num_columns - len(row_data)))
        data_matrix.append(row_data)
    
    df = pd.DataFrame(data_matrix)
    df.to_excel(output_path, index=False, header=False)