from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core import serializers
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

import json
from datetime import datetime
import time

from .models import *
from .forms import *
from leagues.models import *
from accounts.models import showdownalts
from .ShowdownReplayParser.replayparser import *
from .NewParser.parser import *
from .helperfunctions import *
from pokemondraftleague.customdecorators import check_if_subleague, check_if_league, check_if_season, check_if_team, check_if_host, check_if_match

def replay_analysis(request):
    if request.method=="POST":
        form = MatchReplayForm(request.POST)
        if form.is_valid():
            url=form.cleaned_data['url']
            outputstring, team1, team2 = replayparse(url)
            context={
                'output': outputstring,
                'team1':team1,
                'team2':team2,
                'replay': url,
            }
            return render(request,"replayanalysisform.html",context)
    form=MatchReplayForm()
    context={
        'form': form,
        'submission': True,
    }
    return  render(request,"replayanalysisform.html",context)

def replay_analysis2(request):
    if request.method=="POST":
        form = MatchReplayForm(request.POST)
        if form.is_valid():
            url=form.cleaned_data['url']
            results = newreplayparse(url)
            context={
                'results': results,
            }
            return render(request,"replayanalysisresults.html",context)
    form=MatchReplayForm()
    context={
        'form': form,
        'submission': True,
    }
    return  render(request,"replayanalysisform.html",context)

@check_if_subleague
@check_if_season
@check_if_match
@login_required
def upload_league_replay(request,league_name,subleague_name,matchid):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_teams=subleague.subleague_coachs.all().order_by('teamname')
    match=schedule.objects.get(pk=matchid)
    if match.replay != "Link":
        messages.error(request,f'A replay for that match already exists!',extra_tags="danger")
        return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
    if request.method=="POST":
        form = LeagueReplayForm(request.POST,instance=match)
        if form.is_valid():
            url=form.cleaned_data['replay']
            outputstring, team1, team2 = replayparse(url)
            coach1=team1.coach
            coach2=team2.coach
            try:
                coach1alt=showdownalts.objects.all().filter(showdownalt=coach1).first()
                coach1team=coachdata.objects.all().filter(league_name=subleague.league).filter(Q(coach=coach1alt.user)|Q(teammate=coach1alt.user)).first()
            except:
                messages.error(request,f'A matching showdown alt for {coach1} was not found!',extra_tags='danger')
                return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
            try:
                coach2alt=showdownalts.objects.all().filter(showdownalt=coach2).first()
                coach2team=coachdata.objects.all().filter(league_name=subleague.league).filter(Q(coach=coach2alt.user)|Q(teammate=coach2alt.user)).first()
                print(coach2alt)
            except:
                messages.error(request,f'A matching showdown alt for {coach2} was not found!',extra_tags='danger')
                return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
            context={
                'output': outputstring,
                'team1':team1,
                'team2':team2,
                'team1name':coach1team,
                'team2name':coach2team,
                'replay': url,
                'confirm': True,
                'form': form,
                'league_name':league_name,
                'matchid':matchid,
                'subleague': subleague,
                'leaguepage': True,
                'league_teams': league_teams,
            }
            return render(request,"replayanalysisform.html",context)
    form=LeagueReplayForm(instance=match,initial={"replay":""})
    context={
        'form': form,
        'submission': True,
        'league_name':league_name,
        'matchid':matchid,
        'subleague': subleague,
        'leaguepage': True,
        'league_teams': league_teams,
    }
    return  render(request,"replayanalysisform.html",context)

