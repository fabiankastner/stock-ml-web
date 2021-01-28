from django.template import loader
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

import random
from operator import itemgetter

import numpy as np
import pandas as pd
import plotly.express as px
from plotly.offline import plot

from common.util import utils
from common.util import plots
from .forms import SymbolForm, LoginForm


def index(request):
    if request.user.is_authenticated:
        return redirect('/dashboard/')
    else:
        return redirect('/login/')


def login(request):
    context = {}

    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                django_login(request, user)
                messages.success(request, "Successfully logged in" )
                return redirect('/dashboard/')
            else:
                messages.error(request, "Wrong username and or password" )
                return redirect('/login/')

    template = loader.get_template('visualizer/login.html')
    return HttpResponse(template.render(context, request))


def logout(request):
    django_logout(request)
    return redirect('/login/')



def dashboard(request):
    template = loader.get_template('visualizer/dashboard.html')

    config = utils.get_config()
    
    histogram_div = plots.get_hist()
    line_chart_div = plots.get_line_chart("abnb")

    # stock_trends_positive = sorted([{"symbol": symbol, "trend": round(np.random.normal(0, 2) + 5, 2)} for symbol in random.sample(utils.get_symbols(), 3)], key=itemgetter("trend"), reverse=True)
    # stock_trends_positive = [{"symbol": stock_trend_positive["symbol"], "trend_bin": True, "trend": "+{}%".format(stock_trend_positive["trend"])} for stock_trend_positive in stock_trends_positive]
    
    # stock_trends_negative = sorted([{"symbol": symbol, "trend": round(np.random.normal(0, 2) - 5, 2)} for symbol in random.sample(utils.get_symbols(), 3)], key=itemgetter("trend"), reverse=True)
    # stock_trends_negative = [{"symbol": stock_trend_negative["symbol"], "trend_bin": False, "trend": "{}%".format(stock_trend_negative["trend"])} for stock_trend_negative in stock_trends_negative]
    
    # stocks = len(utils.get_symbols())

    context = {
        "stocks": None, 
        "histogram_div": histogram_div,
        "average_prediction": None,
        "stocks_predicted": None,
        "stocks_predicted_value": 0,
        "line_chart_div": None,
        "line_chart_symbol": None,
        "stock_trends_positive": None,
        "stock_trends_negative": None,
        "stock_list_verbose": None,
        "stock_list_date_updated": None 
    }
    
    # config["stock_list"]["verbose"].split(' ')[0]
    # config["stock_list"]["date_updated"]

    if request.method == 'POST':
        if 'submit-symbol-search' in request.POST:
            symbol_form = SymbolForm(request.POST)
            if symbol_form.is_valid():
                return HttpResponseRedirect('{0}/'.format(symbol_form.cleaned_data['symbol']))

    return HttpResponse(template.render(context, request))


def dashboard_symbol(request, symbol):

    fig = utils.get_line_fig_from_symbol(symbol)
    line_chart_div = plot(fig, output_type='div', config=dict(displayModeBar=False))

    template = loader.get_template('visualizer/dashboard_symbol.html')

    symbol_info = utils.get_symbol_information(symbol)

    context = {
        'symbol': symbol,
        'symbol_verbose': symbol_info["Security Name"],
        'line_chart_div': line_chart_div
    }
    
    return HttpResponse(template.render(context, request))
