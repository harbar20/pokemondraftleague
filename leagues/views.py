from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from datetime import datetime, timezone, timedelta
import pytz
import math
import random
from background_task import background

from .forms import *
from .models import *
from leagues.models import league_team
from pokemondatabase.models import *
from pokemonadmin.models import *
from individualleague.models import *
from accounts.models import *
from pokemondraftleague.customdecorators import check_if_subleague, check_if_league, check_if_season, check_if_team, check_if_host

@login_required
def create_league(request):
    if request.method == 'POST':
        form = CreateLeagueForm(request.POST)
        if form.is_valid():
            newleague=form.save()
            newleague.host.add(request.user)
            newleague.save()
            messages.success(request,f'Your league has been successfully created!')
            return redirect('league_list')
        else:
            print(form.errors)
    else:
        form = CreateLeagueForm(initial={'host': request.user})
    context = {
        'form': form,
    }
    return render(request, 'createleague.html',context)

def league_list(request):
    context={
        'leagueheading': 'All Leagues',
    }
    return render(request, 'leagues.html',context)

@login_required
def leagues_hosted_settings(request):
    context = {
        'settingheading': "Select League",
        'leagueshostedsettings': True,
    }
    return render(request, 'leaguelist.html',context)

@check_if_league
@check_if_host
@login_required
def individual_league_settings(request,league_name):
    print('here')
    league_instance=league.objects.get(name=league_name)
    league_settings_instance=league_settings.objects.get(league_name=league_instance)
    if request.method == 'POST':
        l_form = UpdateLeagueForm(
            request.POST,
            request.FILES,
            instance=league_instance
            )
        ls_form = UpdateLeagueSettingsForm(request.POST,instance=league_settings_instance)
        if l_form.is_valid() and ls_form.is_valid():
            l_form.save()
            ls_form.save()
            messages.success(request,league_name+' has been updated!')
            return redirect('individual_league_settings',league_name=league_name)
    else:
        l_form = UpdateLeagueForm(instance=league_instance)
        ls_form = UpdateLeagueSettingsForm(instance=league_settings_instance)
    try:
        addleagueteam=league_instance.configuration.teambased
    except:
        addleagueteam=False
    context = {
        'settingheading': league_name,
        'forms': [l_form,ls_form],
        'deletebutton': 'Delete League',
        'leagueshostedsettings': True,
        'addleagueteam': addleagueteam,
        'league_name':league_name,
    }
    return render(request, 'settings.html',context)

@check_if_league
@check_if_host
@login_required
def league_configuration_(request,league_name):
    league_instance=league.objects.get(name=league_name)
    if request.method == 'POST':
        formpurpose=request.POST['purpose']
        if formpurpose=="Submit":
            try:
                existingconfiguration=league_instance.configuration
                numsubleagues=existingconfiguration.number_of_subleagues
                form=LeagueConfigurationForm(request.POST,instance=existingconfiguration)
            except:
                form=LeagueConfigurationForm(request.POST)
                numsubleagues=None
            if form.is_valid():
                config=form.save()
                newnumsubleagues=config.number_of_subleagues
                if newnumsubleagues != numsubleagues:
                    try:
                        league_instance.subleague.all().delete()
                    except:
                        pass
                    pokemon_tier.objects.filter(league=league_instance).all().delete()
                    configureleague(config.id)
                    messages.success(request,league_name+' has been updated and is being configured! This should be quick but can take a few minutes. DO NOT TRY TO RECONFIGURE IF THERE IS AN ERROR AND CONTACT SITE ADMINISTRATION.')
        elif formpurpose=="Rename":
            itemid=request.POST['itemid']
            slname=request.POST['slname']
            print(slname)
            i=league_subleague.objects.get(id=int(itemid))
            i.subleague=slname
            i.save()
    try:
        existingconfiguration=league_instance.configuration
        form=LeagueConfigurationForm(initial={'league':league_instance},instance=existingconfiguration)
    except:
        form=LeagueConfigurationForm(initial={'league':league_instance})
    showsubleagues=False
    try:    
        subleagues=league_instance.subleague.all()
        if subleagues.count()>1:
            showsubleagues=True
    except:
        subleagues=None
    context = {
        'league_name': league_name,
        'settingheading': league_name,
        'leagueshostedsettings': True,
        'form':form,
        'subleagues':subleagues,
        'showsubleagues':showsubleagues,
    }
    return render(request, 'leagueconfiguration.html',context)

@check_if_subleague
@check_if_host
@login_required
def discordsettings(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    try:
        discordinstance=discord_settings.objects.get(subleague=subleague)
        form=DiscordSettingsForm(instance=discordinstance)
        if request.method=='POST':
            form=DiscordSettingsForm(request.POST,instance=discordinstance)
            if form.is_valid():
                form.save()
                messages.success(request,league_name+' has been updated!')
            else:
                messages.error(request,'Form invalid!')
            return redirect('manage_seasons',league_name=league_name,subleague_name=subleague_name)
    except Exception as e:
        form=DiscordSettingsForm(initial={'league':subleague.league,'subleague':subleague,})
        if request.method=='POST':
            form=DiscordSettingsForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,league_name+' has been updated!')
            else:
                messages.error(request,'Form invalid!')
            return redirect('manage_seasons',league_name=league_name,subleague_name=subleague_name)
    context = {
        'settingheading': f'{subleague} Discord Settings',
        'forms': [form],
        'leagueshostedsettings': True,
    }
    return render(request, 'formsettings.html',context)

@check_if_league
@check_if_host
@login_required
def manage_coachs(request,league_name):
    league_name=league_name.replace("_"," ")
    league_=league.objects.get(name=league_name)
    applicants=league_application.objects.filter(league_name=league_)
    totalapplicants=len(applicants)
    coachs=coachdata.objects.filter(league_name=league_).order_by('coach__username')
    spotsremaining=True
    context = {
        'applicants': applicants,
        'coachs': coachs,
        'league_name': league_name,
        'leagueshostedsettings': True,
        'totalapplicants': totalapplicants,
        'spotsremaining': spotsremaining,
        'league': league_,
    }
    return render(request, 'managecoachs.html',context)

@login_required
def applicants_summary(request,league_name):
    league_=league.objects.get(name=league_name)
    applicants=league_application.objects.filter(league_name=league_)
    leagueshostedsettings=True
    context = {
        'league_name': league_name,
        'leagueshostedsettings': leagueshostedsettings,
        'applicants': applicants,
    }
    return render(request, 'applicants_summary.html',context)

