import json

import networkx as nx
from networkx.readwrite import json_graph
import pandas as pd
from jsm.jsm_analysis import test2


_CODE_TMPL = '*GRAPH_TMPL*'
_BR_TMPL = 'br'


def generate_graph(hypothesis, path, name_reas):
    # TODO: if run 'graph_gen'  change 'tmpl' in code
    # DEFAULT _draw_edges_1()

    # name_reas = hypothesis

    G = nx.Graph()
    # colors = ['green', 'darkred', 'brown', 'yellow', 'blue', 'orange']
    scale = 2  # space near node
    count_line_reas = 3  # point in line reas
    smesh_row = 5  # left margin of next row

    if (isinstance(hypothesis[0], list) == True):
        _draw_nodes2(G, hypothesis, scale, 8, name_reas, count_line_reas, smesh_row)
    else:
        _draw_nodes1(G, hypothesis, scale, 8, name_reas, count_line_reas, smesh_row)


    d = json_graph.node_link_data(G)
    d['edges'] = d['links']
    d['links'] = []
    s = json.dumps(d)

    _generate_cause_html(path, s)
    print(s)


def _generate_cause_html(path, s):
    tmpl = open('gui/templates/cause_template.html')
    # tmpl = open('templates/cause_template.html') # square
    text = tmpl.read()
    # print(text)
    tmpl.close()

    text = text.replace(_CODE_TMPL, s)

    dest = open(path, 'w', encoding='utf-8')
    dest.write(text)
    dest.close()


def _draw_nodes2(G, hypothesis, scale, size_node, name_reas, count_line_reas, smesh_row):
    mas_edge = []
    mas_reas = []
    last_id = 0
    count_node = 0
    x_t, y_t = 1 * scale, 1 * scale

    colors = ['green', 'darkred', 'brown', 'yellow', 'blue', 'orange']
    node_colors = ['darkblue', 'purple', 'gray']
    sel_nod_col = 0  # select color for NODES

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
                    lab = name_reas[j + 1]
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

def _draw_nodes1(G, hypothesis, scale, size_node, name_reas, count_line_reas, smesh_row):
    mas_edge = []
    mas_reas = []
    last_id = 0
    count_node = 0
    x_t, y_t = 1 * scale, 1 * scale

    colors = ['green', 'darkred', 'brown', 'yellow', 'blue', 'orange']
    node_colors = ['darkblue', 'purple', 'gray']
    sel_nod_col = 0  # select color for NODES

    d1 = len(hypothesis)  # count of pairs in hypotheses
    for i in range(d1):
        lengmass = len(hypothesis[i].value)  # count of reasons
        for j in range(lengmass):
            if hypothesis[i].value[j] == True:
                if mas_reas.count(j) > 0:
                    mas_edge.append(mas_edge[j])
                else:
                    mas_edge.append(last_id)
                lab = name_reas[j + 1]
                # lab = 'test'
                if mas_reas.count(j) < 1:
                    if (count_node % count_line_reas == 0) & (j > 0):
                        y_t += 2 * scale
                        x_t = smesh_row + 1 * scale
                    G.add_node(last_id, x=x_t, y=y_t, size=size_node, label=lab,
                               color=node_colors[sel_nod_col])  # add node reas
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
    _draw_edges(G, colors, mas_edge) # next variant of draw grah

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

    _change_node_size(G, mas_edge)

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

    _change_node_size(G, mas_edge)

def _change_node_size(G, mas_edge):


    mas_node_size = []

    for i in range(len(mas_edge)):
        if (mas_edge.count(i) > 0):
            mas_node_size.append(mas_edge.count(i))
            if (mas_node_size[i] >= 10):
                mas_node_size[i] = 10
            if ((mas_node_size[i] < 10) and (mas_node_size[i] >= 2)):
                mas_node_size[i] = 8
            if (mas_node_size[i] < 2):
                mas_node_size[i] = 6

    for i in range(len(mas_node_size)):
        # print(nx.get_node_attributes(G)
        G.node[i]['size'] = mas_node_size[i]
        # print(nx.info(G,i))

    _change_node_color(G, mas_node_size)

def _change_node_color(G, mas_node_size):
    node_color = ['red', 'yellow', 'green']
    for i in range(len(mas_node_size)):
        if (mas_node_size[i] == 10):
            G.node[i]['color'] = node_color[0]
        if (mas_node_size[i] == 8):
            G.node[i]['color'] = node_color[1]
        if (mas_node_size[i] == 6):
            G.node[i]['color'] = node_color[2]


if __name__ == '__main__':

    data = pd.read_csv('../data/ex1.csv', encoding='cp1251', sep=';', index_col=False, na_values='?')
    name_reas = list(data.columns.values)
    print(name_reas)
    hypothesis = test2()

    path = 'templates/res.html'

    generate_graph(hypothesis, path, name_reas)

