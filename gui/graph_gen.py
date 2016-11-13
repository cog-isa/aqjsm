import json

import networkx as nx
from networkx.readwrite import json_graph
import pandas as pd
from jsm.jsm_analysis import test2


_CODE_TMPL = '*GRAPH_TMPL*'
_BR_TMPL = 'br'


def generate_graph(hypothesis, path, name_reas):
    # TODO: make job for hypothesis recieved from aqjsm
    # TODO: fix files square.cfg and ex1.csv

    # name_reas = hypothesis

    G = nx.Graph()
    colors = ['green', 'darkred', 'brown', 'yellow', 'blue', 'orange']
    scale = 3  # space near node

    _draw_nodes(G, hypothesis, scale, 8, name_reas)

    d = json_graph.node_link_data(G)
    d['edges'] = d['links']
    d['links'] = []
    s = json.dumps(d)

    _generate_cause_html(path, s)
    print(s)


def _generate_cause_html(path, s):
    tmpl = open('gui/templates/cause_template.html')
    text = tmpl.read()
    # print(text)
    tmpl.close()

    text = text.replace(_CODE_TMPL, s)

    dest = open(path, 'w', encoding='utf-8')
    dest.write(text)
    dest.close()


def _draw_nodes(G, hypothesis, scale, size_node, name_reas):
    mas_edge = []
    mas_reas = []
    last_id = 0
    count_node = 0
    x_t, y_t = 1 * scale, 1 * scale

    colors = ['green', 'darkred', 'brown', 'yellow', 'blue', 'orange']
    node_colors = ['darkblue', 'purple', 'gray']
    sel_nod_col = 0 # select color for NODES
    count_line_reas = 4  # point in line reas
    smesh_row = 5  # left margin of next row

    d1 = len(hypothesis)  # count of pairs in hypotheses
    for i in range(d1):
        d2 = len(hypothesis[i])
        for k in range(d2):
            lengmass = len(hypothesis[i][k].value)  # count of reasons
            for j in range(lengmass):
                if hypothesis[i][k].value[j] == True:
                    if mas_reas.count(j) > 0:
                        mas_edge.append(mas_edge[j])
                    else:
                        mas_edge.append(last_id)
                    lab = name_reas[j+1]
                    # lab = 'test'
                    if mas_reas.count(j) < 1:
                        if (count_node % count_line_reas == 0) & (j > 0):
                            y_t += 2 * scale
                            x_t = smesh_row + 1 * scale
                        G.add_node(last_id, x=x_t, y=y_t, size=size_node, label=lab, color=node_colors[sel_nod_col])  # add node reas
                        last_id += 1
                        x_t += 1 * scale
                        count_node += 1
                    mas_reas.append(j)
                else:
                    mas_edge.append(None)
            mas_reas.append(None)
        sel_nod_col += 1
        if sel_nod_col > 1:
            sel_nod_col = 0
    num = mas_edge.count(None)
    for i in range(num):
        mas_edge.remove(None)

    for i in range(len(mas_reas)):
        if mas_reas[i] is None:
            mas_edge.insert(i, None)

    _draw_edges_1(G, colors, mas_edge)
    # _draw_edges(G, colors) # next variant of draw grah


def _draw_edges_1(G, colors, mas_edge):
    # mas_edge = []

    select_color = 0
    source = mas_edge[0]
    target = mas_edge[1]
    for i in range(len(mas_edge) - 1):
        if source is None or target is None:
            source = mas_edge[i]
            target = mas_edge[i + 1]
            select_color += 1
            if select_color >= 6:
                select_color=0
        else:
            G.add_edge(source, target, id=i, color=colors[select_color])
            target = mas_edge[i + 1]


def _draw_edges(G, colors, mas_edge):   # posled draw
    # mas_edge = []

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


if __name__ == '__main__':

    data = pd.read_csv('../data/ex1.csv', encoding='cp1251', sep=';', index_col=False, na_values='?')
    name_reas = list(data.columns.values)
    print(name_reas)
    hypothesis = test2()
    print(hypothesis)

    path = 'templates/res.html'

    generate_graph(hypothesis, path, name_reas)

