import numpy as np
import pandas as pd
import plotly.express as px
import datetime as dt
import json
from solver import assign_rides


def plot_rides(rides: list[tuple[int,int]], car_assignments: list[int], car_durations: list[int]):
    df = pd.DataFrame(rides, columns=['start', 'end'])
    df['car'] = car_assignments
    date = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    df['start_time'] = df['start'].apply(lambda x: date + dt.timedelta(minutes=x))
    df['end_time'] = df['end'].apply(lambda x: date + dt.timedelta(minutes=x))

    fig = px.timeline(df, x_start='start_time', x_end='end_time', y='car', title='Car assignments')
    fig.update_yaxes(categoryorder='total ascending')
    fig.update_xaxes(tickformat='%H:%M', type='date', tick0=date, dtick=3600000)
    fig.update_layout(yaxis_title='Car', height=max(500, min(100*len(car_durations), 1000)))
    fig.update_yaxes(tickvals=np.arange(len(df['car'].unique())), ticktext=[f'Car {i+1}  ' for i in range(len(df['car'].unique()))])
    fig.update_traces(marker_line_color='black', marker_line_width=1)
    for i, duration in enumerate(car_durations):
        fig.add_hline(y=i, line_color='black', opacity=0.2)
        end_date = date + dt.timedelta(minutes=max(end for (_, end) in rides)+100)
        fig.add_annotation(x=end_date, y=i, text=f'Duration: {duration} minutes', showarrow=False, yshift=10)
    return fig


if __name__ == '__main__':
    config = json.load(open('config.json'))
    rides = [(np.random.randint(0, 1440), np.random.randint(config['min_ride_duration'], config['max_ride_duration']))
             for _ in range(config['nb_rides'])]
    rides = [(x, x+y) for x, y in rides]
    car_assignments, car_durations = assign_rides(rides, max_running_time=config['max_running_time_in_seconds'])
    if car_assignments is not None:
        fig = plot_rides(rides, car_assignments, car_durations)
        fig.write_html(config['save_plot_filename'], auto_open=True)



