#!/usr/bin/env python
# coding: utf-8

"""
This app generates visualizations using Dash CytoScape package for CRC networks
"""
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, State, html
import dash_cytoscape as cyto
import pandas as pd


# Styles for network

styles = {
    'container': {
        'position': 'fixed',
        'display': 'flex',
        'flex-direction': 'column',
        'height': '100%',
        'width': '100%'
    },
    'cy-container': {
        'flex': '1',
        'position': 'relative'
    },
    'cytoscape': {
        'position': 'absolute',
        'width': '100%',
        'height': '100%',
        'z-index': 999
    }
}


extraStyle = [   
            # Group selectors
            {
                'selector': 'node',
                'style': {
                    'content': 'data(label)'
                }
            },

            # Group selectors
            {
                'selector': 'edge',
                'style': {
                    'target-arrow-shape': 'vee',
                    'curve-style': 'bezier',
                    #'source-arrow-shape': 'triangle',
                }
            },

            # Class selectors
            {
                'selector': '.red',
                'style': {
                    'background-color': 'red',
                    'line-color': 'red'
                }
            },
            {
                'selector': '.triangle',
                'style': {
                    'shape': 'triangle'
                }
            }
        ]

metaDict = {
    'EN' : 'red triangle',
    'TF' : ''
}


# Functions

def getUniqueNodes(nodeSeries, edgeSeries, metaDict, metaDf):
    
    nodeSet = pd.Series(list(nodeSeries) + list(edgeSeries)).unique()
    typeSet = metaDf[metaDf['node'].isin(nodeSet)]
    typDict = dict(zip(typeSet['node'], typeSet['type']))
    return [
        {
            'data': {'id': short, 'label': label},
            'classes': metaDict[typDict[label]]
        }
        for short, label in ( tuple(zip(nodeSet, nodeSet)))
    ]


def getEdges(nodeSeries, edgeSeries):
    return [
        {'data': {'source': source, 'target': target}}
        for source, target in (tuple(zip(nodeSeries, edgeSeries)))
    ]


def readFile(fname):
    return pd.read_csv(fname)

# Body

logoImageUrl = "https://drive.google.com/uc?export=download&id=1osFeWZEmb2ARVq99inh_vEYTUlfctms_"
flowImageUrl = "https://raw.githubusercontent.com/stjude-biohackathon/KIDS23-Team14/main/images/Workflow.svg"

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP])
server = app.server

logoContent = dbc.CardImg(src=logoImageUrl, style={'height':'10%'}, top=True)

# Sample Data load from csv

fname = "./data/sample.csv"
netInputDf = readFile(fname)

metafn = "./data/nodes.csv"
metaDf = readFile(metafn)

nodes = getUniqueNodes(netInputDf['node'].unique(), netInputDf['edge'], metaDict, metaDf)
edges = getEdges(netInputDf['node'], netInputDf['edge'])
initialElements = nodes + edges

cytoObject = cyto.Cytoscape(
        id='cytoscape-layout-1',
        elements=initialElements,
        stylesheet=extraStyle,
        style={'width': '100%', 'height': '600px'},
        layout={
            'name': 'cose', 'directed' : True,
        }
    )


# Header

header = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.CardImg(
                        src=logoImageUrl,
                        className="img-fluid rounded-start",
                    ),
                    className="col-md-4",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [
                            html.H4("CRCMiner", className="card-title"),
                            html.P(
                                "Putative Core Regulatory Circuitry (CRC) Identification.",
                                className="card-text",
                            ),
                            html.Small(
                                "Team 14",
                                className="card-text text-muted",
                            ),
                        ]
                    ),
                    className="col-md-8",
                ),
            ],
            className="align-items-center w-100",
        ),
        
    ],
    style={"maxWidth": "600px"},
    className="align-items-center w-100 border-0 bg-transparent",
)


## Tab 1


flowCard =   dbc.Card(
            dbc.CardBody(
                [
                    html.H5("Stages in CRC identification", className="card-title"),
                    dbc.CardImg(
                        src=flowImageUrl,
                        className="img-fluid rounded-start",
                    )
                ]
            ),
            className="w-100 mb-3",
        )

