from django.template import loader
from django.shortcuts import render
from django.http import HttpResponse

from plotly.offline import plot
import plotly.graph_objs as go
import plotly.express as px

from common.util.retrieve_data import get_df_from_symbol


def index(request):
    data = get_df_from_symbol("PLTR")
    fig = px.line(data, x="date", y="open")
    plt_div = plot(fig, output_type='div')

    template = loader.get_template('visualizer/index.html')
    context = {
        'plt_div': plt_div,
    }
    
    return HttpResponse(template.render(context, request))
