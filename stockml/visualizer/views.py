from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect

from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px

from common.util.retrieve_data import get_df_from_symbol
from .forms import SymbolForm


def index(request):
    return redirect('dashboard/')


def dashboard(request):
    template = loader.get_template('visualizer/dashboard.html')
    context = {
    }
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        symbol_form = SymbolForm(request.POST)
        # check whether it's valid:
        if symbol_form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            print(symbol_form.cleaned_data)
            return HttpResponseRedirect('{0}/'.format(symbol_form.cleaned_data['symbol']))

    # if a GET (or any other method) we'll create a blank form
    else:
        symbol_form = SymbolForm()
        context['symbol_form'] = symbol_form

    return HttpResponse(template.render(context, request))


def dashboard_symbol(request, symbol):
    data = get_df_from_symbol(symbol)
    fig = px.line(data, x="date", y="open")
    plt_div = plot(fig, output_type='div')

    template = loader.get_template('visualizer/dashboard_symbol.html')
    context = {
        'symbol': symbol,
        'plt_div': plt_div
    }
    
    return HttpResponse(template.render(context, request))