@check_if_subleague
@check_if_season
@check_if_match
@login_required
def confirm_league_replay(request,league_name,subleague_name,matchid):
    league_name=league_name.replace('%20',' ')
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    season=subleague.seasonsetting
    league_teams=subleague.subleague_coachs.all().order_by('teamname')
    match=schedule.objects.get(pk=matchid)
    if request.method=="POST":
        if match.replay != "Link":
            messages.error(request,f'A replay for that match already exists!',extra_tags="danger")
            return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
        form = LeagueReplayForm(request.POST,instance=match)
        if form.is_valid():
            url=form.cleaned_data['replay']
            outputstring, team1, team2 = replayparse(url)
            coach1=team1.coach
            coach2=team2.coach
            try:
                coach1alt=showdownalts.objects.all().filter(showdownalt=coach1).first()
                coach1team=coachdata.objects.all().filter(league_name=subleague.league).filter(Q(coach=coach1alt.user)|Q(teammate=coach1alt.user)).first()
            except:
                messages.error(request,f'No coach matching {team1.coach} could be found!',extra_tags="danger")
                return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
            try:
                coach2alt=showdownalts.objects.all().filter(showdownalt=coach2).first()
                coach2team=coachdata.objects.all().filter(league_name=subleague.league).filter(Q(coach=coach2alt.user)|Q(teammate=coach2alt.user)).first()
            except:
                messages.error(request,f'No coach matching {team1.coach} could be found!',extra_tags="danger")
                return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
            #update team1 pokemon data
            t1pokemon1=checkpokemon(team1.pokemon1,season,coach1team,league_name,request)
            t1pokemon2=checkpokemon(team1.pokemon2,season,coach1team,league_name,request)
            t1pokemon3=checkpokemon(team1.pokemon3,season,coach1team,league_name,request)
            t1pokemon4=checkpokemon(team1.pokemon4,season,coach1team,league_name,request)
            t1pokemon5=checkpokemon(team1.pokemon5,season,coach1team,league_name,request)
            t1pokemon6=checkpokemon(team1.pokemon6,season,coach1team,league_name,request)
            t1pokemon1.kills+=team1.P1K
            t1pokemon1.deaths+=team1.P1F
            t1pokemon1.differential+=team1.P1Diff
            t1pokemon1.gp+=1
            t1pokemon1.gw+=team1.win
            t1pokemon2.kills+=team1.P2K
            t1pokemon2.deaths+=team1.P2F
            t1pokemon2.differential+=team1.P2Diff
            t1pokemon2.gp+=1
            t1pokemon2.gw+=team1.win
            t1pokemon3.kills+=team1.P3K
            t1pokemon3.deaths+=team1.P3F
            t1pokemon3.differential+=team1.P3Diff
            t1pokemon3.gp+=1
            t1pokemon3.gw+=team1.win
            t1pokemon4.kills+=team1.P4K
            t1pokemon4.deaths+=team1.P4F
            t1pokemon4.differential+=team1.P4Diff
            t1pokemon4.gp+=1
            t1pokemon4.gw+=team1.win
            t1pokemon5.kills+=team1.P5K
            t1pokemon5.deaths+=team1.P5F
            t1pokemon5.differential+=team1.P5Diff
            t1pokemon5.gp+=1
            t1pokemon5.gw+=team1.win
            t1pokemon6.kills+=team1.P6K
            t1pokemon6.deaths+=team1.P6F
            t1pokemon6.differential+=team1.P6Diff
            t1pokemon6.gp+=1
            t1pokemon6.gw+=team1.win
            #update team2 pokemon data
            t2pokemon1=checkpokemon(team2.pokemon1,season,coach2team,league_name,request)
            t2pokemon2=checkpokemon(team2.pokemon2,season,coach2team,league_name,request)
            t2pokemon3=checkpokemon(team2.pokemon3,season,coach2team,league_name,request)
            t2pokemon4=checkpokemon(team2.pokemon4,season,coach2team,league_name,request)
            t2pokemon5=checkpokemon(team2.pokemon5,season,coach2team,league_name,request)
            t2pokemon6=checkpokemon(team2.pokemon6,season,coach2team,league_name,request)
            t2pokemon1.kills+=team2.P1K
            t2pokemon1.deaths+=team2.P1F
            t2pokemon1.differential+=team2.P1Diff
            t2pokemon1.gp+=1
            t2pokemon1.gw+=team2.win
            t2pokemon2.kills+=team2.P2K
            t2pokemon2.deaths+=team2.P2F
            t2pokemon2.differential+=team2.P2Diff
            t2pokemon2.gp+=1
            t2pokemon2.gw+=team2.win
            t2pokemon3.kills+=team2.P3K
            t2pokemon3.deaths+=team2.P3F
            t2pokemon3.differential+=team2.P3Diff
            t2pokemon3.gp+=1
            t2pokemon3.gw+=team2.win
            t2pokemon4.kills+=team2.P4K
            t2pokemon4.deaths+=team2.P4F
            t2pokemon4.differential+=team2.P4Diff
            t2pokemon4.gp+=1
            t2pokemon4.gw+=team2.win
            t2pokemon5.kills+=team2.P5K
            t2pokemon5.deaths+=team2.P5F
            t2pokemon5.differential+=team2.P5Diff
            t2pokemon5.gp+=1
            t2pokemon5.gw+=team2.win
            t2pokemon6.kills+=team2.P6K
            t2pokemon6.deaths+=team2.P6F
            t2pokemon6.differential+=team2.P6Diff
            t2pokemon6.gp+=1
            t2pokemon6.gw+=team2.win
            #update coach1 data
            coach1team.wins+=team1.win
            coach1team.losses+=abs(team1.win-1)
            coach1team.forfeit+=team1.forfeit
            if team1.forfeit == 1:
                coach1team.differential+=(-6)
            else:
                coach1team.differential+=team1.diff
            if coach1team.streak < 0:
                if team1.win == 1:
                    coach1team.streak=1
                else:
                    coach1team.streak+=(-1)
            else:
                if team1.win == 1:
                    coach1team.streak+=1
                else:
                    coach1team.streak=(-1)
            #update coach2 data
            coach2team.wins+=team2.win
            coach2team.losses+=abs(team2.win-1)
            coach2team.forfeit+=team2.forfeit
            if team2.forfeit == 1:
                coach2team.differential+=(-6)
            else:
                coach2team.differential+=team2.diff
            if coach2team.streak < 0:
                if team2.win == 1:
                    coach2team.streak=1
                else:
                    coach2team.streak+=(-1)
            else:
                if team2.win == 1:
                    coach2team.streak+=1
                else:
                    coach2team.streak=(-1)
            #update match
            if match.team1==coach1team:
                match.team1megaevolved=team1.megaevolved
                match.team2megaevolved=team2.megaevolved
                match.team1score=team1.score
                match.team2score=team2.score
                match.team1usedz=team1.usedz
                match.team2usedz=team2.usedz
                if team1.win==1:
                    match.winner=coach1team
                elif team2.win==1:
                    match.winner=coach2team
            elif match.team1==coach2team:
                match.team1megaevolved=team2.megaevolved
                match.team2megaevolved=team1.megaevolved
                match.team1score=team2.score
                match.team2score=team1.score
                match.team1usedz=team2.usedz
                match.team2usedz=team1.usedz
                if team1.win==1:
                    match.winner=coach1team
                elif team2.win==1:
                    match.winner=coach2team
            #save models
            coach1team.save(); coach2team.save(); t1pokemon1.save(); t1pokemon2.save(); t1pokemon3.save(); t1pokemon4.save(); t1pokemon5.save(); t1pokemon6.save()
            t2pokemon1.save(); t2pokemon2.save(); t2pokemon3.save(); t2pokemon4.save(); t2pokemon5.save(); t2pokemon6.save()
            match.save()
            form.save()
            messages.success(request,'Replay has been saved!')
            discordserver=subleague.discord_settings.discordserver
            discordchannel=subleague.discord_settings.replaychannel
            title=f"Week: {match.week}. {match.team1.teamname} vs {match.team2.teamname}: {match.replay}."
            replay_announcements.objects.create(
                league = discordserver,
                league_name = subleague.league.name,
                text = title,
                replaychannel = discordchannel
            )
            matchpickems=pickems.objects.all().filter(match=match)
            for item in matchpickems:
                if item.pick==match.winner:
                    item.correct=True
                    item.save()
            return  redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
    return  redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)

