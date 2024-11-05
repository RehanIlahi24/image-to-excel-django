from django.shortcuts import render
from rest_framework.decorators import api_view
from faker import Faker
from rest_framework.response import Response
import tempfile
from django.http import FileResponse
from image_to_excel_django.utils import *
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import permission_classes
from django.core.files import File
import json
import cv2
import os
from django.conf import settings
from django.http import JsonResponse
import requests
import base64
from .models import *


@api_view(['POST'])
@permission_classes([AllowAny])
def image_to_excel_convert_view(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'Image is required'}, status=400)
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_image_file:
            temp_image_file.write(image.read())
            temp_image_path = temp_image_file.name

        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            os.makedirs(media_root)

        output_excel_path = os.path.join(media_root, 'output_table.xlsx')

        try:
            image_to_excel_converter_function(temp_image_path, output_excel_path)

            data_instance = Data()
            data_instance.image.save(image.name, File(image))
            data_instance.file.save('output_table.xlsx', open(output_excel_path, 'rb'))
            data_instance.save()

            generate_excel_preview(data_instance)

        finally:
            os.remove(temp_image_path)
        
        return Response(Data.objects.filter(id=data_instance.id).values('id', 'image', 'file', 'preview_image', 'created_at').first())
    

@api_view(['POST'])
@permission_classes([AllowAny])
def image_url_to_excel_convert_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        image_data = data.get('image_url')
        
        if not image_data:
            return Response({'error': 'Image data is required'}, status=400)
        
        # Define paths for saving the images
        image_save_path = os.path.join(settings.MEDIA_ROOT, 'images', 'uploaded_image.png')
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        
        # try:
        # If the image is in base64 format, decode it
        if image_data.startswith('data:image/'):
            header, base64_data = image_data.split(',', 1)
            image_bytes = base64.b64decode(base64_data)
            
            with open(image_save_path, 'wb') as image_file:
                image_file.write(image_bytes)
        else:
            # Otherwise, assume it's a URL and download the image
            response = requests.get(image_data, stream=True)
            response.raise_for_status()

            with open(image_save_path, 'wb') as image_file:
                for chunk in response.iter_content(1024):
                    image_file.write(chunk)
        
        # Validate the image using OpenCV
        image = cv2.imread(image_save_path)
        if image is None:
            return Response({'error': 'Failed to load image. The file may be corrupted or unsupported.'}, status=400)
        
        # Re-save the image to ensure compatibility (OpenCV may fix some format issues)
        validated_image_path = os.path.join(settings.MEDIA_ROOT, 'images', 'validated_image.png')
        cv2.imwrite(validated_image_path, image)
        
        # Convert the validated image to Excel
        output_excel_path = os.path.join(settings.MEDIA_ROOT, 'output_table.xlsx')
        image_to_excel_converter_function(validated_image_path, output_excel_path)

        # Save data to the Data model
        data_instance = Data()
        data_instance.image.save('validated_image.png', File(open(validated_image_path, 'rb')))
        data_instance.file.save('output_table.xlsx', open(output_excel_path, 'rb'))
        data_instance.save()

        # Generate a preview if necessary
        generate_excel_preview(data_instance)

        # Return response with saved data
        return Response(Data.objects.filter(id=data_instance.id).values('id', 'image', 'file', 'preview_image', 'created_at').first())
        
        # except (requests.exceptions.RequestException, ValueError) as e:
        #     return Response({'error': f'Failed to process image: {e}'}, status=400)
    

@api_view(['GET', 'DELETE', 'PUT'])
@permission_classes([AllowAny])
def data_view(request):
    if request.method == 'GET':
        data = json.loads(request.body)
        id = data.get('id')
        data_type = data.get('data_type')
        if id:
            data_instance = Data.objects.filter(id=id).first()
            if not data_instance:
                return Response({'error': 'File not found'}, status=400)
            return Response(data_instance.values('id', 'image', 'file', 'preview_image', 'created_at'))
        
        if data_type == 'recent':
            data_instances = Data.objects.order_by('-id')[:5].values('id', 'image', 'file', 'preview_image', 'created_at')
        else:
            data_instances = Data.objects.order_by('-id').values('id', 'image', 'file', 'preview_image', 'created_at')
        return Response(list(data_instances))
    
    if request.method == 'PUT':
        data = json.loads(request.body)
        id = data.get('id')
        new_file_name = data.get('file_name')
        if not id or not new_file_name:
            return Response({'error': 'File name are required'}, status=400)

        data_instance = Data.objects.filter(id=id).first()
        if not data_instance:
            return Response({'error': 'File not found'}, status=400)
        
        data_instance.file.name = new_file_name
        data_instance.save()
        return Response({'message': 'File name updated successfully'})
    
    if request.method == 'DELETE':
        data = json.loads(request.body)
        id = data.get('id')
        if not id:
            return Response({'error': 'ID is required'}, status=400)
        
        data_instance = Data.objects.filter(id=id).first()
        if not data_instance:
            return Response({'error': 'File not found'}, status=400)

        data_instance.delete()
        
        return Response({'message': 'File deleted successfully'})