@login_required
def view_application(request,league_name):
    if request.POST:
        formpurpose=request.POST['purpose']
        if formpurpose=="View":
            application=league_application.objects.get(pk=request.POST['coach'])
            context = {
                'league_name': league_name,
                'leagueshostedsettings': True,
                "appofinterest":application,
            }
            return render(request, 'view_application.html',context)
        elif formpurpose=="Delete Application":
            league_application.objects.get(id=request.POST['appid']).delete()
            messages.success(request,'Application has been deleted!')
        elif formpurpose=="Add to Subleague":
            appofinterest=league_application.objects.get(id=request.POST['appid'])
            subleagueofinterest=league_subleague.objects.get(id=request.POST['subleagueid'])
            coachdata.objects.create(
                coach=appofinterest.applicant,
                league_name=appofinterest.league_name,
                subleague=subleagueofinterest,
                teamabbreviation=appofinterest.teamabbreviation,
                teamname=appofinterest.teamname,
                )
            appofinterest.delete()
            messages.success(request,'Coach has been added!')
    return redirect('manage_coachs',league_name=league_name)

@login_required
def remove_coach(request,league_name):
    if request.POST:
        league_=league.objects.get(name=league_name)
        try:
            seasonsetting.objects.get(league=league_)
            messages.error(request,'The season has already started!',extra_tags='danger')
            return redirect('manage_coachs',league_name=league_name)
        except:
            coachtoremove=coachdata.objects.get(pk=request.POST['coachtoupdate'])
            league_application.objects.create(applicant=coachtoremove.coach,league_name=coachtoremove.league_name)
            coachtoremove.delete()
    return redirect('manage_coachs',league_name=league_name)

@login_required
def leagues_coaching_settings(request):
    context = {
        'settingheading': "Select League",
        'leaguescoachingpage': True,
        'leaguescoachingsettings': True,
    }
    return render(request, 'leaguelist.html',context)

@login_required
def historic_teams_settings(request):
    context = {
        'settingheading': "Select League",
        'historicteamsettingspage': True,
        'historicteamsettings': True,
    }
    return render(request, 'leaguelist.html',context)

@login_required
def individual_historic_team_settings(request,teamid):
    try:
        hti=historical_team.objects.get(id=teamid)
        if request.user!=hti.coach1 and request.user!=hti.coach2:
            messages.error(request,"Only a team's coach may edit it's data!",extra_tags='danger')
            return redirect('historic_teams_settings')
    except:
        messages.error(request,'Historic team does not exist!',extra_tags='danger')
        return redirect('historic_teams_settings')
    if request.method == 'POST':
        form = UpdateHistoricTeamForm(request,request.POST,request.FILES,instance=hti)
        if form.is_valid():
            form.save()
            messages.success(request,'Your historic team info has been updated!')
            return redirect('historic_teams_settings')
    form=UpdateHistoricTeamForm(request,instance=hti)
    forms=[form]
    context = {
        'settingheading': f'{hti.teamname}',
        'forms': forms,
        'historicteamsettings': True,
    }
    return render(request, 'settings.html',context)

@login_required
def individual_league_coaching_settings(request,league_name):
    try:
        league_instance=league.objects.get(name=league_name)
        coachinstance=coachdata.objects.filter(league_name=league_instance).filter(Q(coach=request.user)|Q(teammate=request.user)).first()
        settings=league_settings.objects.get(league_name=league_instance)
        allowsteams=league_instance.configuration.allows_teams
        teambased=league_instance.configuration.teambased
    except:
        messages.error(request,'League does not exist!',extra_tags='danger')
        return redirect('leagues_hosted_settings')
    if request.method == 'POST':
        if allowsteams:
            form = UpdateCoachInfoForm(request,
                request.POST,
                request.FILES,
                instance=coachinstance
                )
            tm_form=UpdateCoachTeammateForm(request.POST,instance=coachinstance)
            if teambased:
                parent_team_form=UpdateParentTeamForm(league_instance,request.POST,instance=coachinstance)
                if form.is_valid() and tm_form.is_valid() and parent_team_form.is_valid():
                    form.save()
                    tm_form.save()
                    parent_team_form.save()
                    messages.success(request,'Your coach info has been updated!')
                    return redirect('individual_league_coaching_settings',league_name=league_name)
            else:    
                if form.is_valid() and tm_form.is_valid():
                    form.save()
                    tm_form.save()
                    messages.success(request,'Your coach info has been updated!')
                    return redirect('individual_league_coaching_settings',league_name=league_name)
        else:
            form = UpdateCoachInfoForm(request,
                request.POST,
                request.FILES,
                instance=coachinstance
                )
            if teambased:
                parent_team_form=UpdateParentTeamForm(league_instance,request.POST,instance=coachinstance)
                if form.is_valid() and parent_team_form.is_valid():
                    form.save()
                    parent_team_form.save()
                    messages.success(request,'Your coach info has been updated!')
            else:
                if form.is_valid():
                    form.save()
                    messages.success(request,'Your coach info has been updated!')
            return redirect('individual_league_coaching_settings',league_name=league_name)
    else:
        form = UpdateCoachInfoForm(request,instance=coachinstance)
        forms=[]
        forms.append(form)
        if teambased:
            parent_team_form=UpdateParentTeamForm(league_instance,instance=coachinstance)
            forms.append(parent_team_form)
        if allowsteams:
            tm_form=UpdateCoachTeammateForm(instance=coachinstance)
            forms.append(tm_form)
    context = {
        'settingheading': league_name,
        'forms': forms,
        'leaguescoachingsettings': True,
        'league_name':league_name,
    }
    return render(request, 'settings.html',context)

