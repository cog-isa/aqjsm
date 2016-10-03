import json

import networkx as nx
from networkx.readwrite import json_graph

_CODE_TMPL = '*GRAPH_TMPL*'
_BR_TMPL = 'br'


def generate_graph(hypothesis, path):
    # TODO: make job for hypothesis recieved from aqjsm
    # TODO: fix files square.cfg and ex1.csv
    G = nx.Graph()
    colors = ['green', 'darkred', 'brown', 'yellow', 'blue', 'orange']
    scale = 1  # space near node

    _draw_nodes(G, hypothesis, scale, 8)
    # _draw_edges(G, colors) # next variant of draw grah
    _draw_edges_1(G, colors)

    d = json_graph.node_link_data(G)
    d['edges'] = d['links']
    d['links'] = []
    s = json.dumps(d)

    _generate_cause_html(path, s)


def _generate_cause_html(path, s):
    tmpl = open('templates/cause_template.html')
    text = tmpl.read()
    tmpl.close()

    text = text.replace(_CODE_TMPL, s)

    dest = open(path, 'w', encoding='utf-8')
    dest.write(text)
    dest.close()


def _draw_edges_1(G, colors):
    mas_edge = []

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


def _draw_edges(G, colors):
    mas_edge = []

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


def _draw_nodes(G, hypothesis, scale, size_node):
    mas_edge = []
    mas_reas = []
    last_id = 0
    count_node = 0
    x_t, y_t = 1 * scale, 1 * scale

    leng = len(hypothesis)  # count of pairs in hypotheses
    count_line_reas = 2  # point in line reas
    smesh_row = 0  # left margin of next row

    lengmass = len(hypothesis[0].value)  # count of reasons
    for i in range(leng):
        for j in range(lengmass):
            if hypothesis[i].value[j] == True:
                if mas_reas.count(j) > 0:
                    mas_edge.append(mas_edge[j])
                else:
                    mas_edge.append(last_id)
                lab = hypothesis[j + 1]  # Reasons name   from data_frame
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
        if mas_reas[i] is None:
            mas_edge.insert(i, None)
