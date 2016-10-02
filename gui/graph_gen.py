import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import json
from networkx.readwrite import json_graph

import jsm.jsm_analysis as jm  # include our tests

def writeHtml():
    br = '<br>'
    f = open('test.html', 'w', encoding='utf-8')
    str1 = '''
    <html>
    <head>
    <meta charset="Utf-8">
      <style type="text/css">
      #container {
        min-width: 600px;
        min-height: 600px;
        margin-left: 5%;
        background-color:#DFEAFB;
      }
      #bigtable {
        background-color: gray;
      }
      #lefttext {
        background-color:#FFC3C3;
      }

    </style>
    </head>
    <body>
      <table id="bigtable" border="2" align="center">
      <tr>
        <td style="min-width:200px; width:15%; background-color:#F7EC8D";><div></div>
      <p id="result"><b>*** Empty place ***<br></b>
      </td>
      <td style="width:80%; background-color:#A7FBA9;">
          <div id="container"></div>
      </td>

      <td style="min-width:200px; width:25%";>
      <div style="background-color:#8B98F9">
        <b>*** Empty place ***</b><br>

      </div>
        <div id="lefttext">
        <b>*** Empty place ***</b><br>
         </div>
      </td>
        </tr>
        <tr style="height: 50%">
          <td colspan="3" align="center" style="background-color: #FFECEC">LOOOG!!</td>
        </tr>
      </table>
      <script src="sigma.js"></script>
      <script src="sigma.parsers.json.min.js"></script>
      <div id = "myid2" name="text" style="height:1px; width: 100%; visibility:hidden;">
      '''
    str2 = s
    str3 = '''
      </div>'''

    str4 = '''
      <script>
       var x = document.getElementById("myid2").innerHTML;
      // document.getElementById("result").innerHTML = x;
        // console.log(x)
    graph = JSON.parse(x)
    s = new sigma({
            renderer: {
              container: 'container',
              type: 'canvas'
        },
            settings: {
                defaultNodeColor: '#ec5148'
            }
    });
    s.graph.clear();
    s.graph.read(graph);
    s.refresh()
    console.log(s)
    </script>
      <p align="center">end &copy;</p>
    </body>
    </html>

    '''
    f.write(str1 + str2 + str3 + str4)

def old_draw():
    leng = len(t1)  # count of pairs in hypotheses
    lengmass = len(t1[0].value)  # count of reasons
    count_line_prop = 3  # point in line prop
    count_line_reas = 2  # point in line reas
    smesh_row = 0  # left margin of next row
    scale = 1  # space near node

    count_node = 0
    x_t = 1 * scale
    y_t = 1 * scale

    mas_edge = []
    mas_reas = []
    mas_prop = []
    mas_link = []

    select_color = 0
    save_reas = ''''''
    last_id = 0
    name = 0

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
                    print(last_id, "\t", lab)
                    last_id += 1
                    x_t += 1 * scale
                    count_node += 1
                mas_reas.append(j)
            else:
                mas_edge.append(None)
        save_reas += '<br>'
        mas_reas.append(None)

    num = mas_edge.count(None)
    for i in range(num):
        mas_edge.remove(None)

    count_node = 0
    x_t = 1 * scale
    y_t = 1 * scale

    for i in range(leng):
        if (count_node % count_line_prop == 0) & (i > 0):
            y_t += 1 * scale
            x_t = smesh_row + 1 * scale
        lab = 'Свой-во ' + str(i)  # Prooertise name
        # G.add_node(last_id, x=x_t, y=y_t, size=size_node, label=lab, color=colors[select_color])  # add node reas
        mas_prop.append(last_id)
        x_t += 1 * scale
        last_id += 1
        select_color += 1
        count_node += 1

    print('reas:   ', mas_reas)
    print('edge:   ', mas_edge)
    print('prop:   ', mas_prop)

    step_prop = 0
    num = mas_edge[0]
    select_color = 0

    for i in range(len(mas_edge)):
        if mas_edge[i] < num:
            step_prop += 1
            select_color += 1
            # G.add_edge(mas_prop[step_prop], mas_edge[i], id=i, color=colors[select_color])
            print('m: ', mas_edge[i])
        else:
            # G.add_edge(mas_prop[step_prop], mas_edge[i], id=i, color=colors[select_color])
            print('m: ', mas_edge[i])

        num = mas_edge[i]

def obsh_draw(colors):

        select_color = 0
        source = mas_edge[0]
        target = mas_edge[1]
        for i in range(len(mas_edge) - 1):

            if source == None or target == None:
                source = mas_edge[i]
                target = mas_edge[i + 1]
                select_color += 1
            else:
                G.add_edge(source, target, id=i, color=colors[select_color])
                target = mas_edge[i + 1]

def posled_draw():

        select_color = 0
        source = mas_edge[0]
        target = mas_edge[1]
        for i in range(len(mas_edge) - 2):

            if source == None or target == None:
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
# posled_draw() # next variant of draw grah
obsh_draw(colors=colors)

d = json_graph.node_link_data(G)
d['edges'] = d['links']
d['links'] = []
json.dump(d, open('data.json', 'w'))
s = json.dumps(d)
# print(s)




from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("test_template.html",
                           left1='taken from main.py',
                           right1='right1',
                           right2='right2',
                           graph=s,
                           variable1="change!!!!")

if __name__ == "__main__":
    app.run(debug=True)



writeHtml()








# pos = nx.circular_layout(G)
# nx.draw_networkx(G, pos=pos, with_labels=True)
# plt.show()

