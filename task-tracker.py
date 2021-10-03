#!/usr/bin/env python

import sys
import csv
import argparse
import yaml
from datetime import datetime as dt
import pydot


def convert_csv_to_yaml_list(filename):
    keys = []
    datadict = []
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
                datadict.append(r)
                
    # write to yaml file
    yamldata = yaml.dump(datadict, explicit_start=True, default_flow_style=False)
    f = open("tasks.yaml", "w")
    f.write(yamldata) 
    f.close() 

    return datadict
    


if __name__ == "__main__":   

    data = convert_csv_to_yaml_list("tasks.csv")
    
    # dependency chart
    graph = pydot.Dot("my_graph", graph_type="digraph", bgcolor="white")

    for task in data:
        print(task["id"])
        
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
                graph.add_edge(pydot.Edge(dep, task["id"], color="black"))
    
    # write .svg to file
    #output_graphviz_svg = graph.create_svg()
    graph.write_svg("output.svg")
    
    # write .png to file
    graph.write_png("output.png")

    #graph.write_raw("output_raw.dot")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
