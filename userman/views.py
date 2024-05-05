from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Player
from .serializers import *


from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import *
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from .serializers import *
from django.db.models import F

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Player
from .serializers import PlayerSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly 

class PlayerSearchAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly] 
    def get(self, request, username):
        if username:
            users = Player.objects.filter(username__icontains=username)
            serialized_players = PlayerSerializer(users, many=True)
            return Response(serialized_players.data)
        else:
            return Response({'message' : 'No username provided'}, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class SettingsViewSet(ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = SettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def list(self, request):
        user = self.get_object()
        serialized_player = self.get_serializer(user)
        return Response(serialized_player.data)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serialized_player = self.get_serializer(user, data=request.data)
        serialized_player.is_valid(raise_exception=True)
        self.perform_update(serialized_player)
        return Response(serialized_player.data)
    


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET'])
    def leaderboard(detail=False, methods=['GET']):
        player = Player.objects.all().order_by('-level')
        leaderboard_serializer = LeaderBoardSerializer(player, many=True)
        return Response(leaderboard_serializer.data)
        
    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        player, created = Player.objects.get_or_create(username=request.user.username)
        if request.method == 'GET':
            serializer = PlayerSerializer(player)

            #friends
            online_friends = player.friends.filter(status=Player.STATUS_ONLINE)[:10]
            offline_friends = player.friends.filter(status=Player.STATUS_OFFLINE)[:10 - online_friends.count()]
            on_friends_serializer = PlayerSerializer(online_friends, many=True)
            off_friends_serializer = PlayerSerializer(offline_friends, many=True)

            # win_rate && games
            played_games = GameHistory.objects.filter(player=player)
            total_games = played_games.count()
            wins = played_games.filter(player=player, player_score__gt=F('opponent_score')).count()
            win_rate = wins / total_games if total_games > 0 else 0
            games_serializer = GameHistorySerializer(played_games, many=True)

            # achievements_rate && achievement per user
            total_trophies = Achievement.objects.count()
            earned_achievement = AchievementPerUser.objects.filter(user=player)
            earned_achievement_count = earned_achievement.count()
            achievements_rate = earned_achievement_count / total_trophies if total_trophies > 0 else 0
            achievements_per_user_serializer = AchievementPerUserSerializer(earned_achievement, many=True)

            # items per user
            earned_items = ItemsPerUser.objects.filter(user=player)
            item_per_user_serializer = ItemsPerUserSerializer(earned_items, many=True)

            data = {
                'avatar' : serializer.data['image'],
                'username': serializer.data['username'],
                'first_name': serializer.data['first_name'],
                'last_name': serializer.data['last_name'],
                'level': player.level,
                'win_rate': win_rate,
                'achievements_rate': achievements_rate,
                'friends': {
                    'online' : on_friends_serializer.data,
                    'offline' : off_friends_serializer.data,
                } ,
                'games': games_serializer.data,
                'achievements' : achievements_per_user_serializer.data,
                'items':item_per_user_serializer.data,
            }
            return Response(data)
        elif request.method == 'PUT':
            serializer = PlayerSerializer(player, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)