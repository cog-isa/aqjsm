import json

import networkx as nx
import pandas as pd
from networkx.readwrite import json_graph

import jsm.jsm_analysis as jm  # include our tests
from html_generator import generate_cause_html


def draw_edges_colored(colors):
    select_color = 0
    source = mas_edge[0]
    target = mas_edge[1]
    for i in range(len(mas_edge) - 1):
        if source is None or target is None:
            source = mas_edge[i]
            target = mas_edge[i + 1]
            select_color += 1
        else:
            G.add_edge(source, target, id=i, color=colors[select_color])
            target = mas_edge[i + 1]


def draw_edges():
    select_color = 0
    source = mas_edge[0]
    target = mas_edge[1]
    for i in range(len(mas_edge) - 2):

        if source is None or target is None:
            source = mas_edge[i + 1]
            target = mas_edge[i + 2]
            select_color += 1
        else:
            G.add_edge(source, target, id=i, color=colors[select_color])
            source = mas_edge[i + 1]
            target = mas_edge[i + 2]


def draw_nodes(last_id, x_t, y_t, count_node, size_node):
    leng = len(t1)  # count of pairs in hypotheses
    lengmass = len(t1[0].value)  # count of reasons
    for i in range(leng):
        for j in range(lengmass):
            if t1[i].value[j] == True:
                if mas_reas.count(j) > 0:
                    mas_edge.append(mas_edge[j])
                else:
                    mas_edge.append(last_id)
                lab = names_reas[j + 1]  # Reasons name   from data_frame
                if mas_reas.count(j) < 1:
                    if (count_node % count_line_reas == 0) & (j > 0):
                        y_t += 2 * scale
                        x_t = smesh_row + 1 * scale
                    G.add_node(last_id, x=x_t, y=y_t, size=size_node, label=lab, color='darkred')  # add node reas
                    last_id += 1
                    x_t += 1 * scale
                    count_node += 1
                mas_reas.append(j)
            else:
                mas_edge.append(None)
        mas_reas.append(None)

    num = mas_edge.count(None)
    for i in range(num):
        mas_edge.remove(None)

    for i in range(len(mas_reas)):
        if mas_reas[i] == None:
            mas_edge.insert(i, None)


if __name__ == '__main__':
    t1 = jm.test2()  # test square

    data = pd.read_csv('ex1.csv', encoding='cp1251', sep=';', index_col=False, na_values='?')
    names_reas = list(data.columns.values)

    G = nx.Graph()
    colors = ['green', 'darkred', 'brown', 'yellow', 'blue', 'orange']
    size_node = 8

    # Parametres
    count_line_prop = 3  # point in line prop
    count_line_reas = 2  # point in line reas
    smesh_row = 0  # left margin of next row
    scale = 1  # space near node
    last_id = 0

    count_node = 0
    x_t = 1 * scale
    y_t = 1 * scale

    mas_edge = []
    mas_reas = []
    mas_prop = []

    draw_nodes(last_id=last_id, x_t=x_t, y_t=y_t, count_node=count_node, size_node=size_node)
    # draw_edges() # next variant of draw grah
    draw_edges_colored(colors=colors)

    d = json_graph.node_link_data(G)
    d['edges'] = d['links']
    d['links'] = []
    s = json.dumps(d)

    generate_cause_html(s)
