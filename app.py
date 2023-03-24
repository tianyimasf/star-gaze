import pandas as pd
import numpy as np
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
from helper import absmag2rad





app = Dash(__name__)

server = app.server

# -- Import and clean data (importing csv into pandas)
# TODO: 
#   1. Convert constellation name from abbr to full name
#   2. Add more interesting info and allow subsetting with BV, mag and maybe spetral values
df = pd.read_csv("./data/hygdata_v3.csv")# Get the first 100 rows
df2 = pd.read_csv("./data/hygxyz.csv")

data = pd.DataFrame()

data['x'] = df['dist'] * np.cos(np.radians(df['dec'])) * np.cos(np.radians(df['ra']*15))
data['y'] = df['dist'] * np.cos(np.radians(df['dec'])) * np.sin(np.radians(df['ra']*15))
data['z'] = df['dist'] * np.sin(np.radians(df['dec']))
# data['color'] = [bvToRgb(color_index) for color_index in df2['ColorIndex']]
# data['color'] = np.array([f'rgb({color_index[0]}, ({color_index[1]}, ({color_index[2]})' for color_index in data['color']]) fix later
data['color'] = np.array(['rgb(255,255,255)' for color_index in data['x']])
data['radius'] = np.array([absmag2rad(bv, absmag) for (bv, absmag) in zip(df2.ColorIndex, df.absmag)])
data = pd.concat([data, df[['con', 'mag', 'spect', 'dist']], df2['ColorIndex']], axis=1)
data = data.dropna()[1:]
data = data[data['mag'] < 6]

coordinates = ['x', 'y', 'z']
for c in coordinates:
    lower = np.quantile(data[c], 0.16)
    upper = np.quantile(data[c], 0.84)
    data = data[(data[c] > lower) & (data[c] < upper)]


# ------------------------------------------------------------------------------
# Build Figure through Plotly

fig = go.Figure(data=[go.Scatter3d(
    x=data.x,
    y=data.y,
    z=data.z,
    customdata = np.stack((data['spect'], data['con'], data['radius'], data['dist']), axis=-1),
    hovertemplate = 
    '<b>Spectral</b>: %{customdata[0]}<br>'+
    '<b>Constellation</b>: %{customdata[1]}<br>'+
    '<b>Radius</b>: %{customdata[2]}<br>'+
    '<b>Distance (from sun)</b>: %{customdata[3]}<br>'+
    '<b>(x, y, z)</b>: (%{x:.2f}, %{y:.2f}, %{z:.2f})<br>',
    mode='markers',
    marker=dict(
        size=data.radius*2,
        color=data.color,                # set color to an array/list of desired values
        opacity=0.8,
    ),
)])
# Styling
fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False) # invisible axises
fig.update_layout(paper_bgcolor="black") # black background, resize
fig.update_layout( # Styling hoverlabel
    hoverlabel=dict(
        bgcolor="white",
        font_size=14,
        font_family="Arial"
    )
)
camera = dict(
    eye=dict(x=0.0001, y=-0.2, z=0.02)
)
fig.update_layout(scene_camera=camera)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Star Gazing with Dash and Plotly", style={'text-align': 'center'}),

    html.Div(id='output_container', children=[]),
    html.Br(),

    html.Div(
        children = [dcc.Graph(id='stars_plot', figure=fig, style={'height': '85vh'})],
        className='graph',
    )
])


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
# @app.callback(
#     [Output(component_id='output_container', component_property='children'),
#      Output(component_id='my_bee_map', component_property='figure')],
#     [Input(component_id='slct_year', component_property='value')]
# )
# def update_graph(option_slctd):
#     print(option_slctd)
#     print(type(option_slctd))

#     container = "The year chosen by user was: {}".format(option_slctd)

#     dff = df.copy()
#     dff = dff[dff["Year"] == option_slctd]
#     dff = dff[dff["Affected by"] == "Varroa_mites"]

#     # Plotly Express
#     fig = px.choropleth(
#         data_frame=dff,
#         locationmode='USA-states',
#         locations='state_code',
#         scope="usa",
#         color='Pct of Colonies Impacted',
#         hover_data=['State', 'Pct of Colonies Impacted'],
#         color_continuous_scale=px.colors.sequential.YlOrRd,
#         labels={'Pct of Colonies Impacted': '% of Bee Colonies'},
#         template='plotly_dark'
#     )

#     # Plotly Graph Objects (GO)
#     # fig = go.Figure(
#     #     data=[go.Choropleth(
#     #         locationmode='USA-states',
#     #         locations=dff['state_code'],
#     #         z=dff["Pct of Colonies Impacted"].astype(float),
#     #         colorscale='Reds',
#     #     )]
#     # )
#     #
#     # fig.update_layout(
#     #     title_text="Bees Affected by Mites in the USA",
#     #     title_xanchor="center",
#     #     title_font=dict(size=24),
#     #     title_x=0.5,
#     #     geo=dict(scope='usa'),
#     # )

#     return container, fig


# ------------------------------------------------------------------------------
# if __name__ == '__main__':
#     app.run_server(debug=True)