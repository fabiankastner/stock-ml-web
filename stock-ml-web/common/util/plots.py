import numpy as np
import pandas as pd
import plotly.express as px
from plotly.offline import plot

from common.util.utils import *

def get_hist():

    # df = pd.DataFrame({'predictions': np.random.normal(0, 0.3, 50).tolist()})

    # df = get_stuff_from_db() 
    return None

    fig = px.histogram(df, x="predictions", labels={"predictions": "Predicted Trend +/-"})
    fig.update_yaxes(visible=False, showticklabels=False)
    fig.update_layout(
        height=526
    )
    histogram_div = plot(fig, output_type='div', config=dict(displayModeBar=False))

    return histogram_div


def get_line_chart(symbol):

    data = get_symbol_data_from_db(symbol)
    if not data: return None

    data = data.iloc[-5000: ]

    print(data.head())
    data = data.reset_index(drop=True)
    print(data.head())

    pred_len_rel = 0.1

    data_prediction = data.iloc[int(data.shape[0] * (1 - pred_len_rel)): , : ]
    data_prediction.columns = ['id', 'date', 'open_prediction', 'high_prediction', 'low_prediction', 'close_prediction', 'volume', 'symbol']
    data_prediction['high'] = None
    data_prediction['low'] = None
    data_prediction['open'] = None
    data_prediction['close'] = None

    data = data.iloc[ :int(data.shape[0] * (1 - pred_len_rel)), : ]
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

    data_len = data.shape[0]
    data_orig_len = data_len * (1 - pred_len_rel)
    
    print(data.dtypes)

    fig = px.line(data, x=data.index, y=["high", "low", "open", "close", "high_prediction", "low_prediction", "open_prediction", "close_prediction"],
        labels={
                        "date": "Date",
                        "value": "Value",
                        "variable": "Target"
                    },
                    color_discrete_sequence=["#99AFC2", "#C9DFB9", "#FBC888", "#FCB0B2", "#4D6880", "#7DB257", "#EC8609", "#F7262D",]
    )
    
    fig.add_vrect(x0=data_orig_len, x1=data_len, line_width=0, fillcolor="black", opacity=0.1)
    fig.add_vrect(x0=data_orig_len, x1=data_orig_len, line_dash="dash")

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(
        height=418
    )
    
    line_chart_div = plot(fig, output_type='div', config=dict(displayModeBar=False))
    
    return line_chart_div
