import pandas as pd
import numpy as np
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
import colorsys
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
from helper import absmag2rad, bvToRgb, bv2rgb






app = Dash(__name__)

# server = app.server

# -- Import and clean data (importing csv into pandas)
# TODO: 
#   1. Convert constellation name from abbr to full name
#   2. Add more interesting info and allow subsetting with BV, mag and maybe spetral values
df = pd.read_csv("./data/hygdata_v3.csv")

data = pd.DataFrame()
data = pd.concat([data, df[['hip', 'con', 'mag', 'absmag', 'spect', 'dist', 'ci']]], axis=1)

data['x'] = np.cos(np.radians(df['dec'])) * np.cos(np.radians(df['ra']*15))
data['y'] = np.cos(np.radians(df['dec'])) * np.sin(np.radians(df['ra']*15))
data['z'] = np.sin(np.radians(df['dec']))
data['color'] = [bv2rgb(color_index) for color_index in data['ci']]

data = data.dropna()[1:]
data = data[(data['mag'] < 6) & (data['ci'] > -0.4) & data['ci'] <= 2.0]

upper = np.quantile(data['absmag'], 0.95)
data = data[data['absmag'] < upper]
blue_stars = data[(data['ci'] > -0.4) & (data['ci'] < -0.055)]
yellow_stars = data[data['ci'] > 0.15]
data = pd.concat([blue_stars.sample(3000), yellow_stars.sample(3000)], axis=0)

def change_saturation_by(rgb, p):
    hsv = colorsys.rgb_to_hsv(rgb[0], rgb[1], rgb[2])
    hsv_new = (hsv[0], hsv[1] * p, hsv[2])
    rgb_new = colorsys.hsv_to_rgb(hsv_new[0], hsv_new[1], hsv_new[2])

    R = round(rgb_new[0])
    G = round(rgb_new[1])
    B = round(rgb_new[2])
    R = 255 if R > 255 else R
    R = 0 if R < 0 else R
    G = 255 if G > 255 else G
    G = 0 if G < 0 else G
    B = 255 if B > 255 else B
    B = 0 if B < 0 else B

    return [R, G, B]


data['color'] = [change_saturation_by(rgb, 1.5) for rgb in data['color']]


def is_valid_ci(ci):
    return all([ci[i] > 0 for i in range(2)])

data['color'] = np.array([f'rgb({color_index[0]}, {color_index[1]}, {color_index[2]})' if is_valid_ci(color_index) else None for color_index in data['color']]) # fix later
data['radius'] = np.array([absmag2rad(bv, absmag) for (bv, absmag) in zip(data['ci'], data['absmag'])])
data['radius'] = np.log(data['radius'] * 10 + 1)
data = data[data['radius'] > 0]
data = data[~data['color'].isnull()]


# ------------------------------------------------------------------------------
# Build Figure through Plotly

fig = go.Figure(data=[go.Scatter3d(
    x=data['x'],
    y=data['y'],
    z=data['z'],
    customdata = np.stack((data['spect'], data['con'], data['radius'], data['dist'], data['color'], data['hip'], data['ci']), axis=-1),
    hovertemplate = 
    '<b>HIP</b>: %{customdata[5]}<br>'+
    '<b>Spectral</b>: %{customdata[0]}<br>'+
    '<b>Constellation</b>: %{customdata[1]}<br>'+
    '<b>Radius</b>: %{customdata[2]}<br>'+
    '<b>Distance (from sun)</b>: %{customdata[3]}<br>'+
    '<b>B - V</b>: %{customdata[6]}<br>'+
    '<b>Color</b>: %{customdata[4]}<br>'+
    '<b>(x, y, z)</b>: (%{x:.2f}, %{y:.2f}, %{z:.2f})<br>',
    mode='markers',
    marker=dict(
        size=data['radius'],
        color=data['color'], 
        line=dict(width=2, color=data['color']),             # set color to an array/list of desired values
        opacity=1,
    ),
)])
# Styling
fig.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False) # invisible axises
fig.update_layout(paper_bgcolor="black") # black background
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
        children = [dcc.Graph(id='stars_plot', figure=fig, style={'height': '95vh'})],
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
if __name__ == '__main__':
    app.run_server(debug=True)