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
    config = utils.get_config()

    template = loader.get_template('visualizer/dashboard.html')
    
    df = pd.DataFrame({'predictions': np.random.normal(0, 0.3, 50).tolist()})
  
    # get overall prediction histogram
    fig = px.histogram(df, x="predictions", labels={"predictions": "Predicted Trend +/-"})
    fig.update_yaxes(visible=False, showticklabels=False)
    histogram_div = plot(fig, output_type='div')



    # best best predicted line chart
    target_symbol = "abnb"
    data = utils.get_symbol_data_from_db(target_symbol)
    print(data.head())
    fig = px.line(data, x="date", y=["high", "low", "open", "close"],
        labels={
                        "date": "Date",
                        "value": "Value",
                        "variable": "Target"
                    },
    )
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_layout(
        height=418
    )
    line_chart_div = plot(fig, output_type='div')



    stock_trends_positive = sorted([{"symbol": symbol, "trend": round(np.random.normal(0, 2) + 5, 2)} for symbol in random.sample(utils.get_symbols(), 3)], key=itemgetter("trend"), reverse=True)
    stock_trends_positive = [{"symbol": stock_trend_positive["symbol"], "trend_bin": True, "trend": "+{}%".format(stock_trend_positive["trend"])} for stock_trend_positive in stock_trends_positive]
    
    stock_trends_negative = sorted([{"symbol": symbol, "trend": round(np.random.normal(0, 2) - 5, 2)} for symbol in random.sample(utils.get_symbols(), 3)], key=itemgetter("trend"), reverse=True)
    stock_trends_negative = [{"symbol": stock_trend_negative["symbol"], "trend_bin": False, "trend": "{}%".format(stock_trend_negative["trend"])} for stock_trend_negative in stock_trends_negative]
    
    stocks = len(utils.get_symbols())

    context = {
        "stocks": stocks, 
        "histogram_div": histogram_div,
        "line_chart_div": line_chart_div,
        "line_chart_symbol": target_symbol.upper(),
        "stock_trends_positive": stock_trends_positive,
        "stock_trends_negative": stock_trends_negative,
        "stock_list_verbose": config["stock_list"]["verbose"].split(' ')[0],
        "stock_list_date_updated": config["stock_list"]["date_updated"]
    }

    if request.method == 'POST':
        if 'submit-symbol-search' in request.POST:
            symbol_form = SymbolForm(request.POST)
            if symbol_form.is_valid():
                return HttpResponseRedirect('{0}/'.format(symbol_form.cleaned_data['symbol']))

    return HttpResponse(template.render(context, request))


def dashboard_symbol(request, symbol):

    data = utils.get_symbol_data_from_db(symbol)
    fig = px.line(data, x="date", y="open")
    line_chart_div = plot(fig, output_type='div')

    template = loader.get_template('visualizer/dashboard_symbol.html')

    symbol_info = utils.get_symbol_information(symbol)

    context = {
        'symbol': symbol,
        'symbol_verbose': symbol_info["Security Name"],
        'line_chart_div': line_chart_div
    }
    
    return HttpResponse(template.render(context, request))
