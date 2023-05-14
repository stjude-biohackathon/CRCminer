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
import plotly.express as px


# Styles for network

styles = {
    "container": {
        "position": "fixed",
        "display": "flex",
        "flex-direction": "column",
        "height": "100%",
        "width": "100%",
    },
    "cy-container": {"flex": "1", "position": "relative"},
    "cytoscape": {
        "position": "absolute",
        "width": "100%",
        "height": "100%",
        "z-index": 999,
    },
}


extraStyle = [
    # Group selectors
    {"selector": "node", "style": {"content": "data(label)"}},
    # Group selectors
    {
        "selector": "edge",
        "style": {
            "target-arrow-shape": "vee",
            "curve-style": "bezier",
            #'source-arrow-shape': 'triangle',
        },
    },
    # Class selectors
    {"selector": ".red", "style": {"background-color": "red", "line-color": "red"}},
    {"selector": ".triangle", "style": {"shape": "triangle"}},
]

metaDict = {"EN": "red triangle", "TF": ""}


# Functions


def getUniqueNodes(nodeSeries, edgeSeries, metaDict, metaDf):
    nodeSet = pd.Series(list(nodeSeries) + list(edgeSeries)).unique()
    typeSet = metaDf[metaDf["node"].isin(nodeSet)]
    typDict = dict(zip(typeSet["node"], typeSet["type"]))
    return [
        {"data": {"id": short, "label": label}, "classes": metaDict[typDict[label]]}
        for short, label in (tuple(zip(nodeSet, nodeSet)))
    ]


def getEdges(nodeSeries, edgeSeries):
    return [
        {"data": {"source": source, "target": target}}
        for source, target in (tuple(zip(nodeSeries, edgeSeries)))
    ]


def readFile(fname):
    return pd.read_csv(fname)


# Body


# logoImageUrl = "https://drive.google.com/uc?export=download&id=1osFeWZEmb2ARVq99inh_vEYTUlfctms_"
flowImageUrl = "https://raw.githubusercontent.com/stjude-biohackathon/KIDS23-Team14/main/images/Workflow.svg"

app = dash.Dash(external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP])
server = app.server
logoImageUrl = app.get_asset_url("logo1.png")
logoContent = dbc.CardImg(src=logoImageUrl, style={"height": "10%"}, top=True)

# Sample Data load from csv
sampleA = pd.read_csv("./data/group1_degreeTable.txt", sep=",").sort_values(
    by="TF_CliqueFraction", ascending=False
)
sampleB = pd.read_csv("./data/group2_degreeTable.txt", sep=",").sort_values(
    by="TF_CliqueFraction", ascending=False
)

fname = "./data/sample_2.csv"
# fname = "./data/group1_EdgeTable.txt"
netInputDf = readFile(fname)

metafn = "./data/nodes_2.csv"
# metafn = "./data/group1_degreeTable.txt"
metaDf = readFile(metafn)

# cliqueFn = "./data/TF_Degrees.csv"
# cliqueDf = pd.read_csv(cliqueFn).sort_values(by = 'TF_CliqueFraction', ascending=False)
cliquePlot = px.bar(
    data_frame=sampleA.loc[sampleA["TF_CliqueFraction"] > 0.1],
    x="TF",
    y="TF_CliqueFraction",
)
cliquePlot.update_layout(xaxis=dict(tickfont=dict(size=14)))

nodes = getUniqueNodes(
    netInputDf["node"].unique(), netInputDf["edge"], metaDict, metaDf
)
edges = getEdges(netInputDf["node"], netInputDf["edge"])

initialElements = nodes + edges

cytoObject = cyto.Cytoscape(
    id="cytoscape-layout-1",
    elements=initialElements,
    stylesheet=extraStyle,
    style={"width": "100%", "height": "600px"},
    layout={
        "name": "cose",
        "directed": True,
    },
)

# Group comparison

groupData = pd.merge(sampleA, sampleB, on="TF", how="left").fillna(0)