@check_if_subleague
@check_if_season
@check_if_match
def league_match_results(request,league_name,subleague_name,matchid):
    league_name=league_name.replace('%20',' ')
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_teams=subleague.subleague_coachs.all().order_by('teamname')
    match=schedule.objects.get(pk=matchid)
    if match.replay == "Link":
        messages.error(request,f'A replay for that match does not exist!',extra_tags="danger")
        return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
    try:
        manualreplay=manual_replay.objects.get(match=match)
        showreplay=False
        if manualreplay.replay.find('replay.pokemonshowdown.com') >-1:
            showreplay=True
        if manualreplay.match.team1==manualreplay.winner:
            loser=manualreplay.match.team2
        if manualreplay.match.team2==manualreplay.winner:
            loser=manualreplay.match.team1
        team1score=manualreplay.match.team1score
        team2score=manualreplay.match.team2score
        score=f'{max(team1score,team2score)}-0'
        context={
            'manualreplay':manualreplay,
            'showreplay': showreplay,
            'loser': loser,
            'score': score,
            'league_teams': league_teams,
        }
        return render(request,"manualreplayresults.html",context)
    except:
        url=match.replay
        outputstring, team1, team2 = replayparse(url)
        coach1=team1.coach
        coach2=team2.coach 
        coach1alt=showdownalts.objects.all().filter(showdownalt=coach1).first()
        coach2alt=showdownalts.objects.all().filter(showdownalt=coach2).first()
        coach1team=coachdata.objects.all().filter(league_name=subleague.league).filter(Q(coach=coach1alt.user)|Q(teammate=coach1alt.user)).first()
        coach2team=coachdata.objects.all().filter(league_name=subleague.league).filter(Q(coach=coach2alt.user)|Q(teammate=coach2alt.user)).first()
        context={
            'output': outputstring,
            'team1':team1,
            'team2':team2,
            'team1name':coach1team,
            'team2name':coach2team,
            'replay': url,
            'league_name':league_name,
            'matchid':matchid,
            'showreplay': True,
            'subleague': subleague,
            'leaguepage': True,
            'league_teams': league_teams,
        }
        return render(request,"replayanalysisform.html",context)

