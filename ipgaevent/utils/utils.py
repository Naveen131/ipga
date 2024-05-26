import random
import imghdr
import io
import magic
import PyPDF2
import requests
from django.db import models
from django.http import JsonResponse
from drf_extra_fields.fields import Base64FileField
from rest_framework.pagination import PageNumberPagination



class FileFieldManager:
    def __init__(self, instance):
        self.instance = instance

    def delete_file(self, field_name):
        try:
            field = getattr(self.instance, field_name)
            if field and hasattr(field, 'delete'):
                field.delete(save=False)
        except Exception as e:
            # Handle any errors that may occur during deletion
            print(f"Error deleting {field_name}: {str(e)}")

    def delete_old_files(self, data):
        for field in self.instance._meta.fields:
            if isinstance(field, models.FileField) and field.name in data:
                old_file = getattr(self.instance, field.name)
                if old_file:
                    self.delete_file(field.name)


class APIResponse(JsonResponse):
    def __init__(self, data=None, status_code=200, message="Request succeeded", **kwargs):
        # Check if the status code indicates success or failure
        is_success = 200 <= status_code < 300
        status_code = 200 if status_code < 500 else status_code

        response_data = {
            "status": "success" if is_success else "error",
            "message": message,
            "data": data,
        }
        if kwargs:
            response_data.update(kwargs)

        super().__init__(data=response_data, status=status_code)


class CustomPagination(PageNumberPagination):
    default_page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        # import pdb;pdb.set_trace()
        pagination_data = {
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
        }

        # Remove keys with None values
        pagination_data = {k: v for k, v in pagination_data.items() if v is not None}

        return APIResponse(data=data, status_code=200, message="Request succeeded", **pagination_data)


class CustomBase64FileField(Base64FileField):
    ALLOWED_TYPES = ['pdf', 'png', 'jpg', 'jpeg']

    def get_file_extension(self, filename, decoded_file):
        # import pdb;pdb.set_trace()
        image_format = imghdr.what(None, h=decoded_file)
        if image_format in self.ALLOWED_TYPES:
            return image_format

        try:
            magic_instance = magic.Magic(mime=True)
            mime_type = magic_instance.from_buffer(decoded_file)
        except magic.MagicException:
            pass
        else:
            if mime_type.startswith('image'):
                return mime_type.split('/')[1]

        try:
            PyPDF2.PdfFileReader(io.BytesIO(decoded_file))
        except PyPDF2.utils.PdfReadError:
            pass
        else:
            return 'pdf'

        return None