groupData["deltaInDegree"] = groupData["In_x"] - groupData["In_y"]
groupData["deltaOutDegree"] = groupData["Out_x"] - groupData["Out_y"]

fig = px.scatter(
    data_frame=groupData,
    x="deltaOutDegree",
    y="deltaInDegree",
    labels={
        "deltaOutDegree": "deltaOutDegree (group1 OUT - group2 OUT degree)",
        "deltaInDegree": "deltaInDegree (group1 IN - group1 IN degree)",
    },
    hover_data=groupData,
)

fig.add_hline(y=0)
fig.add_vline(x=0)
fig.update_traces(
    marker=dict(size=10, line=dict(width=2, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)


fig_CF = px.scatter(
    data_frame=groupData,
    x="TF_CliqueFraction_x",
    y="TF_CliqueFraction_y",
    labels={
        "TF_CliqueFraction_x": "TF Clique Fraction in group 1",
        "TF_CliqueFraction_y": "TF Clique Fraction in group 2",
    },
    hover_data=groupData,
)

fig_CF.add_hline(y=0)
fig_CF.add_vline(x=0)
fig_CF.update_traces(
    marker=dict(size=10, color="#ce6c17", line=dict(width=2, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
)


fig_In = px.scatter(data_frame=sampleA, x="In", y="Out", hover_data=sampleA)

fig_In.add_hline(y=0)
fig_In.add_vline(x=0)
fig_In.update_traces(
    marker=dict(size=10, color="#e2dd25", line=dict(width=2, color="DarkSlateGrey")),
    selector=dict(mode="markers"),
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


flowCard = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Stages in CRC identification", className="card-title"),
            dbc.Row(
                [
                    dbc.Col(
                        dbc.CardImg(
                            src=flowImageUrl,
                            className="img-fluid rounded-start",
                            style={"height": "85%", "width": "85%"},
                        ),
                        className="justify-content-center align-items-center",
                    )
                ]
            ),
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
            html.H5("Network visualization:", className="card-text"),
            # dcc.Input(id="input2", type="text", placeholder="Gene", debounce=True),
            html.I(" Enhancer", className="bi bi-triangle-fill me-2"),
            html.I(" Transcription factor", className="bi bi-circle-fill me-2"),
            dbc.Row(
                [
                    dbc.Col(
                        cyto.Cytoscape(
                            id="cytoscape-layout-2",
                            elements=initialElements,
                            stylesheet=extraStyle,
                            style={"width": "100%", "height": "600px"},
                            layout={
                                "name": "cose",
                                "directed": True,
                            },
                        ),
                        width=8,
                    ),
                    dbc.Col(
                        [
                            dbc.Badge("In Degree >=:", color="info", className="mr-1"),
                            dcc.Dropdown(
                                id="inDegree",
                                options=[
                                    {"label": k, "value": k}
                                    for k in range(
                                        metaDf["In"].min(), metaDf["In"].max()
                                    )
                                ],
                                clearable=False,
                                value=metaDf["In"].min(),
                                style={"width": "80px"},
                            ),
                            dbc.Badge("Out Degree >=:", color="info", className="mr-1"),
                            dcc.Dropdown(
                                id="outDegree",
                                options=[
                                    {"label": k, "value": k}
                                    for k in range(
                                        metaDf["Out"].min(), metaDf["Out"].max()
                                    )
                                ],
                                clearable=False,
                                value=metaDf["Out"].min(),
                                style={"width": "80px"},
                            ),
                            dbc.Badge("Nodes:", color="info", className="mr-1"),
                            dcc.Dropdown(
                                id="nodeDropdown",
                                options=[
                                    {
                                        "label": i,
                                        "value": i,
                                    }
                                    for i in metaDf["node"].unique()
                                ],
                                value=list(metaDf["node"].unique()),
                                multi=True,
                                style={"width": "80%"},
                            ),
                            dbc.Badge("Edge color:", color="info", className="mr-1"),
                            dcc.Input(id="input-edge-color", type="text"),
                            html.Br(),
                            dbc.Badge("Node color:", color="info", className="mr-1"),
                            dcc.Input(id="input-node-color", type="text"),
                            html.Br(),
                            dbc.Badge("Layout:", color="info", className="mr-1"),
                            dcc.Dropdown(
                                id="dropdown-update-layout",
                                value="cose",
                                clearable=False,
                                options=[
                                    {"label": name.capitalize(), "value": name}
                                    for name in [
                                        "grid",
                                        "random",
                                        "circle",
                                        "cose",
                                        "concentric",
                                    ]
                                ],
                            ),
                        ]
                    ),
                ]
            ),
            # network2,
        ]
    ),
    className="mt-3",
)


# Tab 3

tab3_content = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Clique fraction plot: ", className="card-text"),
            dcc.Graph(
                figure=cliquePlot,
                responsive=True,
                style={"display": "inline-block", "width": "50%"},
            ),
            dcc.Graph(
                figure=fig_In,
                responsive=True,
                style={"display": "inline-block", "width": "50%"},
            ),
            # network2,
        ]
    ),
    className="mt-3",
)


