from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core import serializers
from django.db.models import Q
from django.core.files import File

import json
from datetime import datetime
import time
import csv
import os
import requests

from django.core.files.temp import NamedTemporaryFile

import urllib.request
from PIL import Image

from accounts.forms import UserRegisterForm
from .models import *
from accounts.models import *
from leagues.models import *
from individualleague.models import *
from pokemonadmin.models import *

from replayanalysis.ShowdownReplayParser.replayparser import *
from replayanalysis.helperfunctions import *

# Create your views here.
def home(request):
    try:
        yourleagues=coachdata.objects.all().filter(Q(coach=request.user)|Q(teammate=request.user))
        if yourleagues.count()>0:
            upcomingmatches=schedule.objects.all().filter(Q(team1__coach=request.user)|Q(team2__coach=request.user)|Q(team1__teammate=request.user)|Q(team2__teammate=request.user)).filter(replay="Link")[0:4]
            recentresults=schedule.objects.all().filter(Q(team1__coach=request.user)|Q(team2__coach=request.user)|Q(team1__teammate=request.user)|Q(team2__teammate=request.user)).exclude(replay="Link").exclude(Q(team1__coach=request.user)|Q(team1__teammate=request.user),team1alternateattribution__isnull=False).exclude(Q(team2__coach=request.user)|Q(team2__teammate=request.user),team2alternateattribution__isnull=False).order_by('-timestamp','-id')[0:4]
            context = {
                "title": "Pokemon Draft League",
                "yourleagues": yourleagues,
                "upcomingmatches":upcomingmatches,
                "recentresults": recentresults,
            }
            return  render(request,"coachlandingpage.html", context)
    except:
        print("error")
    form=UserRegisterForm()
    context = {
        "title": "Pokemon Draft League",
        "form": form,
    }
    return  render(request,"index.html", context)

def about(request):
    coachs=[]
    coachlist=coachdata.objects.all().exclude(league_name__name__contains="Test")
    for c in coachlist:
        if c.coach.username not in coachs:
            coachs.append(c.coach.username)
        if c.teammate and c.teammate.username not in coachs:
            coachs.append(c.teammate.username) 
    coachlist=historical_team.objects.all().exclude(coach1__username="UnclaimedCoach")
    for c in coachlist:
        if c.coach1.username not in coachs:
            coachs.append(c.coach1.username)
        if c.coach2 and c.coach2.username not in coachs:
            coachs.append(c.coach2.username) 
    leagues=league.objects.all().exclude(name__contains="Test")
    historicalmatches=historical_match.objects.all().exclude(replay="").exclude(replay__contains="FF")
    currentmatches=schedule.objects.all().exclude(replay="Link").exclude(replay__contains="FF")
    seasonscompleted=0
    for l in leagues:
        seasonscompleted+=historical_team.objects.all().filter(league=l).distinct('seasonname').count()
    context = {
        "numberofleagues":leagues.count(),
        "uniquecoaches": len(coachs),
        "seasonscompleted":seasonscompleted,
        "matchesplayed": currentmatches.count()+historicalmatches.count(),
    }
    return  render(request,"about.html", context)

def custom404(request,exception):
    return  render(request,"404.html")

def custom500(request,exception):
    return  render(request,"500.html")

def discordbotpage(request):
    return  render(request,"discordbot.html")

def pokemonleaderboard(request):
    leaderboard=pokemon_leaderboard.objects.all().filter(gp__gt=0).order_by('-kills','-differential')
    context = {
        "title": "Pokemon Leaderboard",
        "leaderboard": leaderboard
    }
    return  render(request,"pokemonleaderboard.html",context)

def userleaderboard(request):
    leaderboard=profile.objects.all().filter(Q(wins__gt=0)|Q(losses__gt=0)).order_by('-wins','-differential').exclude(user__username="UnclaimedCoach")
    context = {
        "title": "User Leaderboard",
        "leaderboard": leaderboard
    }
    return  render(request,"userleaderboard.html",context)

