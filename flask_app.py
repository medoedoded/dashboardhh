from urllib.request import urlopen
import json
from dash import Dash, Input, Output, callback, dcc, html
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px


df = pd.read_csv('Loginom_hh_data_excel1.csv', sep=';')
all_areas = pd.unique(df['area_name'])

with urlopen('https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/russia.geojson') as response:
    counties = json.load(response)

df.loc[df['description'].str.contains('C\+\+|Go'), 'name'] = 'Python Developer'
df.loc[df['name'].str.contains('Backend'), 'name'] = 'Python Backend Developer'
df.loc[df['name'].str.contains('Lead'), 'name'] = 'Python Developer TeamLead'
df.loc[df['description'].str.contains('Data'), 'name'] = 'Data Scientist'
df.loc[df['name'].str.contains('Data'), 'name'] = 'Data Scientist'
df.loc[df['name'].str.contains('Аналитик|Analytic'), 'name'] = 'Python аналитик'
df.loc[df['name'].str.contains('Web'), 'name'] = 'Python Web Developer'
df.loc[df['description'].str.contains('Web'), 'name'] = 'Python Web Developer'
df.loc[df['name'].str.contains('Стажер'), 'name'] = 'Python Developer Стажер'
df.loc[df['name'].str.contains('Junior'), 'name'] = 'Python Developer Младший'
df.loc[df['name'].str.contains('Middle'), 'name'] = 'Python Developer'
df.loc[df['name'].str.contains('тестированию'), 'name'] = 'Python Developer Тестировщик'
df.loc[df['name'].str.contains('разработчик'), 'name'] = 'Программист Python'


external_stylesheets = [dbc.themes.BOOTSTRAP]
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.config.suppress_callback_exceptions = True

SIDESTYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#8C82BC",
}

CONTSTYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div([
        html.H2("Раздел", className="display-4", style={'color': 'white'}),
        html.Hr(style={'color': 'white'}),
            dbc.Nav([
                    dbc.NavLink("Общие показатели", href="/page1", active="exact"),
                    dbc.NavLink("Карта", href="/page2", active="exact")],
                    vertical=False, pills=True),
        ],
        style=SIDESTYLE,
    ),
    html.Div(id="page-content", children=[], style=CONTSTYLE)
])


@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")])
def pagecontent(pathname):
    if pathname == '/page1':
        return [
            html.Div([
                html.H1("Показатели вакансий"),
                html.P("Анализ основных показателей вакансий"),

            ], style={
                'backgroundcolor': 'rgb(140, 130, 188)',
                'padding': '10px 5px'
            }),

            html.Div([
                html.Div([
                    html.Label('Основные показатели'),
                    dcc.Dropdown(
                        id='crossfilter-areas',
                        options=[{'label': item, 'value': item} for item in all_areas],
                        value=['Москва'],
                        multi=True
                    )
                ], style={
                    'width': '48%',
                    'float': 'right',
                    'display': 'inline-block'
                }),

                html.Div([
                    html.Label('Основные показатели'),
                    dcc.RadioItems(
                        options=[
                            {'label': 'Есть тест',
                                'value': 'has_test'},
                            {'label': 'В валюте',
                                'value': 'currency'},
                        ],
                        id='crossfilter-ind',
                        value='area_name',
                        labelStyle={'display': 'inline-block', 'padding': '10px'}
                    )
                ], style={
                    'width': '45%',
                    'float': 'right',
                    'display': 'inline-block'
                    }),
                ], style={
                        'borderBottom': 'thin lightgrey solid',
                        'backgroundColor': 'rgb(250, 250, 250)',
                        'padding': '20px 20px 75px 20px'
                }),
            html.Div(
                dcc.Graph(id='line'),
                style={
                    'width': '70%',
                    'display': 'inline-block'
                    }),
            html.Div(
                dcc.Graph(id='bar'),
                style={
                    'width': '49%',
                    'display': 'inline-block'
                }
            ),
            html.Div(
                dcc.Graph(id='sunburst'),
                style={
                    'width': '49%',
                    'float': 'right',
                    'display': 'inline-block'
                }
            ),
        ]
    elif pathname == "/page2":
        return [
            html.Div(
                children=[
                    html.H1("Показатели зарплат по России на карте"),
                    html.P(
                        "Карта будет разработана позднее"
                    )
                ], style={
                    'backgroundColor': 'rgb(140, 130, 188)',
                    'padding': '10px 5px'
                }),

            html.Div([
                    html.Label('Основные показатели'),
                    dcc.RadioItems(
                        options=[
                            {'label': 'Зарплата от', 'value': 'salary_from'},
                            {'label': 'Зарплата до', 'value': 'salary_to'},
                        ],
                        id='crossfilter-ind1',
                        value='area_name',
                        labelStyle={'display': 'inline-block'}
                    )
                ],
                style={'width': '48%',  'float': 'right', 'display': 'inline-block'}),

            html.Div(
                dcc.Graph(id='choropleth'),
                style={'width': '100%', 'display': 'inline-block'}
            ),
        ]


@callback(
    Output('bar', 'figure'),
    [Input('crossfilter-ind', 'value'),
     Input('crossfilter-areas', 'value')]
)
def update_stacked_area(indication, area):
    currency = 'USD' if indication == 'currency' else 'RUR'
    filtered_data = df[(df['salary_currency'] == currency) & (df['area_name'] != 'Москва') & (df['area_name'] != 'Санкт-Петербург')]
    figure = px.bar(
        filtered_data,
        x='area_name',
        y='salary_from',
        title="Зарплаты по городам, кроме Москвы",
        color='salary_from'
    )
    return figure


@callback(
    Output('line', 'figure'),
    [Input('crossfilter-ind', 'value'),
     Input('crossfilter-areas', 'value')]
)
def update_scatter(indication, area):
    currency = 'RUR'
    indication = 'has_test' if indication == 'area_name' or indication == 'currency' else indication
    filtered_data = df[(df['area_name'] == area[0]) & (df[indication] == True) & (df['salary_currency'] == currency)]
    print(filtered_data)
    figure = px.line(
        filtered_data,
        x="salary_from",
        y="name",
        color="name",
        title="Зарплаты по вакансиям в рублях",
        markers=True,
    )
    return figure


@callback(
    Output('sunburst', 'figure'),
    [Input('crossfilter-ind', 'value'),
     Input('crossfilter-areas', 'value')]
)
def update_sunburst(indication, area):
    filtered_data = df
    figure = px.sunburst(
        filtered_data,
        path=['area_name', 'name'],
        values='salary_from',
        title="Показатели по городам",
    )
    return figure


@callback(
    Output('choropleth', 'figure'),
    Input('crossfilter-ind', 'value')
)
def update_choropleth(indication):
    figure = px.choropleth(
        df,
        # geojson=counties,
        locations=counties,
        # locationmode='Russia',
        color='salary_to',
        hover_name='area_name',
        title='Показатели по городам',
        color_continuous_scale=px.colors.sequential.BuPu,
        # animation_frame='salary_from',
        height=650
    )
    return figure


if __name__ == '__main__':
    app.run_server(debug=True)
