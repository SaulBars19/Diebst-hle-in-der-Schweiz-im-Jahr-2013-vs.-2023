from dash import Dash, dcc, html, Input, Output, callback_context
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

# Laden der Daten
df_Diebstahl = pd.read_csv('/Users/saulbarrientosdelosmonterorivera/Documents/Projecto Lea/OneDrive_1_25.6.2024/Diebstahl.csv', sep=';')

# Entfernen von Zeilen, die das Wort "total" enthalten
df_Diebstahl = df_Diebstahl[~df_Diebstahl.apply(lambda row: row.astype(str).str.contains('total', case=False).any(), axis=1)]

# Filtern für 'Mann' und 'Frau' und Ausschluss von 'Altersklasse - Total'
data = df_Diebstahl[(df_Diebstahl['Geschlecht'].isin(['Mann', 'Frau'])) & (df_Diebstahl['Altersklasse'] != 'Altersklasse - Total')]

# Laden der Daten für die Karte
df_Diebstahl_Map = pd.read_csv('/Users/saulbarrientosdelosmonterorivera/Documents/Projecto Lea/OneDrive_1_25.6.2024/Diebstahl_Map.csv', sep=';')

# Definieren der Farben für spezifische Kantone
color_map = {
    'St. Gallen': '#174679',
    'Zürich': '#174679',
    'Aargau': '#174679',
    'Vaud': '#174679',
    'Bern / Berne': '#174679'
}

# Funktion zur Erstellung des Slope-Diagramms
def create_slope_graph():
    fig = go.Figure()

    for i, row in df_Diebstahl_Map.iterrows():
        kanton = row['Kanton']
        color = color_map.get(kanton, 'gray')  # Standardfarbe ist grau, wenn der Kanton nicht im color_map ist
        
        fig.add_trace(go.Scatter(
            x=[2013, 2023],
            y=[row['Anzahl_2013'], row['Anzahl_2023']],
            mode='lines+markers+text',
            text=[kanton],
            textposition='top right' if kanton != 'Aargau' else 'bottom right', # Textwinkel für Aarau anpassen (nach unten rechts orientiert)
            textfont=dict(size=12, color='black', family='Arial Black'),
            name=kanton,
            line=dict(color=color),
            marker=dict(size=8, color=color)
        ))
        
    fig.update_layout(
        xaxis_title="Jahr",
        yaxis_title="Anzahl Diebstähle",
        xaxis=dict(tickvals=[2013, 2023]),
        yaxis=dict(showgrid=True),
        showlegend=False
    )

    return fig

# Initialisierung der Dash-App
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Layout der App mit zwei Tabs
app.layout = dbc.Container([
    html.H1("Diebstähle in der Schweiz im Jahr 2013 vs. 2023"),

    dcc.Tabs([
        dcc.Tab(label='Analyse eines Kantons', children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Vergleich der Zahlen nach Alter und Jahr"),
                    dcc.Dropdown(
                        id='kanton-dropdown',
                        options=[{'label': k, 'value': k} for k in df_Diebstahl["Kanton"].unique()],
                        value='Zürich',
                        multi=False
                    ),
                    dcc.Graph(id="graph_balken", style={'border': '1px solid black', 'height': '500px'})
                ], width=6),

                dbc.Col([
                    html.H3("Balkendiagramm Geschlecht"),
                    dcc.Dropdown(
                        id='bar-chart-kanton-dropdown',
                        options=[{'label': k, 'value': k} for k in df_Diebstahl["Kanton"].unique()],
                        value='Zürich',
                        multi=False
                    ),
                    html.Div(id='bar-chart-container', children=[
                        dcc.Graph(id="bar-chart", style={'border': '1px solid black', 'height': '500px'}),
                        html.Div([
                            dbc.Button("2013", id="btn-2013", className="me-2", n_clicks=0),
                            dbc.Button("2023", id="btn-2023", className="me-2", n_clicks=0),
                        ], style={'margin-top': '20px', 'text-align': 'center'})
                    ])
                ], width=6)
            ]),
            html.Div("Quelle: BFS, 2024", style={'text-align': 'right', 'margin-top': '20px'})
        ]),

        dcc.Tab(label='Vergleich von Kantonen', children=[
            dbc.Row([
                dbc.Col([
                    html.H3("Verteilung der Diebstähle - Karte"),
                    dcc.Dropdown(
                        id='jahr-auswahl',
                        options=[
                            {'label': '2013', 'value': 'Anzahl_2013'},
                            {'label': '2023', 'value': 'Anzahl_2023'}
                        ],
                        value='Anzahl_2023',
                        multi=False
                    ),
                    dcc.Graph(id='map-graph', style={'border': '1px solid black', 'height': '500px'})
                ], width=6),

                dbc.Col([
                    html.H3("Vergleich der Diebstähle zwischen den Jahren 2013 und 2023"),
                    dcc.Graph(id='slope-graph', style={'border': '1px solid black', 'height': '500px'})
                ], width=6)
            ]),
            html.Div("Quelle: BFS, 2024", style={'text-align': 'right', 'margin-top': '20px'})
        ])
    ])
], fluid=True)