@check_if_subleague
@check_if_season
@check_if_match
@login_required
def upload_league_replay_manual(request,league_name,subleague_name,matchid):
    league_name=league_name.replace('%20',' ')
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    season=subleague.seasonsetting
    league_teams=subleague.subleague_coachs.all().order_by('teamname')
    match=schedule.objects.get(pk=matchid)
    if match.replay != "Link":
        messages.error(request,f'A replay for that match already exists!',extra_tags="danger")
        return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
    if request.method=="POST":
        form=ManualLeagueReplayForm(match,request.POST)
        if form.is_valid():
            #get match
            match=form.cleaned_data['match']
            #get teams
            team1=match.team1
            team2=match.team2
            #get pokemon
            t1pokemon1=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t1pokemon1'])
            t1pokemon2=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t1pokemon2'])
            t1pokemon3=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t1pokemon3'])
            t1pokemon4=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t1pokemon4'])
            t1pokemon5=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t1pokemon5'])
            t1pokemon6=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t1pokemon6'])
            t2pokemon1=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t2pokemon1'])
            t2pokemon2=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t2pokemon2'])
            t2pokemon3=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t2pokemon3'])
            t2pokemon4=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t2pokemon4'])
            t2pokemon5=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t2pokemon5'])
            t2pokemon6=roster.objects.filter(season=season).get(pokemon=form.cleaned_data['t2pokemon6'])
            #update match
            match.replay=form.cleaned_data['replay']
            match.team1megaevolved=form.cleaned_data['t1megaevolved']
            match.team2megaevolved=form.cleaned_data['t2megaevolved']
            match.team1usedz=form.cleaned_data['t1usedz']
            match.team2usedz=form.cleaned_data['t2usedz']
            match.team1score=6-form.cleaned_data['t1pokemon1death']-form.cleaned_data['t1pokemon2death']-form.cleaned_data['t1pokemon3death']-form.cleaned_data['t1pokemon4death']-form.cleaned_data['t1pokemon5death']-form.cleaned_data['t1pokemon6death']
            match.team2score=6-form.cleaned_data['t2pokemon1death']-form.cleaned_data['t2pokemon2death']-form.cleaned_data['t2pokemon3death']-form.cleaned_data['t2pokemon4death']-form.cleaned_data['t2pokemon5death']-form.cleaned_data['t2pokemon6death']
            #update pokemon
            t1pokemon1.kills+=form.cleaned_data['t1pokemon1kills']
            t1pokemon2.kills+=form.cleaned_data['t1pokemon2kills']
            t1pokemon3.kills+=form.cleaned_data['t1pokemon3kills']
            t1pokemon4.kills+=form.cleaned_data['t1pokemon4kills']
            t1pokemon5.kills+=form.cleaned_data['t1pokemon5kills']
            t1pokemon6.kills+=form.cleaned_data['t1pokemon6kills']
            t2pokemon1.kills+=form.cleaned_data['t2pokemon1kills']
            t2pokemon2.kills+=form.cleaned_data['t2pokemon2kills']
            t2pokemon3.kills+=form.cleaned_data['t2pokemon3kills']
            t2pokemon4.kills+=form.cleaned_data['t2pokemon4kills']
            t2pokemon5.kills+=form.cleaned_data['t2pokemon5kills']
            t2pokemon6.kills+=form.cleaned_data['t2pokemon6kills']
            t1pokemon1.deaths+=form.cleaned_data['t1pokemon1death']
            t1pokemon2.deaths+=form.cleaned_data['t1pokemon2death']
            t1pokemon3.deaths+=form.cleaned_data['t1pokemon3death']
            t1pokemon4.deaths+=form.cleaned_data['t1pokemon4death']
            t1pokemon5.deaths+=form.cleaned_data['t1pokemon5death']
            t1pokemon6.deaths+=form.cleaned_data['t1pokemon6death']
            t2pokemon1.deaths+=form.cleaned_data['t2pokemon1death']
            t2pokemon2.deaths+=form.cleaned_data['t2pokemon2death']
            t2pokemon3.deaths+=form.cleaned_data['t2pokemon3death']
            t2pokemon4.deaths+=form.cleaned_data['t2pokemon4death']
            t2pokemon5.deaths+=form.cleaned_data['t2pokemon5death']
            t2pokemon6.deaths+=form.cleaned_data['t2pokemon6death']
            t1pokemon1.differential+=form.cleaned_data['t1pokemon1kills']-form.cleaned_data['t1pokemon1death']
            t1pokemon2.differential+=form.cleaned_data['t1pokemon2kills']-form.cleaned_data['t1pokemon2death']
            t1pokemon3.differential+=form.cleaned_data['t1pokemon3kills']-form.cleaned_data['t1pokemon3death']
            t1pokemon4.differential+=form.cleaned_data['t1pokemon4kills']-form.cleaned_data['t1pokemon4death']
            t1pokemon5.differential+=form.cleaned_data['t1pokemon5kills']-form.cleaned_data['t1pokemon5death']
            t1pokemon6.differential+=form.cleaned_data['t1pokemon6kills']-form.cleaned_data['t1pokemon6death']
            t2pokemon1.differential+=form.cleaned_data['t2pokemon1kills']-form.cleaned_data['t2pokemon1death']
            t2pokemon2.differential+=form.cleaned_data['t2pokemon2kills']-form.cleaned_data['t2pokemon2death']
            t2pokemon3.differential+=form.cleaned_data['t2pokemon3kills']-form.cleaned_data['t2pokemon3death']
            t2pokemon4.differential+=form.cleaned_data['t2pokemon4kills']-form.cleaned_data['t2pokemon4death']
            t2pokemon5.differential+=form.cleaned_data['t2pokemon5kills']-form.cleaned_data['t2pokemon5death']
            t2pokemon6.differential+=form.cleaned_data['t2pokemon6kills']-form.cleaned_data['t2pokemon6death']
            t1pokemon1.gp+=1; t1pokemon2.gp+=1; t1pokemon3.gp+=1; t1pokemon4.gp+=1; t1pokemon5.gp+=1; t1pokemon6.gp+=1
            t2pokemon1.gp+=1; t2pokemon2.gp+=1; t2pokemon3.gp+=1; t2pokemon4.gp+=1; t2pokemon5.gp+=1; t2pokemon6.gp+=1
            winner=form.cleaned_data['winner']
            match.winner=winner
            if winner == match.team1:
                team1.wins+=1; team2.losses+=1
                t1pokemon1.gw+=1; t1pokemon2.gw+=1; t1pokemon3.gw+=1; t1pokemon4.gw+=1; t1pokemon5.gw+=1; t1pokemon6.gw+=1
                if team1.streak>-1:
                    team1.streak+=1
                else:
                    team1.streak=1
                if team2.streak>-1:
                    team2.streak=(-1)
                else:
                    team2.streak+=(-1)
            elif winner == match.team2:
                team2.wins+=1; team1.losses+=1
                t2pokemon1.gw+=1; t2pokemon2.gw+=1; t2pokemon3.gw+=1; t2pokemon4.gw+=1; t2pokemon5.gw+=1; t2pokemon6.gw+=1
                if team2.streak>-1:
                    team2.streak+=1
                else:
                    team2.streak=1
                if team1.streak>-1:
                    team1.streak=(-1)
                else:
                    team1.streak+=(-1)
            if form.cleaned_data['t1forfeit']==True:
                team1.forfeit+=1
                team1.differential+=(-6)
            else:
                if match.team1score>match.team2score:
                    team1.differential+=match.team1score
                elif match.team2score>match.team1score:
                    team1.differential+=(-match.team2score)
            if form.cleaned_data['t2forfeit']==True:
                team2.forfeit+=1
                team2.differential+=(-6)
            else:
                if match.team2score>match.team1score:
                    team2.differential+=match.team2score
                elif match.team1score>match.team2score:
                    team2.differential+=(-match.team1score)
            #save data
            form.save(); match.save(); team1.save(); team2.save()
            t1pokemon1.save(); t1pokemon2.save(); t1pokemon3.save(); t1pokemon4.save(); t1pokemon5.save(); t1pokemon6.save()
            t2pokemon1.save(); t2pokemon2.save(); t2pokemon3.save(); t2pokemon4.save(); t2pokemon5.save(); t2pokemon6.save()
            messages.success(request,"Match has been saved!")
            discordserver=subleague.discord_settings.discordserver
            discordchannel=subleague.discord_settings.replaychannel
            title=f"Week: {match.week}. {match.team1.teamname} vs {match.team2.teamname}: {match.replay}."
            replay_announcements.objects.create(
                league = discordserver,
                league_name = league_name,
                text = title,
                replaychannel = discordchannel
            )
            matchpickems=pickems.objects.all().filter(match=match)
            for item in matchpickems:
                if item.pick==match.winner:
                    item.correct=True
                    item.save()
            return redirect('league_schedule',league_name=league_name,subleague_name=subleague.subleague)
    form=ManualLeagueReplayForm(match,initial={'match':match})
    context={
        'form': form,
        'manual_submission': True,
        'league_name':league_name,
        'matchid':matchid,
        'subleague': subleague,
        'leaguepage': True,
        'match': match,
        'league_teams': league_teams,
    }
    return  render(request,"replayanalysisform.html",context)
