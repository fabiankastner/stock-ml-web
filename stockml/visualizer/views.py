from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

from common.util.retrieve_data import get_df_from_symbol
from .forms import SymbolForm


def index(request):
    return redirect('/dashboard/')


def login(request):
    template = loader.get_template('visualizer/login.html')
    context = {}
    return HttpResponse(template.render(context, request))


def dashboard(request):

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
        "stock_trends": stock_trends
    }

    # handle post request
    if request.method == 'POST':
        
        # handle submit-symbol-search request
        if 'submit-symbol-search' in request.POST:
            symbol_form = SymbolForm(request.POST)
            if symbol_form.is_valid():
                return HttpResponseRedirect('{0}/'.format(symbol_form.cleaned_data['symbol']))

    else:
        pass

    return HttpResponse(template.render(context, request))


def dashboard_symbol(request, symbol):

    data = get_df_from_symbol(symbol)
    fig = px.line(data, x="date", y="open")
    line_chart_div = plot(fig, output_type='div')

    template = loader.get_template('visualizer/dashboard_symbol.html')
    
    symbols_verbose = {
        "pltr": "Palantir",
        "tsla": "Tesla"
    }

    if symbol not in symbols_verbose: symbols_verbose[symbol] = symbol

    context = {
        'symbol': symbol,
        'symbol_verbose': symbols_verbose[symbol],
        'line_chart_div': line_chart_div
    }
    
    return HttpResponse(template.render(context, request))
