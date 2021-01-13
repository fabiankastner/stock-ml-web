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
    data = data.iloc[-5000: ]

    print(data.head())
    data = data.reset_index(drop=True)
    print(data.head())

    data_prediction = data.iloc[int(data.shape[0] * 0.9): , : ]
    data_prediction.columns = ['id', 'date', 'open_prediction', 'high_prediction', 'low_prediction', 'close_prediction', 'volume', 'symbol']
    data_prediction['high'] = None
    data_prediction['low'] = None
    data_prediction['open'] = None
    data_prediction['close'] = None

    data = data.iloc[ :int(data.shape[0] * 0.9), : ]
    data['high_prediction'] = None
    data['low_prediction'] = None
    data['open_prediction'] = None
    data['close_prediction'] = None

    print(data_prediction.shape)
    print(data_prediction.columns)

    print(data.shape)
    print(data.columns)

    data = data.append(data_prediction)

    data.high = data.high.astype('float64')
    data.low = data.low.astype('float64')
    data.open = data.open.astype('float64')
    data.close = data.close.astype('float64')

    print(data.shape)
    print(data.columns)
    
    print(data.dtypes)

    fig = px.line(data, x=data.index, y=["high", "low", "open", "close", "high_prediction", "low_prediction", "open_prediction", "close_prediction"],
        labels={
                        "date": "Date",
                        "value": "Value",
                        "variable": "Target"
                    },
                    color_discrete_sequence=["#99AFC2", "#C9DFB9", "#FBC888", "#FCB0B2", "#4D6880", "#7DB257", "#EC8609", "#F7262D",]
    )
    
    fig.add_vrect(x0=4500, x1=5000, line_width=0, fillcolor="green", opacity=0.1)
    fig.add_vrect(x0=4500, x1=4500, line_dash="dash")

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(
        height=418
    )
    line_chart_div = plot(fig, output_type='div', config=dict(
                    displayModeBar=False)
                    )



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
