from django.urls import path

from . import views
urlpatterns = [
    path('<int:id>', views.home_view, name='home_view'),
    path('addProduct/<int:id>', views.add_view, name='add_view')
]