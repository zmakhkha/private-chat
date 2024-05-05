from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('player', views.PlayerViewSet, basename = 'player')
router.register('setting', views.SettingsViewSet, basename = 'setting')
urlpatterns = [
    # path('', views.players_list),
    path('', include(router.urls)), 
	path('search/<str:username>',views.PlayerSearchAPIView.as_view(), name='user-search'),
]