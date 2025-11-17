# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# App layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'font-size': 40
        }
    ),

    # ---------- TASK 1: Launch Site dropdown ----------
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites',    'value': 'ALL'},
            {'label': 'CCAFS LC-40',  'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E',  'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A',   'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        value='ALL',  # default
        placeholder='Select a Launch Site Here',
        searchable=True
    ),

    html.Br(),

    # ---------- TASK 2: Pie chart ----------
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # ---------- TASK 3: RangeSlider ----------
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={
            int(min_payload): str(int(min_payload)),
            int(max_payload): str(int(max_payload))
        },
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # ---------- TASK 4: Scatter chart ----------
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# ---------- TASK 2: callback for pie chart ----------
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Total success launches by site
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Successful Launches for All Sites'
        )
    else:
        # Success vs failure for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]

        counts = (
            filtered_df['class']
            .value_counts()
            .reset_index()
        )
        counts.columns = ['class', 'count']

        fig = px.pie(
            counts,
            values='count',
            names='class',
            title=f'Total Success vs Failure for {selected_site}'
        )

    return fig


# ---------- TASK 4: callback for scatter chart ----------
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range

    # Filter by payload range first
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # If a specific site is selected, filter by that site as well
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    title_site = 'All Sites' if selected_site == 'ALL' else selected_site

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Correlation between Payload and Success for {title_site}',
        hover_data=['Launch Site']
    )

    return fig


# Run the app
if __name__ == '__main__':
    app.run()
