from django.template import loader
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages

from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
import configparser

from common.util.retrieve_data import get_df_from_symbol
from common.util.utils import get_config, get_symbol_information
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
    config = get_config()

    template = loader.get_template('visualizer/dashboard.html')
    
    df = pd.DataFrame({'predictions': np.random.normal(0, 0.3, 50).tolist()})
  
    fig = px.histogram(df, x="predictions", title="Histogram of Predicted Trends", labels={"predictions": "Predicted Trend +/-"})
    fig.update_yaxes(visible=False, showticklabels=False)
    histogram_div = plot(fig, output_type='div')

    stock_trends = [
        {
            "symbol": "TSLA",
            "trend": "+11.3 %"
        },
        {
            "symbol": "PLTR",
            "trend": "+4.7 %"
        }
    ]

    context = {
        "histogram_div": histogram_div,
        "stock_trends": stock_trends,
        "stock_list_verbose": config["stock_list"]["verbose"],
        "stock_list_date_updated": config["stock_list"]["date_updated"]
    }

    if request.method == 'POST':
        if 'submit-symbol-search' in request.POST:
            symbol_form = SymbolForm(request.POST)
            if symbol_form.is_valid():
                return HttpResponseRedirect('{0}/'.format(symbol_form.cleaned_data['symbol']))

    return HttpResponse(template.render(context, request))


def dashboard_symbol(request, symbol):

    config = get_config()
    key = config["keys"]["alpha_vantage_api"]

    data = get_df_from_symbol(symbol, key, "1min")
    fig = px.line(data, x="date", y="open")
    line_chart_div = plot(fig, output_type='div')

    template = loader.get_template('visualizer/dashboard_symbol.html')

    symbol_info = get_symbol_information(symbol)

    context = {
        'symbol': symbol,
        'symbol_verbose': symbol_info["Security Name"],
        'line_chart_div': line_chart_div
    }
    
    return HttpResponse(template.render(context, request))
