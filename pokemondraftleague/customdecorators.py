from django.shortcuts import render, redirect
from django.contrib import messages
from leagues.models import *
from individualleague.models import *

def check_if_league(view):
    def wrap(request, *args, **kwargs):
        try:
            league_=league.objects.get(name=kwargs['league_name'])
            return view(request, *args, **kwargs)
        except Exception as e:
            print(e)
            messages.error(request,'League does not exist!',extra_tags='danger')
            return redirect('league_list')
    return wrap

def check_if_subleague(view):
    def wrap(request, *args, **kwargs):
        try:
            league_=league_subleague.objects.filter(league__name=kwargs['league_name']).get(subleague=kwargs['subleague_name'])
            return view(request, *args, **kwargs)
        except Exception as e:
            print(e)
            print('subleague')
            messages.error(request,'League does not exist!',extra_tags='danger')
            return redirect('league_list')
    return wrap

def check_if_season(view):
    def wrap(request, *args, **kwargs):
        try:
            season=seasonsetting.objects.filter(subleague__league__name=kwargs['league_name']).get(subleague__subleague=kwargs['subleague_name'])
            return view(request, *args, **kwargs)
        except Exception as e:
            print(e)
            print('season')
            messages.error(request,'Season does not exist!',extra_tags='danger')
            return redirect('league_detail',league_name=kwargs['league_name'])
    return wrap

def check_if_team(view):
    def wrap(request, *args, **kwargs):
        try:
            team=coachdata.objects.filter(league_name__name=kwargs['league_name']).get(teamabbreviation=kwargs['team_abbreviation'])
            return view(request, *args, **kwargs)
        except Exception as e:
            print(e)
            print('team')
            messages.error(request,'Team does not exist!',extra_tags='danger')
            return redirect('league_detail',league_name=kwargs['league_name']) 
    return wrap

def check_if_host(view):
    def wrap(request, *args, **kwargs):
        subleague=league_subleague.objects.filter(league__name=kwargs['league_name']).get(subleague=kwargs['subleague_name'])
        if request.user not in subleague.league.host.all():
            messages.error(request,'Only a league host may access a leagues settings!',extra_tags='danger')
            return redirect('leagues_hosted_settings')
        else:    
            return view(request, *args, **kwargs)
    return wrap

def check_if_match(view):
    def wrap(request, *args, **kwargs):
        try:
            match=schedule.objects.get(pk=kwargs['matchid'])
            return view(request, *args, **kwargs)
        except Exception as e:
            print(e)
            print('match')
            messages.error(request,'Match does not exist!',extra_tags='danger')
            return redirect('league_schedule',league_name=kwargs['league_name'])
    return wrap