useCard = dbc.Card(
                dbc.CardBody(
                [
                    html.P(
                        "Please refer to the GitHub repo for details.",
                    ),
                    dbc.Button(
                        html.I(" GitHub Repo", className="bi bi-github me-2"),
                        href="https://github.com/stjude-biohackathon/KIDS23-Team14",
                        external_link=True,
                        target="_blank",
                        color="info",
                        outline=True,
                    ),
                    
                ]
            ),
            className="w-100 mb-3",
        )

tab1_content = dbc.Card(
    dbc.CardBody(
        [
            dbc.Button(
                "How to Use?", 
                id="use-button",
                className="mb-3",
                color="info",
                n_clicks=0,
            ),
            dbc.Collapse(
                useCard,
                id="collapseUse",
                is_open=True,
            ),

            html.Br(),
            dbc.Button(
                "Overall CRC Identification workflow", 
                id="flow-button",
                className="mb-3",
                color="info",
                n_clicks=0,
            ),

            dbc.Collapse(
                flowCard,
                id="collapseFlow",
                is_open=True,
            ),
        ]
    ),
    className="mt-3",
)

# Tab 2


tab2_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Network visualization:", className="card-text"),
            #dcc.Input(id="input2", type="text", placeholder="Gene", debounce=True),
            dbc.Row([
                dbc.Col(
                    cyto.Cytoscape(
                        id='cytoscape-layout-2',
                        elements=initialElements,
                        stylesheet=extraStyle,
                        style={'width': '100%', 'height': '600px'},
                        layout={
                            'name': 'cose', 'directed' : True,
                        }
                    )
                ),
                dbc.Col([
                    dbc.Badge(
                            "Nodes:", color="info", className="mr-1"
                        ),
                    dcc.Dropdown(
                                    id="nodeDropdown",
                                    options=[
                                        {
                                            "label": i,
                                            "value": i,
                                        }
                                        for i in metaDf['node'].unique()
                                    ],
                                    value=list(metaDf['node'].unique()),
                                    multi=True,
                                    style={"width": "50%"},
                                ),
            ]),

            ]),
            #network2,
        ]
    ),
    className="mt-3",
)


# Tab 3

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Network visualization:", className="card-text"),
            cytoObject,
            #network2,
        ]
    ),
    className="mt-3",
)


# Tab 4

tab4_content = dbc.Card(
    dbc.CardBody(
        [
            html.P("Network visualization:", className="card-text"),
            cytoObject,
            #network2,
        ]
    ),
    className="mt-3",
)


tabs = dbc.Card(
    [
        dbc.CardHeader(
            dbc.Tabs(
                [
                    dbc.Tab(tab1_content, label="Introduction", tab_id="tab-1"),
                    dbc.Tab(tab2_content, label="Network", tab_id="tab-2"),
                    dbc.Tab(tab3_content, label="Clique", tab_id="tab-3"),
                    dbc.Tab(tab4_content, label="GO", tab_id="tab-4"),
                ],
                id="tabs",
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(html.P(id="card-content", className="card-text")),
    ],
    style={'height':'100vh'}
)

# Tab 3


# App layout

app.layout = html.Div(
    [
        #hpage,
        dbc.Row(
                dbc.Col(header, width=12),
        ),
        dbc.Row(
            dbc.Col(tabs),
        ),
        #tabs
    ]
)


@app.callback(
    Output("cytoscape-layout-2", "elements"),
    [
        Input("nodeDropdown", "value"),
    ],
)
def filter_nodes(selectNodes):
    # Generate node list
    filterDf = netInputDf[netInputDf['node'].isin(selectNodes)]
    subNodes = getUniqueNodes(filterDf['node'].unique(), filterDf['edge'], metaDict, metaDf)
    subEdges = getEdges(filterDf['node'], filterDf['edge'])
    return subNodes + subEdges


@app.callback(
    Output("collapseFlow", "is_open"),
    [Input("flow-button", "n_clicks")],
    [State("collapseFlow", "is_open")],
)
def toggle_collapse(n, is_open):
    return not is_open if n else is_open


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
    