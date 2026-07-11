from django.urls import path
from . import views

urlpatterns = [

    path(
        'create/',
        views.create_trip,
        name='create_trip'
    ),

    path(
        'delete/<int:trip_id>/',
        views.delete_trip,
        name='delete_trip'
    ),

    path(
        'view/<int:trip_id>/',
        views.view_trip,
        name='view_trip'
    ),

    path(
        'pdf/<int:trip_id>/',
        views.download_pdf,
        name='download_pdf'
    ),

]