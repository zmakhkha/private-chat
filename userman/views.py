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
from .models import Player, FriendshipRequest
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from .serializers import *
from django.db.models import F


class PlayerViewSet(viewsets.ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['GET', 'PUT'])
    def leaderboard(detail=False, methods=['GET']):
        player = Player.objects.all().order_by(sc)
        
    @action(detail=False, methods=['GET', 'PUT'])
    def me(self, request):
        player, created = Player.objects.get_or_create(username=request.user.username)
        if request.method == 'GET':
            serializer = PlayerSerializer(player)

            online_friends = player.friends.filter(status=Player.STATUS_ONLINE)[:10]
            offline_friends = player.friends.filter(status=Player.STATUS_OFFLINE)[:10 - online_friends.count()]
            played_games = GameHistory.objects.filter(player=player)

            # win_rate
            total_games = played_games.count()
            wins = played_games.filter(player=player, player_score__gt=F('opponent_score')).count()
            win_rate = wins / total_games if total_games > 0 else 0

            # trophies_rate
            total_trophies = Achievement.objects.count()
            earned_trophies = AchievementPerUser.objects.filter(user=player).count()
            trophies_rate = earned_trophies / total_games if total_trophies > 0 else 0

            #friends_serializer = PlayerSerializer(online_friends.union(offline_friends), many=True)
            on_friends_serializer = PlayerSerializer(online_friends, many=True)
            off_friends_serializer = PlayerSerializer(offline_friends, many=True)
            games_serializer = GameHistorySerializer(played_games, many=True)

            data = {
                'username': serializer.data['username'],
                'first_name': serializer.data['first_name'],
                'last_name': serializer.data['last_name'],
                'level': player.level,
                'win_rate': win_rate,
                'trophies_rate': trophies_rate,
                'friends': {
                    'online' : on_friends_serializer.data,
                    'offline' : off_friends_serializer.data,
                } ,
                'games': games_serializer.data,
            }
            return Response(data)
        elif request.method == 'PUT':
            serializer = PlayerSerializer(player, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)