@check_if_subleague
@check_if_host
@login_required
def manage_seasons(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    try:
        seasonsettings=seasonsetting.objects.get(subleague=subleague)
        originalpicksperteam=seasonsettings.picksperteam
        form = EditSeasonSettingsForm(instance=seasonsettings)
        settingheading='Update Season Settings'
        create=False
        manageseason=True
    except:
        seasonsettings=None
        form = CreateSeasonSettingsForm(initial={'league': subleague.league,'subleague':subleague})
        settingheading='Create New Season'
        create=True
        manageseason=False
    if request.method == 'POST':
        try:
            seasonsettings=seasonsetting.objects.get(subleague=subleague)
            form = EditSeasonSettingsForm(request.POST,instance=seasonsettings)
            if form.is_valid():
                newpicksperteam=form.cleaned_data['picksperteam']
                leaguecoaches=coachdata.objects.all().filter(subleague=subleague)
                if originalpicksperteam<newpicksperteam:
                    coachdraft=draft.objects.all().filter(season=seasonsettings).order_by('-picknumber')[0:leaguecoaches.count()]
                    pn=coachdraft.first().picknumber+1
                    did=draft.objects.all().order_by('-id').first().id+1
                    rid=roster.objects.all().order_by('-id').first().id+1
                    for i in range(newpicksperteam-originalpicksperteam):
                        if i%2==0:
                            for item in coachdraft:
                                draft.objects.create(id=did,season=item.season,picknumber=pn,team=item.team)
                                roster.objects.create(id=did,season=item.season,team=item.team)
                                pn+=1;did+=1;rid+=1
                        else:
                            for item in coachdraft[::-1]:
                                draft.objects.create(id=did,season=item.season,picknumber=pn,team=item.team)
                                roster.objects.create(id=did,season=item.season,team=item.team)
                                pn+=1;did+=1;rid+=1
                elif originalpicksperteam>newpicksperteam:
                    for item in leaguecoaches:
                        coachdraft=item.draftpicks.all().order_by('picknumber')
                        coachroster=item.teamroster.all().order_by('id')
                        for i in range(originalpicksperteam-newpicksperteam):
                            coachdraft.last().delete()
                            coachroster.last().delete()
                form.save()
                messages.success(request,'Season settings have been updated!')
            else:
                messages.error(request,form.errors,extra_tags='danger')    
        except:   
            form = CreateSeasonSettingsForm(request.POST)
            print('here') 
            if form.is_valid():
                thisseason=form.save()
                """
                picksperteam=form.cleaned_data['picksperteam']
                rosterid=roster.objects.all().order_by('id').last().id
                for coach in currentcoaches:
                    for i in range(picksperteam):
                        rosterid+=1
                        roster.objects.create(id=rosterid,season=thisseason,team=coach)
                        """
                rule.objects.create(season=thisseason)
                messages.success(request,'Your season has been created!')
        return redirect('manage_seasons',league_name=league_name,subleague_name=subleague_name)
    context = {
        'subleague':subleague,
        'league_name': league_name,
        'leagueshostedsettings': True,
        'forms': [form],
        'seasonsettings': seasonsettings,
        'settingheading': settingheading,
        'create': create,
        'manageseason': manageseason,    
    }
    return render(request, 'settings.html',context)

#works
@check_if_subleague
@check_if_host
@login_required
def manage_tiers(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    if request.method == 'POST':
        form = CreateTierForm(request.POST)
        if form.is_valid() :
            form.save()
            messages.success(request,'Tier has been added!')
            return redirect('manage_tiers',league_name=league_name,subleague_name=subleague_name)
    else:
        form = CreateTierForm(initial={'league': subleague.league,'subleague':subleague})
    pokemontiers=pokemon_tier.objects.filter(subleague=subleague).all().order_by('pokemon__pokemon','tier')
    pokemontiers_id=list(pokemontiers.values_list('pokemon__id',flat=True))
    remainingmons=all_pokemon.objects.all().exclude(id__in=pokemontiers_id)
    leaguestiers=leaguetiers.objects.filter(subleague=subleague).all().order_by('tiername')
    bannedtier=leaguestiers.get(tiername='Banned')
    for mon in remainingmons:
        pokemon_tier.objects.create(
            id=pokemon_tier.objects.all().order_by('-id').first().id+1,
            pokemon = mon,
            league = subleague.league,
            subleague = subleague,
            tier = bannedtier
        )
    pokemontiers=pokemon_tier.objects.filter(subleague=subleague).all().order_by('pokemon__pokemon','tier')
    untiered=pokemon_tier.objects.filter(subleague=subleague,tier=None).all().order_by('pokemon__pokemon')
    context = {
        'league_name': league_name,
        'leagueshostedsettings': True,
        'pokemontiers': pokemontiers,
        'leaguetiers':leaguestiers,
        'forms': [form],
        'managetiers': True,
        'subleague':subleague,
        'untiered':untiered,
    }
    return render(request, 'managetiers.html',context)

@csrf_exempt
def update_tiering(request):
    tierid=request.POST['tierid']
    pokemonid=request.POST['pokemonid']
    newtierid=request.POST['newtierid']
    newtier=leaguetiers.objects.get(id=newtierid)
    if tierid != "Untiered":
        poi=pokemon_tier.objects.get(id=tierid)
        poi.tier=newtier
        poi.save()
    else:
        poi=pokemon_tier.objects.get(id=pokemonid)
        poi.tier=newtier
        poi.save()
    data={
        'response':'Success'
        }
    return JsonResponse(data)

#works
@login_required
def delete_tier(request,league_name,subleague_name):
    if request.POST:
        tiertodelete=leaguetiers.objects.get(pk=request.POST['tiertodelete']).delete()
    return redirect('manage_tiers',league_name=league_name,subleague_name=subleague_name)

#works
@check_if_subleague
@check_if_host
@login_required
def edit_tier(request,league_name,subleague_name,tierid):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    if request.method == 'POST':
        tierinstance=leaguetiers.objects.get(pk=tierid)
        form = UpdateTierForm(request.POST,instance=tierinstance)
        if form.is_valid() :
            form.save()
            messages.success(request,'Tier has been edited!')
            return redirect('manage_tiers',league_name=league_name,subleague_name=subleague_name)
    else:
        tierinstance=leaguetiers.objects.get(pk=tierid)
        form=UpdateTierForm(instance=tierinstance)
    pokemontiers=pokemon_tier.objects.filter(subleague=subleague).all().order_by('pokemon__pokemon','tier__tierpoints')
    leaguestiers=leaguetiers.objects.filter(subleague=subleague).all().order_by('tiername')
    context = {
        'league_name': league_name,
        'leagueshostedsettings': True,
        'pokemontiers': pokemontiers,
        'leaguetiers':leaguestiers,
        'forms': [form],
        'editingtier': True,
        'subleague':subleague,
    }
    return render(request, 'managetiers.html',context)

#works
@check_if_subleague
@check_if_host
@login_required
def update_tier(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_=subleague.league
    if request.POST:
        pokemonofinterest=all_pokemon.objects.get(pokemon=request.POST['pokemon-select'])
        pokemontoupdate=pokemon_tier.objects.filter(subleague=subleague).get(pokemon=pokemonofinterest)
        tiertoadd=leaguetiers.objects.get(pk=request.POST['tier-select'])
        pokemontoupdate.tier=tiertoadd
        pokemontoupdate.save()
        messages.success(request,'Tier has been edited!')
    return redirect('manage_tiers',league_name=league_name,subleague_name=subleague_name)

#works
@check_if_subleague
@check_if_host
@login_required
def view_tier(request,league_name,subleague_name,tier):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_=subleague.league
    if request.method == 'POST':
        form = CreateTierForm(request.POST)
        if form.is_valid() :
            form.save()
            messages.success(request,'Tier has been added!')
            return redirect('manage_tiers',league_name=league_name,subleague_name=subleague_name)
    else:
        form = CreateTierForm(initial={'league': league_,',subleague':subleague})
        pokemontiers=pokemon_tier.objects.filter(subleague=subleague).all().order_by('pokemon__pokemon','tier')
        leaguestiers=leaguetiers.objects.filter(subleague=subleague).all().order_by('tiername')
        if tier=="Untiered":
            pokemonlist=pokemon_tier.objects.filter(subleague=subleague,tier=None).all().order_by('pokemon__pokemon')
        else:
            tier=tier.replace("_"," ")
            tierofinterest=leaguetiers.objects.filter(subleague=subleague,tiername=tier).first()
            pokemonlist=pokemon_tier.objects.filter(subleague=subleague,tier=tierofinterest).all().order_by('pokemon__pokemon')
    context = {
        'league_name': league_name,
        'leagueshostedsettings': True,
        'pokemontiers': pokemontiers,
        'leaguetiers':leaguestiers,
        'forms': [form],
        'pokemonlist': pokemonlist,
        'subleague':subleague,
    }
    return render(request, 'managetiers.html',context)


@check_if_subleague
@check_if_host
@login_required
def default_tiers(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_=subleague.league
    if request.method == 'POST':
        purpose=request.POST['purposeid']
        if purpose=='Select':
            templatetierset=leaguetiertemplate.objects.all().filter(template=request.POST['template-select']).exclude(tiername="Banned")
            leaguetiers.objects.all().filter(subleague=subleague).exclude(tiername="Banned").delete()
            for item in templatetierset:
                leaguetiers.objects.create(league=league_,subleague=subleague,tiername=item.tiername,tierpoints=item.tierpoints)
            templatepokemonset=pokemon_tier_template.objects.all().filter(template=request.POST['template-select'])
            existingpokemontiers=pokemon_tier.objects.all().filter(league=league_,subleague=subleague).exclude(tier__tiername="Banned").delete()
            thisleaguetiers=leaguetiers.objects.all().filter(subleague=subleague)
            for item in templatepokemonset:
                tiertouse=thisleaguetiers.get(tiername=item.tier.tiername)
                id_=pokemon_tier.objects.all().order_by("-id").first().id+1
                try:
                    pokemon_tier.objects.create(id=id_,pokemon=item.pokemon,league=subleague.league,subleague=subleague,tier=tiertouse)
                except:
                    pass
            messages.success(request,'The template has been applied!')
        elif purpose=="Use":
            #delete existing
            subleague.subleaguetiers.all().exclude(tiername="Banned").delete()
            #add new
            leagueofinterest=league_subleague.objects.get(id=request.POST['leagueid'])
            leagueofinteresttiers=leagueofinterest.subleaguetiers.all().exclude(tiername="Banned")
            for item in leagueofinteresttiers:
                leaguetiers.objects.create(league=league_,subleague=subleague,tiername=item.tiername,tierpoints=item.tierpoints)
            ##update pokemon
            leagueofinteresttiering=leagueofinterest.subleaguepokemontiers.all()
            existingpokemontiers=pokemon_tier.objects.all().filter(subleague=subleague).exclude(tier__tiername="Banned").delete()
            thisleaguetiers=leaguetiers.objects.all().filter(subleague=subleague)
            for item in leagueofinteresttiering:
                tiertouse=thisleaguetiers.get(tiername=item.tier.tiername)
                id_=pokemon_tier.objects.all().order_by("-id").first().id+1
                try:
                    pokemon_tier.objects.create(id=id_,pokemon=item.pokemon,league=subleague.league,subleague=subleague,tier=tiertouse)
                except:
                    pass
        return redirect('manage_tiers',league_name=league_name,subleague_name=subleague_name)
    pokemonlist=pokemon_tier.objects.filter(subleague=subleague,tier=None).all().order_by('pokemon__pokemon')
    pokemontiers=pokemon_tier.objects.filter(subleague=subleague).all().order_by('pokemon__pokemon','tier')
    leaguestiers=leaguetiers.objects.filter(subleague=subleague).all().order_by('tiername')
    availabletemplates=leaguetiertemplate.objects.all().distinct('template')
    form = CreateTierForm(initial={'league': league_,'subleague': subleague})
    context = {
        'league_name': league_name,
        'leagueshostedsettings': True,
        'pokemontiers': pokemontiers,
        'leaguetiers':leaguestiers,
        'forms': [form],
        'pokemonlist': pokemonlist,
        'defaulttemplate': True,
        'availabletemplates': availabletemplates,
        'subleague':subleague,
    }
    return render(request, 'managetiers.html',context)

@check_if_subleague
@check_if_season
@check_if_host
@login_required
def set_draft_order(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_=subleague.league
    leaguesettings=league_settings.objects.get(league_name=league_)
    currentcoaches=coachdata.objects.filter(subleague=subleague).order_by('teamname')
    currentcoachescount=len(currentcoaches)
    seasonsettings=seasonsetting.objects.filter(subleague__league__name=league_name).get(subleague__subleague=subleague_name)
    needednumberofcoaches=seasonsettings.number_of_teams
    draftstyle=seasonsettings.drafttype  
    if request.method == 'POST':
        formpurpose=request.POST['formpurpose']
        if formpurpose=='Set':
            currentdraft=draft.objects.all().filter(season=seasonsettings).delete()
            currentroster=roster.objects.all().filter(season=seasonsettings).delete()
            if draftstyle=="Snake":
                order=[]
                j=1
                for i in range(needednumberofcoaches):
                    order.append(coachdata.objects.filter(teamname=request.POST[str(i+1)],subleague=subleague).first())
                flippedorder=order[::-1]
                numberofpicks=seasonsettings.picksperteam
                id_=roster.objects.all().order_by('-id').first().id
                id__=draft.objects.all().order_by('-id').first().id
                for i in range(numberofpicks):
                    if i%2 == 0:
                        for item in order:
                            id_+=1
                            id__+=1
                            draft.objects.create(id=id__,season=seasonsettings,team=item,picknumber=j)
                            roster.objects.create(id=id_,season=seasonsettings,team=item)
                            j+=1
                    else:    
                        for item in flippedorder:
                            id_+=1
                            id__+=1
                            draft.objects.create(id=id__,season=seasonsettings,team=item,picknumber=j)
                            roster.objects.create(id=id_,season=seasonsettings,team=item)   
                            j+=1         
        elif formpurpose=='Randomize':
            currentdraft=draft.objects.all().filter(season=seasonsettings).delete()
            currentroster=roster.objects.all().filter(season=seasonsettings).delete()
            coachstoadd=coachdata.objects.all().filter(subleague=subleague)
            order=[]
            j=1
            for item in coachstoadd:
                order.append(item)
            random.shuffle(order)
            flippedorder=order[::-1]
            numberofpicks=seasonsettings.picksperteam
            id_=roster.objects.all().order_by('id').last().id
            id__=draft.objects.all().order_by('-id').first().id
            for i in range(numberofpicks):
                if i%2 == 0:
                    for item in order:
                        id_+=1
                        id__+=1
                        draft.objects.create(id=id__,season=seasonsettings,team=item,picknumber=j)
                        roster.objects.create(id=id_,season=seasonsettings,team=item)
                        j+=1
                else:    
                    for item in flippedorder:
                        id_+=1
                        id__+=1
                        draft.objects.create(id=id__,season=seasonsettings,team=item,picknumber=j)
                        roster.objects.create(id=id_,season=seasonsettings,team=item)
                        j+=1
        messages.success(request,'Draft order has been set!')
        return redirect('individual_league_settings',league_name=league_name)        
    context = {
        'league_name': league_name,
        'leagueshostedsettings': True,
        'settingheading': 'Set Draft Order',
        'currentcoaches': currentcoaches,
        'subleague':subleague,
    }
    return render(request, 'draftorder.html',context)

@check_if_subleague
@check_if_host
@login_required
def add_conference_and_division_names(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_=subleague.league
    leaguesettings=seasonsetting.objects.get(subleague=subleague)
    currentconferences = conference_name.objects.all().filter(subleague=subleague)
    currentdivisions = division_name.objects.all().filter(subleague=subleague)
    totalconferences=leaguesettings.number_of_conferences
    totaldivisions=leaguesettings.number_of_divisions
    neededconferences=totalconferences-currentconferences.count()
    neededdivisions=totaldivisions-currentdivisions.count()
    if int(totalconferences/totaldivisions)==1:
        neededdivisions=0 
    if request.method == 'POST':
        name=request.POST['itemname']
        category=request.POST['category']
        if category=='conference':
            conference_name.objects.create(league=league_,subleague=subleague,name=name)
        elif category=='division':
            associatedconference=conference_name.objects.all().filter(subleague=subleague).get(name=request.POST['divisionconference'])
            division_name.objects.create(league=league_,subleague=subleague,name=name,associatedconference=associatedconference)
        messages.success(request,f'{name} has been added as a {category}!')
        return redirect('add_conference_and_division_names',league_name=league_name,subleague_name=subleague_name)        
    context = {
        'league_name': league_name,
        'leagueshostedsettings': True,
        'currentconferences': currentconferences,
        'currentdivisions': currentdivisions,
        'neededconferences': neededconferences,
        'neededdivisions': neededdivisions,
        'subleague':subleague,
    }
    return render(request, 'addconferencesanddivisions.html',context)

@login_required
def delete_conference(request,league_name,subleague_name):
    if request.method=="POST":
        itemid=request.POST['itemid']
        itemtodelete=conference_name.objects.get(pk=itemid)
        itemtodelete.delete()
        messages.success(request,'Conference has been deleted!')
    return redirect('add_conference_and_division_names',league_name=league_name,subleague_name=subleague_name)        

@login_required
def delete_division(request,league_name,subleague_name):
    if request.method=="POST":
        itemid=request.POST['itemid']
        itemtodelete=division_name.objects.get(pk=itemid)
        itemtodelete.delete()
        messages.success(request,'Division has been deleted!')
    return redirect('add_conference_and_division_names',league_name=league_name,subleague_name=subleague_name)        

@check_if_league
@check_if_host
@login_required
def manage_coach(request,league_name,coachofinterest):
    league_name=league_name.replace("_"," ")
    league_=league.objects.get(name=league_name.replace("_"," "))
    try:
        coachofinterest=coachdata.objects.filter(league_name=league_).get(coach__username=coachofinterest)
    except:
        messages.error(request,'Coach does not exist!',extra_tags='danger')
        league_name=league_name.replace(" ","_")
        return redirect('manage_coachs', league_name=league_name)
    form=ManageCoachForm(league_,coachofinterest.subleague,instance=coachofinterest)
    try:
        season=seasonsetting.objects.get(league=league_)
        seasonnotinsession=False
    except:
        seasonnotinsession=True
    context = {
        'league_name': league_name,
        'leagueshostedsettings': True,
        'coachofinterest':coachofinterest,
    } 
    if request.method == 'POST':
        formtype=request.POST['formtype']
        coachtoupdate=coachdata.objects.get(id=request.POST['coachtoupdate'])
        print(coachtoupdate)
        if formtype=="Update":
            form=ManageCoachForm(league_,coachtoupdate.subleague,request.POST,request.FILES,instance=coachtoupdate)
            if form.is_valid():
                form.save()
                messages.success(request,f'{coachofinterest.coach.username} has been updated!')
                return redirect('manage_coach', league_name=league_name,coachofinterest=coachofinterest.coach.username)
        elif formtype=="Adjust Draft":
            context.update({
                'coachtoupdate':coachtoupdate,
                'adjustdraft': True,
                })
            return render(request, 'managecoach.html',context)
        elif formtype=="Adjust Roster":
            context.update({
                'coachtoupdate':coachtoupdate,
                'adjustroster': True,
                })
            return render(request, 'managecoach.html',context)
        elif formtype=="Update Draft":
            pokemontoupdate=draft.objects.get(id=request.POST['pokemontoupdate'])
            try:
                pokemontoupdateto=all_pokemon.objects.get(pokemon=request.POST['pokemontoupdateto'])
                pokemontoupdate.pokemon=pokemontoupdateto
                pokemontoupdate.save()
                messages.success(request,"Draft has been updated")
            except Exception as e:
                messages.error(request,"Pokemon doesn't exist",extra_tags="danger")
            return redirect('manage_coach', league_name=league_name,coachofinterest=coachofinterest.coach.username)
        elif formtype=="Update Roster":
            pokemontoupdate=roster.objects.get(id=request.POST['pokemontoupdate'])
            try:
                pokemontoupdateto=all_pokemon.objects.get(pokemon=request.POST['pokemontoupdateto'])
                pokemontoupdate.pokemon=pokemontoupdateto
                pokemontoupdate.save()
                messages.success(request,"Roster has been updated")
            except Exception as e:
                messages.error(request,"Pokemon doesn't exist",extra_tags="danger")
            return redirect('manage_coach', league_name=league_name,coachofinterest=coachofinterest.coach.username)
        elif formtype=="Adjust Record":
            context.update({
                'form': UpdateCoachRecordForm(instance=coachtoupdate),
                'coachtoupdate':coachtoupdate,
                'adjustrecord': True,
                })
            return render(request, 'managecoach.html',context)
        elif formtype=="updatecoachdata":
            form=UpdateCoachRecordForm(request.POST,instance=coachtoupdate)
            if form.is_valid():
                form.save()
                messages.success(request,f'{coachtoupdate.coach.username} has been updated!')
                return redirect('manage_coachs', league_name=league_name)
            return redirect('manage_coach', league_name=league_name,coachofinterest=coachofinterest.coach.username)
        elif formtype=="Add Showdown Alt":
            alts=showdownalts.objects.all().filter(user=coachtoupdate.coach)
            context.update({
                'alts':alts,
                'coachtoupdate':coachtoupdate,
                'addalt': True,
                })
            return render(request, 'managecoach.html',context)
        elif formtype=="addalt":
            showdownalts.objects.create(user=coachtoupdate.coach,showdownalt=request.POST['givenalt'])
            messages.success(request,f'{coachtoupdate.coach} has been updated!')
            return redirect('manage_coach', league_name=league_name,coachofinterest=coachofinterest.coach.username)     
    context.update({
        'form':form,
        'coachform':True,
        'seasonnotinsession': seasonnotinsession,
    })
    return render(request, 'managecoach.html',context)

@check_if_league
@login_required
def designate_z_users(request,league_name):
    league_instance=league.objects.get(name=league_name)
    coachinstance=coachdata.objects.filter(league_name=league_instance).filter(Q(coach=request.user)|Q(teammate=request.user)).first()
    settings=league_settings.objects.get(league_name=league_instance)
    season=coachinstance.subleague.seasonsetting
    if request.method == 'POST':
        form=DesignateZUserForm(season,coachinstance,request.POST)
        if form.is_valid():
            zuser=form.cleaned_data['zuser']
            ztype=form.cleaned_data['zmovetype']
            zuser.zuser=ztype
            zuser.save()
            messages.success(request,f'{zuser.pokemon.pokemon} has been added as a Z user!')
        return redirect('designate_z_users',league_name=league_name)
    else:
        numberofz=season.numzusers
        currentz=roster.objects.all().filter(season=season,team=coachinstance).exclude(zuser="N")
        zneeded=numberofz-currentz.count()
        forms=[]
        forms.append(DesignateZUserForm(season,coachinstance))
    context = {
        'settingheading': f'{league_name}: Designate Z Users',
        'leaguescoachingsettings': True,
        'league_name':league_name,
        'forms': forms,
        'zneeded':zneeded,
        'currentz': currentz,
        'candeletez': season.candeletez,
    }
    return render(request, 'designatezusers.html',context)

@check_if_league
@login_required
def delete_z_user(request,league_name):
    try:
        league_instance=league.objects.get(name=league_name)
        coachinstance=coachdata.objects.filter(league_name=league_instance).filter(Q(coach=request.user)|Q(teammate=request.user)).first()
        settings=league_settings.objects.get(league_name=league_instance)
    except:
        messages.error(request,'League does not exist!',extra_tags='danger')
        return redirect('leagues_coaching_settings')
    try:
        season=coachinstance.subleague.seasonsetting
    except:
        messages.error(request,'Season does not exist!',extra_tags='danger')
        return redirect('leagues_coaching_settings')
    if request.method == 'POST':
        
        zuser=roster.objects.get(pk=request.POST['zid'])
        zuser.zuser="N"
        zuser.save()
        messages.success(request,f'{zuser.pokemon.pokemon} has been removed as a Z user!')
    print("here")
    return redirect('designate_z_users',league_name=league_name)

@login_required
def add_team_of_coachs(request,league_name):
    try:
        league_instance=league.objects.get(name=league_name)
        coachinstance=coachdata.objects.filter(league_name=league_instance).filter(Q(coach=request.user)|Q(teammate=request.user)).first()
        settings=league_settings.objects.get(league_name=league_instance)
    except:
        messages.error(request,'League does not exist!',extra_tags='danger')
        return redirect('leagues_coaching_settings')
    heading='Add Team of Coaches'
    if request.method == 'POST':
        purpose=request.POST['purpose']
        if purpose == 'Submit':
            form=AddTeamOfCoachsForm(request.POST,request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request,f'Team has been added!')
        elif purpose == 'Delete':
            teamtodelete=league_team.objects.get(id=request.POST['deleteid'])
            teamtodelete.delete()
        elif purpose == 'Edit':
            team_instance=league_team.objects.get(id=request.POST['editid'])
            editid=team_instance.id
            form=AddTeamOfCoachsForm(instance=team_instance)
            allteams=league_team.objects.all().filter(league=league_instance)
            heading='Edit Team of Coaches'
            context = {
                'leagueshostedsettings': True,
                'league_name':league_name,
                'form': form,
                'allteams': allteams,
                'heading':heading,
                'updateteam': True,
                'editid': editid,
            }
            return render(request, 'addteamofcoachs.html',context)
        elif purpose == 'Update':
            team_instance=league_team.objects.get(id=request.POST['editid'])
            form=AddTeamOfCoachsForm(request.POST,request.FILES,instance=team_instance)
            if form.is_valid():
                form.save()
                messages.success(request,f'Team has been updated!')
    form=AddTeamOfCoachsForm(initial={'league':league_instance})
    allteams=league_team.objects.all().filter(league=league_instance)
    context = {
        'leagueshostedsettings': True,
        'league_name':league_name,
        'form': form,
        'heading':heading,
        'allteams': allteams,
    }
    return render(request, 'addteamofcoachs.html',context)

@check_if_league
@check_if_host
@login_required
def archive_season(request,league_name):
    league_=league.objects.get(name=league_name)
    unplayedgames=schedule.objects.all().filter(replay="Link",season__league=league_).count()
    if unplayedgames>0:
        messages.error(request,'You cannot archive a season with matches remaining to be played!',extra_tags='danger')
        return redirect('leagues_hosted_settings')
    try:
        archiveseason(league_name)
        messages.success(request,'The site is currently archiving your season. This can take several minutes. If there are issues, contact site administration and DO NOT TRY ARCHIVING AGAIN.')
    except Exception as e: 
        print(e)
        messages.error(request,'There was an error archiving your season. Contact site administration for help.',extra_tags='danger')
    return redirect('leagues_hosted_settings')

@login_required
@check_if_subleague
@check_if_season
@check_if_host
def createroundrobinschedule(request,league_name,subleague_name):
    league_name=league_name.replace('%20',' ')
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    season=subleague.seasonsetting
    league_teams=subleague.subleague_coachs.all().order_by('teamname')
    leaguesettings=seasonsetting.objects.get(subleague=subleague)
    needednumberofcoaches=leaguesettings.number_of_teams
    currentcoaches=coachdata.objects.filter(league_name=subleague.league)
    currentcoachescount=len(currentcoaches)
    existingmatches=schedule.objects.all().filter(season=leaguesettings).exclude(replay='Link')
    if existingmatches.count()>0:
        messages.error(request,'Matches already exist!',extra_tags='danger')
        return redirect('manage_seasons',league_name=league_name,subleague_name=subleague_name)
    schedule.objects.all().filter(season=leaguesettings).delete()
    #get conferences
    conferences=conference_name.objects.all().filter(subleague=subleague)
    conference_rosters=[]
    for c in conferences:
        coachs=coachdata.objects.all().filter(conference=c)
        conference_rosters.append(coachs)
    #create matches
    interconfteams=[]
    for conference in conference_rosters:
        conference=list(conference)
        if len(conference) % 2:
            conference.append(None)
        count=len(conference)
        sets=count-1
        interconf=[]
        for week in range(sets):
            for i in range(int(count/2)):
                if conference[i]!=None and conference[count-i-1]!=None:
                    schedule.objects.create(season=leaguesettings,week=str(week+1),team1=conference[i],team2=conference[count-i-1])
                elif conference[i]==None:
                    interconf.append(conference[count-i-1])
                elif conference[count-i-1]==None:
                    interconf.append(conference[i])
            conference.insert(1, conference.pop())
        interconfteams.append(interconf)
    for i in range(len(interconfteams[0])):
        schedule.objects.create(season=leaguesettings,week=str(i+1),team1=interconfteams[0][i],team2=interconfteams[1][i])
    return redirect('manage_seasons',league_name=league_name,subleague_name=subleague_name)

@login_required
@check_if_subleague
@check_if_season
@check_if_host
def create_match(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_teams=subleague.subleague_coachs.all().order_by('teamname')
    seasonsettings=subleague.seasonsetting
    leaguesettings=league_settings.objects.get(league_name=subleague.league)
    currentcoaches=coachdata.objects.filter(league_name=subleague.league)
    form = CreateMatchForm(seasonsettings,subleague,initial={'season':seasonsettings})
    settingheading='Create New Match'
    edit=False
    matchid=None
    if request.method == 'POST':  
        formpurpose=request.POST['formpurpose']
        if formpurpose=="Create":
            form = CreateMatchForm(seasonsettings,subleague,request.POST)
            if form.is_valid() :
                ioi=form.save()
                try:
                    moi=schedule.objects.filter(season=ioi.season,week=ioi.week,duedate__isnull=False).first()
                    ioi.duedate=moi.duedate
                    ioi.save()
                except:
                    pass
                messages.success(request,'That match has been added!')
            return redirect('create_match',league_name=league_name,subleague_name=subleague_name)
        elif formpurpose=="Submit":
            matchofinterest=schedule.objects.get(id=request.POST['matchid'])
            form = CreateMatchForm(seasonsettings,subleague,request.POST,instance=matchofinterest)
            if form.is_valid() :
                ioi=form.save()
                try:
                    moi=schedule.objects.filter(season=ioi.season,week=ioi.week,duedate__isnull=False).first()
                    ioi.duedate=moi.duedate
                    ioi.save()
                except:
                    pass
                messages.success(request,'That match has been added!')
            else:
                print(form.errors)
            return redirect('create_match',league_name=league_name,subleague_name=subleague_name)
        elif formpurpose=="Edit":
            matchofinterest=schedule.objects.get(id=request.POST['matchid'])
            form = CreateMatchForm(seasonsettings,subleague,instance=matchofinterest)
            settingheading='Edit Match'
            matchid=matchofinterest.id
            edit=True
        elif formpurpose=="Delete":
            schedule.objects.get(id=request.POST['matchid']).delete()
            messages.success(request,'That match has been deleted!')
            return redirect('create_match',league_name=league_name,subleague_name=subleague_name)
    create=True
    manageseason=False
    existingmatches=schedule.objects.all().filter(season=seasonsettings).order_by('week','id')
    context = {
        'subleague':subleague,
        'league_name': league_name,
        'leagueshostedsettings': True,
        'league_teams': league_teams,
        'forms': [form],
        'seasonsettings': seasonsettings,
        'settingheading': settingheading,
        'create': create,
        'edit':edit,
        'matchid':matchid,
        'manageseason': manageseason,
        'existingmatches':existingmatches,
    }
    return render(request, 'creatematch.html',context)


@login_required
@check_if_subleague
@check_if_season
@check_if_host
def set_match_due_dates(request,league_name,subleague_name):
    subleague=league_subleague.objects.filter(league__name=league_name).get(subleague=subleague_name)
    league_teams=subleague.subleague_coachs.all().order_by('teamname')
    season=subleague.seasonsetting
    matchs=season.schedule.all().order_by('week','duedate').distinct('week')
    if request.method == 'POST':  
        matchid=request.POST['matchid']
        duedate=request.POST['duedate']
        moi=schedule.objects.get(id=matchid)
        relatedmatches=schedule.objects.all().filter(week=moi.week,season=moi.season)
        for match in relatedmatches:
            match.duedate=duedate
            match.save()
    context = {
        'subleague':subleague,
        'league_name': league_name,
        'leagueshostedsettings': True,
        'league_teams': league_teams,
        'matchs':matchs,
    }
    return render(request, 'matchduedate.html',context)

##--------------------------------------------TASKS--------------------------------------------
@background(schedule=1)
def configureleague(configid):
    config=league_configuration.objects.get(id=configid)
    league_instance=config.league
    if config.number_of_subleagues==1:
        sl=league_subleague.objects.create(league=league_instance,subleague="Main")
        allpokes=all_pokemon.objects.all()
        i=pokemon_tier.objects.all().order_by('id').last().id
        bannedtier=leaguetiers.objects.create(league=league_instance,subleague=sl,tiername="Banned",tierpoints=1000)
        for item in allpokes:
            i+=1
            pokemon_tier.objects.create(id=i,pokemon=item,league=league_instance,subleague=sl,tier=bannedtier)
    elif config.number_of_subleagues>1:
        for i in range(config.number_of_subleagues):
            sl=league_subleague.objects.create(league=league_instance,subleague=f"Subleague{i+1}")
            allpokes=all_pokemon.objects.all()
            i=pokemon_tier.objects.all().order_by('id').last().id
            bannedtier=leaguetiers.objects.create(league=league_instance,subleague=sl,tiername="Banned",tierpoints=1000)
            for item in allpokes:
                i+=1
                pokemon_tier.objects.create(id=i,pokemon=item,league=league_instance,subleague=sl,tier=bannedtier)

@background(schedule=1)
def archiveseason(league_name):
    league_=league.objects.get(name=league_name)
    coachdataitems=coachdata.objects.all().filter(league_name=league_)
    rosteritems=roster.objects.all().filter(season__league=league_)
    draftitems=draft.objects.all().filter(season__league=league_)
    scheduleitems=schedule.objects.all().filter(season__league=league_)
    freeagencyitems=free_agency.objects.all().filter(season__league=league_)
    tradingitems=trading.objects.all().filter(season__league=league_)
    season=league_.subleague.first().seasonsetting
    maxid=historical_team.objects.all().order_by('-id').first().id
    for item in coachdataitems:
        maxid+=1
        if item.teammate:
            ht=historical_team.objects.create(
                id=maxid,
                league = item.league_name,
                seasonname = season.seasonname,
                subseason= item.subleague.subleague.replace("_"," "),
                teamname = item.teamname,
                coach1= item.coach,
                coach1username=item.coach.username,
                coach2=item.teammate,
                coach2username=item.teammate.username,
                logo = item.logo,
                wins=item.wins,
                losses=item.losses,
                differential=item.differential,
                forfeit=item.forfeit,
                support=item.support,
                damagedone=item.damagedone,
                hphealed=item.hphealed,
                luck=item.luck,
                remaininghealth=item.remaininghealth
            )
        else:
            ht=historical_team.objects.create(
                id=maxid,
                league = item.league_name,
                seasonname = season.seasonname,
                subseason= item.subleague.subleague.replace("_"," "),
                teamname = item.teamname,
                coach1= item.coach,
                coach1username=item.coach.username,
                logo = item.logo,
                wins=item.wins,
                losses=item.losses,
                differential=item.differential,
                forfeit=item.forfeit,
                support=item.support,
                damagedone=item.damagedone,
                hphealed=item.hphealed,
                luck=item.luck,
                remaininghealth=item.remaininghealth
            )
        if item.parent_team:
            ht.subteam=item.parent_team.name
            ht.save()       
    maxid=historical_freeagency.objects.all().order_by('-id').first().id
    for item in freeagencyitems:
        team=historical_team.objects.filter(league=league_,seasonname = season.seasonname)
        team=team.get(coach1=item.coach.coach)
        maxid+=1
        historical_freeagency.objects.create(id=maxid,team=team,addedpokemon=item.addedpokemon,droppedpokemon=item.droppedpokemon)
        item.delete()
    maxid=historical_trading.objects.all().order_by('-id').first().id
    for item in tradingitems:
        team=historical_team.objects.filter(league=league_,seasonname = season.seasonname).get(coach1=item.coach.coach)
        maxid+=1
        historical_trading.objects.create(id=maxid,team=team,addedpokemon=item.addedpokemon,droppedpokemon=item.droppedpokemon)
        item.delete()
    maxid=historical_draft.objects.all().order_by('-id').first().id
    for item in draftitems:
        team=historical_team.objects.filter(league=league_,seasonname = season.seasonname).get(coach1=item.team.coach)
        maxid+=1
        historical_draft.objects.create(id=maxid,team=team,pokemon=item.pokemon,picknumber=item.picknumber)
        item.delete()
    maxid=historical_roster.objects.all().order_by('-id').first().id
    for item in rosteritems:
        team=historical_team.objects.filter(league=league_,seasonname = season.seasonname).get(coach1=item.team.coach)
        maxid+=1
        historical_roster.objects.create(id=maxid,team=team,pokemon=item.pokemon,kills=item.kills,deaths=item.deaths,differential=item.differential,gp=item.gp,gw=item.gw,support=item.support,damagedone=item.damagedone,hphealed=item.hphealed,luck=item.luck,remaininghealth=item.remaininghealth)
        item.delete()
    maxid=historical_match.objects.all().order_by('-id').first().id
    for item in scheduleitems:
        maxid+=1
        team1=historical_team.objects.filter(league=league_,seasonname = season.seasonname).get(coach1=item.team1.coach)
        team2=historical_team.objects.filter(league=league_,seasonname = season.seasonname).get(coach1=item.team2.coach)
        if item.team1==item.winner:
            winner=team1
        elif item.team2==item.winner:
            winner=team2
        else:
            winner=None
        histmatch=historical_match.objects.create(
            id=maxid,
            week=item.week,
            team1=team1,
            team1alternateattribution=item.team1alternateattribution,
            team2=team2,
            team2alternateattribution=item.team2alternateattribution,
            winner = winner,
            winneralternateattribution=item.winneralternateattribution,
            team1score = item.team1score,
            team2score = item.team2score,
            replay = item.replay,
        )
        try: 
            mr=item.match_replay
            historical_match_replay.objects.create(match=histmatch,data=mr.data)
        except:
            try:
                manualmr=item.manual_replay
                historic_manual_replay.objects.create(
                    match=histmatch,
                    t1pokemon1=manualmr.t1pokemon1,
                    t1pokemon2=manualmr.t1pokemon2,
                    t1pokemon3=manualmr.t1pokemon3,
                    t1pokemon4=manualmr.t1pokemon4,
                    t1pokemon5=manualmr.t1pokemon5,
                    t1pokemon6=manualmr.t1pokemon5,
                    t2pokemon1=manualmr.t2pokemon1,
                    t2pokemon2=manualmr.t2pokemon2,
                    t2pokemon3=manualmr.t2pokemon3,
                    t2pokemon4=manualmr.t2pokemon4,
                    t2pokemon5=manualmr.t2pokemon5,
                    t2pokemon6=manualmr.t2pokemon6,
                    t1pokemon1kills=manualmr.t1pokemon1kills,
                    t1pokemon2kills=manualmr.t1pokemon2kills,
                    t1pokemon3kills=manualmr.t1pokemon3kills,
                    t1pokemon4kills=manualmr.t1pokemon4kills,
                    t1pokemon5kills=manualmr.t1pokemon5kills,
                    t1pokemon6kills=manualmr.t1pokemon6kills,
                    t2pokemon1kills=manualmr.t2pokemon1kills,
                    t2pokemon2kills=manualmr.t2pokemon2kills,
                    t2pokemon3kills=manualmr.t2pokemon3kills,
                    t2pokemon4kills=manualmr.t2pokemon4kills,
                    t2pokemon5kills=manualmr.t2pokemon5kills,
                    t2pokemon6kills=manualmr.t2pokemon6kills,
                    t1pokemon1death=manualmr.t1pokemon1death,
                    t1pokemon2death=manualmr.t1pokemon2death,
                    t1pokemon3death=manualmr.t1pokemon3death,
                    t1pokemon4death=manualmr.t1pokemon4death,
                    t1pokemon5death=manualmr.t1pokemon5death,
                    t1pokemon6death=manualmr.t1pokemon6death,
                    t2pokemon1death=manualmr.t2pokemon1death,
                    t2pokemon2death=manualmr.t2pokemon2death,
                    t2pokemon3death=manualmr.t2pokemon3death,
                    t2pokemon4death=manualmr.t2pokemon4death,
                    t2pokemon5death=manualmr.t2pokemon5death,
                    t2pokemon6death=manualmr.t2pokemon6death,
                )
            except: 
                pass
        item.delete()   
    coachdataitems.delete()
    seasonsetting.objects.filter(league=league_).delete()