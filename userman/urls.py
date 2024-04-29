from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register('', views.PlayerViewSet)
urlpatterns = [
    # path('', views.players_list),
    path('', include(router.urls)), 
]