def pickemleaderboard(request):
    leaderboard=pickem_leaderboard.objects.all().order_by('-numbercorrect').exclude(matchescompleted__lt=1)
    context = {
        "title": "Pickem Leaderboard",
        "leaderboard": leaderboard
    }
    return  render(request,"pickemleaderboard.html",context)

def runscript(request):
    mostdrafted=pokemon_leaderboard.objects.all().order_by('-timesdrafted')[0:20]
    for item in mostdrafted:
        print(item.pokemon)
    return redirect('home')

def awardcheck(coach,awardtogive,awardtext,messagebody,admin):
    try:
        coachaward.objects.filter(coach=coach, award=awardtogive).get(text=awardtext)
    except:
        inbox.objects.create(sender=admin,recipient=coach,messagesubject='You have been awarded a trophy!', messagebody=messagebody)
        coachaward.objects.create(coach=coach,award=awardtogive,text=awardtext)

def findpoke(team1,team2,pokemonname,line_count):
    try:
        item=historical_roster.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).filter(team=team1).get(pokemon__pokemon=pokemonname)
    except:
        try:
            item=historical_roster.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).filter(team=team1).get(pokemon__pokemon=f'{pokemonname}-Mega')
        except:
            try:
                item=historical_roster.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).filter(team=team1).get(pokemon__pokemon=f'{pokemonname}-Mega-X')
            except:
                try:
                    item=historical_roster.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).filter(team=team1).get(pokemon__pokemon=f'{pokemonname}-Mega-Y')
                except:
                    try:
                        historical_freeagency.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).filter(team=team1).get(droppedpokemon__pokemon=pokemonname)   
                        item=all_pokemon.objects.all().get(pokemon=pokemonname)
                    except Exception as e:
                        try:
                            historical_freeagency.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).filter(team=team1).get(droppedpokemon__pokemon=f'{pokemonname}-Mega')   
                            item=all_pokemon.objects.all().get(pokemon=f'{pokemonname}-Mega')
                        except:
                            try:
                                historical_freeagency.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).filter(team=team1).get(droppedpokemon__pokemon=f'{pokemonname}-Mega-X')   
                                item=all_pokemon.objects.all().get(pokemon=f'{pokemonname}-Mega-X')
                            except:
                                try:
                                    historical_freeagency.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).filter(team=team1).get(droppedpokemon__pokemon=f'{pokemonname}-Mega-Y')   
                                    item=all_pokemon.objects.all().get(pokemon=f'{pokemonname}-Mega-Y')
                                except:
                                    try:
                                        historical_freeagency.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).get(droppedpokemon__pokemon=pokemonname)   
                                        item=all_pokemon.objects.all().get(pokemon=pokemonname)
                                    except Exception as e:
                                        try:
                                            historical_freeagency.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).get(droppedpokemon__pokemon=f'{pokemonname}-Mega')   
                                            item=all_pokemon.objects.all().get(pokemon=f'{pokemonname}-Mega')
                                        except:
                                            try:
                                                historical_freeagency.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).get(droppedpokemon__pokemon=f'{pokemonname}-Mega-X')   
                                                item=all_pokemon.objects.all().get(pokemon=f'{pokemonname}-Mega-X')
                                            except:
                                                try:
                                                    historical_freeagency.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).get(droppedpokemon__pokemon=f'{pokemonname}-Mega-Y')   
                                                    item=all_pokemon.objects.all().get(pokemon=f'{pokemonname}-Mega-Y')
                                                except:
                                                    try:
                                                        item=historical_roster.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).get(pokemon__pokemon=pokemonname)
                                                    except:
                                                        try:
                                                            item=historical_roster.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).get(pokemon__pokemon=f'{pokemonname}-Mega')
                                                        except:
                                                            try:
                                                                item=historical_roster.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).get(pokemon__pokemon=f'{pokemonname}-Mega-X')
                                                            except:
                                                                try:
                                                                    item=historical_roster.objects.all().filter(team__league=team1.league,team__seasonname=team1.seasonname).get(pokemon__pokemon=f'{pokemonname}-Mega-Y')
                                                                except:
                                                                    item=all_pokemon.objects.all().get(pokemon=f'{pokemonname}')
                                                                    print(f'{line_count}. {pokemonname}')                      
    return item