import pandas as pd
import easyocr  
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.core.files import File
import os

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

def generate_excel_preview(data_instance):
    if data_instance.file:
        df = pd.read_excel(data_instance.file.path) 
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.axis('off')

        if df.empty:
            ax.text(0.5, 0.5, "No data found", ha='center', va='center', fontsize=15, color='red', fontweight='bold')
        else:
            table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.2)

        preview_image_path = "excel_image.png" 
        plt.savefig(preview_image_path, bbox_inches='tight', dpi=300)
        plt.close()

        with open(preview_image_path, 'rb') as img_file:
            data_instance.preview_image.save('excel_preview.png', File(img_file), save=True)

        os.remove(preview_image_path)