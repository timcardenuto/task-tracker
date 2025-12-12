#!/usr/bin/env python

import sys
import csv
import argparse
import yaml
from datetime import datetime as dt
import pydot

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
from dash import dash_table
import pandas as pd


_datafile = "tasks.csv"
_datadictlist = {}


def fix_dependencies(rows):
    print("fix_dependencies(rows)")
    for row in rows:
        if row['dependencies'] is not None:
            row['dependencies'] = list(row['dependencies'].split(";"))
    return rows


def convert_csv_to_data(filename):
    print("convert_csv_to_data("+str(filename)+")")

    keys = []
    datadictlist = []
    firstline = True
    with open(filename, "r") as stream:
        data = csv.reader(stream)

        for row in data:
            if firstline:
                keys = row
                firstline = False
            else:
                # will convert everything without knowing the keys but then every value is a string, the data type won't be right
                #r = {}
                #for i in range(len(keys)):
                #    r[keys[i]] = row[i]

                deps = list(row[7].split(";")) if row[7] != '' else []
                r = {"id": int(row[0]),
                    "title": str(row[1]),
                    "assignee": str(row[2]),
                    "priority": int(row[3]),
                    "estimate": int(row[4]),
                    "start": dt.strptime(row[5], "%Y-%m-%d"),
                    "end": dt.strptime(row[6], "%Y-%m-%d"),
                    "dependencies": deps,
                    "status": str(row[8]),
                    "description": str(row[9])
                    }

                #print(r)
                datadictlist.append(r)

    return datadictlist


def convert_data_to_yaml(datadictlist):
    print("convert_data_to_yaml(datadictlist)")
    yamldata = yaml.dump(datadictlist, explicit_start=True, default_flow_style=False)
    f = open("tasks.yaml", "w")
    f.write(yamldata)
    f.close()


def updateGraph(datadictlist):
    print("updateGraph(datadictlist)")

    # dependency chart
    graph = pydot.Dot("my_graph", graph_type="digraph", bgcolor="white")

    for task in datadictlist:
        print("id: "+str(task["id"]))
        # TODO add some kind of wordwrap for the HTML label so it's reasonably sized with large descriptions. Also then it can maybe fit in a circle
        color = "darkgreen" if task["status"] == "done" else "red"
        label = '<<table border="0" cellborder="0" cellspacing="1">\
                <tr><td align="left"><b>'+task["title"]+'</b></td></tr>\
                 <tr><td align="left">'+task["description"]+'</td></tr>\
                 <tr><td align="left"><font color="'+color+'">'+task["status"]+'</font></td></tr>\
               </table>>'

        graph.add_node(pydot.Node(task["id"], label=label, shape="rectangle"))

        if task["dependencies"]:
            for dep in task["dependencies"]:
                print("    |-- "+dep)
                graph.add_edge(pydot.Edge(dep, task["id"], color="black"))

    # write .svg to file
    #graph.write_svg("/assets/graph.svg")
    #graphimg = graph.create_svg()

    # write .png to file
    graph.write_png("assets/graph.png")



def updateTable(datafile):
    print("updateTable("+datafile+")")
    df = pd.read_csv(datafile)
    return df






########### Dash web stuff ###########

# initialize app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, title='Remind Me', external_stylesheets=external_stylesheets)


