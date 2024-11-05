import openpyxl
import pandas as pd
import easyocr  
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.core.files.base import ContentFile


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
        # Load the workbook and select the first sheet
        wb = openpyxl.load_workbook(data_instance.file, data_only=True)
        sheet = wb.active  # Assumes the first sheet is the target

        # Define max rows and columns to preview
        max_rows = 10   # Number of data rows to include
        max_cols = 5    # Number of columns to include

        # Extract data from Excel, including headers
        data = []
        for row in sheet.iter_rows(min_row=1, max_row=max_rows + 1, max_col=max_cols, values_only=True):
            # Convert each cell to a string, replacing None with an empty string
            data.append([str(cell) if cell is not None else "" for cell in row])

        # Identify and remove any unwanted rows (like "Sheet1" or empty headers)
        # Here, assume row 1 contains the column headers
        headers = data[1]  # First row after metadata as headers
        data = data[2:]  # Remove metadata rows from data if present

        # Set up image dimensions and font
        cell_width = 100
        cell_height = 30
        font = ImageFont.load_default()

        img_width = cell_width * max_cols
        img_height = cell_height * (len(data) + 1)  # Extra row for headers

        # Create a blank image with white background
        image = Image.new("RGB", (img_width, img_height), "white")
        draw = ImageDraw.Draw(image)

        # Draw headers
        for col_num, header in enumerate(headers):
            x = col_num * cell_width
            draw.rectangle([x, 0, x + cell_width, cell_height], outline="black", fill="lightgrey")  # Fill for header
            draw.text((x + 5, 5), header, fill="black", font=font)

        # Draw rows and columns with data
        for row_num, row in enumerate(data, start=1):
            for col_num, cell_value in enumerate(row):
                x = col_num * cell_width
                y = row_num * cell_height
                draw.rectangle([x, y, x + cell_width, y + cell_height], outline="black")
                draw.text((x + 5, y + 5), cell_value, fill="black", font=font)

        # Save image to in-memory file
        image_io = BytesIO()
        image.save(image_io, format="PNG")
        image_io.seek(0)

        # Save the image to the preview_image field in the data instance
        data_instance.preview_image.save(f"{data_instance.id}_preview.png", ContentFile(image_io.read()), save=True)