# Callback für das Balkendiagramm Alter/Kanton/Jahr
@app.callback(Output("graph_balken", "figure"), [Input("kanton-dropdown", "value")])
def update_balken(auswahl_stadt):
    dff = df_Diebstahl[df_Diebstahl["Kanton"] == auswahl_stadt]
    fig = px.bar(dff, x="Altersklasse", y=["2013", "2023"], barmode='group', 
                 color_discrete_map={'2013': 'lightblue', '2023': 'darkblue'})
    fig.update_layout(title_text='Diebstahl nach Altersklasse für {}'.format(auswahl_stadt))
    return fig

# Callback für das Balkendiagramm Geschlecht
@app.callback(
    Output('bar-chart', 'figure'),
    [Input('bar-chart-kanton-dropdown', 'value'),
     Input('btn-2013', 'n_clicks'),
     Input('btn-2023', 'n_clicks')]
)
def update_chart(selected_kanton, n_clicks_2013, n_clicks_2023):
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "btn-2023":
        year = '2023'
    else:
        year = '2013'

    filtered_data = data[data['Kanton'] == selected_kanton]

    fig = px.bar(filtered_data, x='Altersklasse', y=year, color='Geschlecht',
                 color_discrete_map={'Mann': 'darkblue', 'Frau': 'darkred'},
                 title=f'Diebstähle nach Geschlecht in {selected_kanton} im Jahr {year}')

    fig.update_layout(transition_duration=500,
                      title_text=f'Diebstähle nach Geschlecht in {selected_kanton} im Jahr {year}')

    return fig

# Callback für die Karte
@app.callback(Output("map-graph", "figure"),
              Input("jahr-auswahl", "value"))
def update_map(selected_year):
    # Benutzerdefinierte Farbskala
    custom_colorscale = [
        [0.0, 'rgb(240,248,255)'],  # aliceblue
        [0.2, 'rgb(135,206,235)'],  # skyblue
        [0.4, 'rgb(0,191,255)'],    # deepskyblue
        [0.6, 'rgb(30,144,255)'],   # dodgerblue
        [0.8, 'rgb(0,0,255)'],      # blue
        [1.0, 'rgb(0,0,139)']       # darkblue
    ]

    # Obtener el máximo valor entre Anzahl_2013 y Anzahl_2023 para establecer la misma escala de color
    max_value = max(df_Diebstahl_Map[['Anzahl_2013', 'Anzahl_2023']].max())

    fig = px.scatter_mapbox(
        df_Diebstahl_Map,
        lat="Latitude",
        lon="Longitude",
        size=selected_year,
        hover_name="Kanton",
        hover_data={selected_year: True},
        size_max=20,
        zoom=6,
        mapbox_style="carto-positron",
        title="Anzahl Diebstähle nach Kanton zwischen 2013 und 2023"
    )

    fig.update_traces(marker=dict(
        color=df_Diebstahl_Map[selected_year],
        colorscale=custom_colorscale,
        showscale=True,
        size=20,  # Setze eine feste Grösse für alle Marker
        cmin=0,
        cmax=max_value  # Legt den Maximalwert für die Farbskala fest
    ))

    return fig

# Callback für das Slope-Diagramm
@app.callback(Output("slope-graph", "figure"), [Input("jahr-auswahl", "value")])
def update_slope(selected_year):
    # Erstelle das Slope-Diagramm mit den aktualisierten Daten
    fig = create_slope_graph()
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, port=8053)