# assemble the components on the webpage
app.layout = html.Div(
    style={
        'height': '100%',
        #'height': '100%',
        'backgroundColor': 'whitesmoke',
        #'background-image': 'url(/assets/image.jpg)',
    },
    children=[
        html.H1(children='Remind Me',
            #style={'background-image': 'url(https://upload.wikimedia.org/wikipedia/commons/2/22/North_Star_-_invitation_background.png)', 'height': '100%'}
            #style={'background-image': 'url(/assets/image.jpg)', 'height': '100%'}
            #style={'background-color': 'blue'}
        ),

        # TODO user assigns factboxes to the category - what you subjectively think represents that category
        html.Div(children=[
            html.Button('Load', id='load-button', style={'marginLeft': '10px', 'marginRight': '20px', 'boxShadow': '1px 2px 6px #888888'}),
            dcc.Input(id='load-input', value="tasks.csv", type='text')
            ]),

        html.Div(children=[
            html.Button('Save', id='save-button', style={'marginLeft': '10px', 'marginRight': '20px', 'boxShadow': '1px 2px 6px #888888'}),
            dcc.Input(id='save-input', value="tasks.json", type='text')
            ]),



        html.Div(children='Dependency Graph:', style={'marginTop': '20px', 'marginBottom': '20px', 'marginLeft': '10px'}),

        html.Img(id='graph-image', src=app.get_asset_url('graph.png'), style={'width':'100%'}),

        html.Div(children='Data Table:', style={'marginBottom': '20px', 'marginLeft': '10px'}),

        html.Div(children=[
            #html.Div(id='table-container', style={'marginTop': '20px', 'marginBottom': '20px', 'marginLeft': '10px'}, children=dash_table.DataTable(id='task-table')),
            #html.Div(id='detail-container', style={'borderCollapse': 'seperate', 'borderSpacing': '20px 5px'}),
            #html.Div(id='table-container'),
            #html.Div(id='detail-container')
            html.Div(id='table-container', style={'color': 'black', 'textAlign': 'left', 'borderRadius': '5px', 'boxShadow': '0px 2px 6px #888888', 'padding': '10px', 'display': 'table-cell', 'width': '75%'}, children=dash_table.DataTable(id='task-table')),
            html.Div(id='detail-container', style={'color': 'black', 'textAlign': 'left', 'borderRadius': '5px', 'boxShadow': '1px 2px 6px #888888', 'padding': '10px', 'display': 'table-cell', 'width': '600px'}, children=[
                html.Div(children=[
                    html.Div(children="Title", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        children=dcc.Input(id='row-title', type='text', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':' 80%'})
                    ]),
                html.Div(children=[
                    html.Div(children="Assignee", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Dropdown(id='row-assignee', options=[{'label': 'person1', 'value': 'person1'},{'label': 'person2', 'value': 'person2'},{'label': 'person3', 'value': 'person3'},{'label': 'person4', 'value': 'person4'}], style={'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Priority", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Input(id='row-priority', type='number', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Estimate", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Input(id='row-estimate', type='number', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Start Date", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.DatePickerSingle(id='row-start', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="End Date", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.DatePickerSingle(id='row-end', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Dependencies", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Dropdown(id='row-dependencies', multi=True, options=[{'label': '1', 'value': '1'},{'label': '2', 'value': '2'},{'label': '3', 'value': '3'},{'label': '4', 'value': '4'},{'label': '5', 'value': '5'}], style={'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Status", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Dropdown(id='row-status', options=[{'label': 'done', 'value': 'done'},{'label': 'todo', 'value': 'todo'}], style={'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Description", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Input(id='row-description', type='text', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'})
                    ]),
            ]),
        ]),
        html.Div(id='invisible')

    ])


#@app.callback(
#    Output('graph-image', 'src'),
#    [Input('load-button', 'n_clicks')],
#    [State('load-input', 'value')])
#def update_graph(clicks, filename):
#    print("### update_graph()")
#    datadictlist = convert_csv_to_data(datafile)
#    updateGraph(datadictlist)
#    return app.get_asset_url('graph.png')


""" Loads the specified data file into the table display when the Load button is clicked """
@app.callback(
    Output('table-container', 'children'),
    [Input('load-button', 'n_clicks')],
    [State('load-input', 'value')])
def update_table(clicks, filename):
    global _datadictlist
    print("### update_table()")
    # TODO if .csv then use this function, else if .yaml use different, etc.
    _datadictlist = convert_csv_to_data(filename)
    table = updateTable(filename)
    columns = [{"name": i, "id": i} for i in table.columns]
    data = table.to_dict('records')
    return dash_table.DataTable(id='task-table', columns=columns, data=data, editable=True)


""" Save the current table state into a file when the Save button is clicked """
# TODO how to save as csv?
@app.callback(
    Output('invisible', 'children'),
    [Input('save-button', 'n_clicks')],
    [State('save-input', 'value')])
def save_table(clicks, filename):
    print("### save_table()")
    f = open(filename, "w")
    f.write(yaml.dump(_datadictlist, explicit_start=True, default_flow_style=False))
    f.close()

""" Display detailed view of a single row in the data table """
@app.callback(
    Output('detail-container', 'children'),
    Input('task-table', 'active_cell'))
def update_data(active_cell):
    print("### update_data()")
    if active_cell is not None:
        row = _datadictlist[active_cell['row']]

        return [
                html.Div(children=[
                    html.Div(children="Title", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        children=dcc.Input(id='row-title', value=row['title'], type='text', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':' 80%'})
                    ]),
                html.Div(children=[
                    html.Div(children="Assignee", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Dropdown(id='row-assignee', value=row['assignee'], options=[{'label': 'person1', 'value': 'person1'},{'label': 'person2', 'value': 'person2'},{'label': 'person3', 'value': 'person3'},{'label': 'person4', 'value': 'person4'}], style={'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Priority", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Input(id='row-priority', value=row['priority'], type='number', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Estimate", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Input(id='row-estimate', value=row['estimate'], type='number', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Start Date", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.DatePickerSingle(id='row-start', date=row['start'], style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="End Date", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.DatePickerSingle(id='row-end', date=row['end'], style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Dependencies", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Dropdown(id='row-dependencies', value=row['dependencies'], multi=True, options=[{'label': '1', 'value': '1'},{'label': '2', 'value': '2'},{'label': '3', 'value': '3'},{'label': '4', 'value': '4'},{'label': '5', 'value': '5'}], style={'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Status", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Dropdown(id='row-status', value=row['status'], options=[{'label': 'done', 'value': 'done'},{'label': 'todo', 'value': 'todo'}], style={'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'}),
                    ]),
                html.Div(children=[
                    html.Div(children="Description", style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width':'100px'}),
                    html.Div(
                        dcc.Input(id='row-description', value=row['description'], type='text', style={'display':'table-cell', 'width':'100%'}),
                        style={'color':'black', 'textAlign':'left', 'borderRadius':'5px', 'padding':'10px', 'display':'table-cell', 'width': '80%'})
                    ]),
                ]



""" Updates the graph image based on the live data table """
# @app.callback(
#     Output('task-table', 'data'),
#     Input('row-dependencies', 'value'),
#     Input('row-status', 'value'),
#     )
# def change_table(deps, status):
#     print("### change_table()")
#     print(deps)
#     print(status)
#
#     return _datadictlist


""" Updates the graph image based on the live data table """
@app.callback(
    Output('graph-image', 'src'),
    Input('task-table', 'data'),
    Input('task-table', 'columns'))
def change_image(rows, columns):
    global _datadictlist
    print("### change_image()")
    if rows is not None:
        # I need this because I have to parse/split the dependencies syntax
        _datadictlist = fix_dependencies(rows)

        # update the graph image on disk and tell Dash to load it
        updateGraph(_datadictlist)
        return app.get_asset_url('graph.png')





if __name__ == "__main__":
    app.run(debug=True)
