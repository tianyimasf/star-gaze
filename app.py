import pandas as pd
import numpy as np
import plotly.express as px  # (version 4.7.0 or higher)
import plotly.graph_objects as go
import colorsys
from dash import Dash, dcc, html, Input, Output  # pip install dash (version 2.0.0 or higher)
from helper import absmag2rad, bvToRgb, bv2rgb, const_abbr2full






app = Dash(__name__)

# server = app.server

# -- Import and clean data (importing csv into pandas)
# TODO: 
#   1. Convert constellation name from abbr to full name
#   2. Add more interesting info and allow subsetting with BV, mag and maybe spectral values
df = pd.read_csv("./data/hygdata_v3.csv")

data = pd.DataFrame()
data = pd.concat([data, df[['hip', 'con', 'mag', 'absmag', 'spect', 'dist', 'ci']]], axis=1)

data['x'] = np.cos(np.radians(df['dec'])) * np.cos(np.radians(df['ra']*15))
data['y'] = np.cos(np.radians(df['dec'])) * np.sin(np.radians(df['ra']*15))
data['z'] = np.sin(np.radians(df['dec']))
data['color'] = [bv2rgb(color_index) for color_index in data['ci']]
data['con'] = data['con'].apply(const_abbr2full)

data = data.dropna()[1:]
data = data[(data['mag'] < 6) & (data['ci'] > -0.4) & data['ci'] <= 2.0]

lower = np.quantile(data['absmag'], 0.25)
upper = np.quantile(data['absmag'], 0.75)
data = data[(data['absmag'] > lower) & data['absmag'] < upper]
blue_stars = data[(data['ci'] > -0.4) & (data['ci'] < 0)]
yellow_stars = data[data['ci'] > 0.15]
data = pd.concat([blue_stars.sample(5000), yellow_stars.sample(5000)], axis=0)

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


data['color'] = [change_saturation_by(rgb, 1.1) for rgb in data['color']]


def is_valid_ci(ci):
    return all([ci[i] > 0 for i in range(2)])

data['color'] = np.array([f'rgb({color_index[0]}, {color_index[1]}, {color_index[2]})' if is_valid_ci(color_index) else None for color_index in data['color']]) # fix later
data['radius'] = np.array([absmag2rad(bv, absmag) for (bv, absmag) in zip(data['ci'], data['absmag'])])
data['radius'] = np.exp(data['radius'] + 0.1) * 1.7
data = data[data['radius'] > 0]
data = data[~data['color'].isnull()]


# ------------------------------------------------------------------------------
# Build Figure through Plotly

def generate_fig(data):

    def transform_radius(r):
        return r * 1.5 if r > 1 else r ** 3 + 0.5

    fig = go.Figure(data=[go.Scatter3d(
        x=data['x'],
        y=data['y'],
        z=data['z'],
        customdata = np.stack((data['spect'], data['con'], data['absmag'], data['dist'], data['hip'], data['ci']), axis=-1),
        hovertemplate = 
        '<b>HIP</b>: %{customdata[4]}<br>'+
        '<b>Spectral</b>: %{customdata[0]}<br>'+
        '<b>Constellation</b>: %{customdata[1]}<br>'+
        '<b>B - V</b>: %{customdata[5]}<br>'+
        '<b>Absolute Magnitude</b>: %{customdata[2]}<br>'+
        '<b>Distance (from sun)</b>: %{customdata[3]}<br>',
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
    return fig

# ------------------------------------------------------------------------------
# App layout
dropdown_options = np.concatenate((["All"], np.asarray(data['con'].unique())), axis = 0)

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    html.H4("⭐ Star Gazing with Dash and Plotly"),
                                    className="header__title",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Click on each star to see details. Drag to see different parts of the sky. (Try zoom all the way out!)"
                                        )
                                    ],
                                    className="header__info pb-20",
                                ),
                                html.Div(
                                    [
                                        html.A(
                                            "View Source Code on GitHub",
                                            href="https://github.com/tianyimasf/star-gaze",
                                            target="_blank",
                                        )
                                    ],
                                    className="header__button",
                                ),
                            ],
                            className="header pb-20",
                        ),
                        html.Div(
                            [
                                dcc.Graph(id='stars_plot', figure=generate_fig(data), style={'height': '95vh'})
                            ],
                            className="graph__container",
                        ),
                    ],
                    className="container",
                )
            ],
            className="two-thirds column app__left__section",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.P(
                                    "Click to select specific constellation(s)", className="subheader"
                                ),
                                dcc.Dropdown(id="constellation",
                                                options=dropdown_options,
                                                multi=True,
                                                value=dropdown_options[:3],
                                                style={'width': "100vh", "color":"grey"}
                                            ),
                            ]
                        )
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.P("Filter by possible BV value", className="subheader"),
                        dcc.RangeSlider(min=-0.4, max=2.0, step=0.01, value=[-0.2, 1.8], marks={-0.4: {"label": "-0.4"}, 0: {"label": "0"}, 1: {"label": "1"}, 2: {"label": "2.0"},
                                            }, id='bv-range-slider'),
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.P("Filter by possible Absolute Magnitude value", className="subheader"),
                        dcc.RangeSlider(min=lower, max=upper, step=0.1, value=[0, 2.5], marks={lower: {"label": str(lower)}, 1: {"label": "1"}, 2: {"label": "2"}, upper: {"label": str(upper)},
                                            }, id='absmag-range-slider'),
                    ],
                    className="pb-20",
                ),
            ],
            className="one-third column app__right__section",
        ),
    ]
)


# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='stars_plot', component_property='figure')],
    [Input(component_id='constellation', component_property='value'),
     Input(component_id='bv-range-slider', component_property='value'),
     Input(component_id='absmag-range-slider', component_property='value'),]
)
def update_figure(cons, bv_range, absmag_range):
    selected_data = data[data["con"].isin(cons)] if not ("All" in cons) else data
    selected_data = selected_data[(selected_data['ci'] >= bv_range[0]) & (selected_data['ci'] <= bv_range[1])]
    selected_data = selected_data[(selected_data['absmag'] >= absmag_range[0]) & (selected_data['absmag'] <= absmag_range[1])]

    return [generate_fig(selected_data)]


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)