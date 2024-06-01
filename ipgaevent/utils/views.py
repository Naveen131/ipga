from django.db import transaction, models
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from utils.utils import CustomPagination, APIResponse, FileFieldManager


# from utils.common.utils import CustomPagination, APIResponse, FileFieldManager


class ListAPIViewWithPagination(generics.ListAPIView):
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        queryset = self.get_queryset()

        # Apply pagination
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        # If not paginated, serialize the entire queryset
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(data=serializer.data)


class CustomCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        serializer = self.serializer_class(data=request.data, context={"request": request})
        if not serializer.is_valid():
            errors = []
            for field, messages in serializer.errors.items():
                errors.append(messages[0] if type(messages) == list else messages)

            return APIResponse(data=None, status_code=400,
                               message=errors[0].__str__() if type(errors[0])=='rest_framework.exceptions.ErrorDetail'
                               else errors[0])

        data = serializer.validated_data
        try:
            instance = serializer.create(data)
            if isinstance(instance, dict):
                return APIResponse(data=instance, status_code=200, message="success")

            elif isinstance(instance, models.Model):
                data = self.get_view_serializer(instance).data
                return APIResponse(data=data, status_code=200, message="success")
            return APIResponse(data=data, status_code=200, message="success")
        except Exception as e:
            return APIResponse(data=None, status_code=400, message=str(e))

    def get_view_serializer(self, instance):
        raise NotImplementedError("Subclasses must implement this method")


class CustomRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    # lookup_field = 'pk'

    def get_view_serializer(self, instance):
        raise NotImplementedError("Subclasses must implement this method")

    def get(self, request, *args, **kwargs):
        # import pdb;pdb.set_trace()
        try:
            instance = self.get_object()
            data = self.get_view_serializer(instance).data
            return APIResponse(data=data, message='success', status_code=200)
        except Exception as e:
            return APIResponse(data=None, message="Object Does not exist", status_code=400)

    @transaction.atomic
    def put(self, request, *args, **kwargs):

        instance = self.get_object()

        if not instance:
            return APIResponse(data=None, message="Object Does not exist", status_code=400)
        serializer = self.serializer_class(data=request.data, context={'request': request})
        if not serializer.is_valid():
            errors = []
            for field, messages in serializer.errors.items():
                errors.extend((messages[0] if type(messages) == list else messages))

            return APIResponse(data=None, status_code=400,
                               message=errors[0].__str() if type(errors[0])=='rest_framework.exceptions.ErrorDetail'
                               else errors[0])

        data = serializer.validated_data
        try:
            file_manager = FileFieldManager(instance)
            file_manager.delete_old_files(serializer.validated_data)
            instance = serializer.update(instance, data)
            data = self.get_view_serializer(instance).data
            return APIResponse(data=data, status_code=200, message="success")
        except Exception as e:
            return APIResponse(data=None, status_code=400, message=str(e))

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return APIResponse(data=None, status_code=200, message="success")