# Tab 4

tab4_content = dbc.Card(
    dbc.CardBody(
        [
            html.H5("Group comparison plot:", className="card-text"),
            dcc.Graph(
                figure=fig,
                responsive=False,
                style={"display": "inline-block", "width": "50%"},
            ),
            dcc.Graph(
                figure=fig_CF,
                responsive=False,
                style={"display": "inline-block", "width": "50%"},
            ),
            # network2,
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
                    dbc.Tab(tab3_content, label="Putative CRC TFs", tab_id="tab-3"),
                    dbc.Tab(tab4_content, label="Group Comparison", tab_id="tab-4"),
                ],
                id="tabs",
                active_tab="tab-1",
            )
        ),
        dbc.CardBody(html.P(id="card-content", className="card-text")),
    ],
    style={"height": "100vh"},
)

# Tab 3


# App layout

app.layout = html.Div(
    [
        # hpage,
        dbc.Row(
            dbc.Col(header, width=12),
        ),
        dbc.Row(
            dbc.Col(tabs),
        ),
        # tabs
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
    filterDf = netInputDf[netInputDf["node"].isin(selectNodes)]
    subNodes = getUniqueNodes(
        filterDf["node"].unique(), filterDf["edge"], metaDict, metaDf
    )
    subEdges = getEdges(filterDf["node"], filterDf["edge"])
    return subNodes + subEdges


@app.callback(
    Output("nodeDropdown", "options"),
    Output("nodeDropdown", "value"),
    [
        Input("inDegree", "value"),
        Input("outDegree", "value"),
    ],
)
def filter_nodes(inputDegree, outputDegree):
    # Generate node list
    genes = list(
        metaDf.loc[
            (metaDf["In"] >= inputDegree) & (metaDf["Out"] >= outputDegree), "node"
        ]
    )
    dropOptions = [
        {
            "label": i,
            "value": i,
        }
        for i in genes
    ]
    return dropOptions, genes


@app.callback(
    Output("cytoscape-layout-2", "layout"), Input("dropdown-update-layout", "value")
)
def update_layout(layout):
    return {"name": layout, "directed": True, "animate": True}


@app.callback(
    Output("cytoscape-layout-2", "stylesheet"),
    Input("input-edge-color", "value"),
    Input("input-node-color", "value"),
)
def update_stylesheet(line_color, bg_color):
    if line_color is None:
        line_color = "gray"

    if bg_color is None:
        bg_color = "gray"

    new_styles = [
        {"selector": "node", "style": {"background-color": bg_color}},
        {"selector": "edge", "style": {"line-color": line_color}},
    ]

    return extraStyle + new_styles


@app.callback(
    Output("collapseFlow", "is_open"),
    [Input("flow-button", "n_clicks")],
    [State("collapseFlow", "is_open")],
)
def toggle_collapse(n, is_open):
    return not is_open if n else is_open


if __name__ == "__main__":
    app.run_server(port=8888, debug=True)
