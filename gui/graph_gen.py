import networkx as nx
import matplotlib.pyplot as plt
import json
from networkx.readwrite import json_graph

import jsm.jsm_analysis as jm  # include our tests

# TODO (AP): make a function that will generate html and recieve as input JSM hypothesis, remove all abandoned code
t1 = jm.test2()  # test square

G = nx.Graph()

colors = ['red', 'green', 'pink', 'yellow', 'blue', 'orange']

leng = len(t1)  # count of pairs in hypotheses
lengmass = len(t1[0].value)  # count of reasons

# labeles = []
# dict(labeles)
for i in range(lengmass):
    lab = 'Reas ' + str(i)  # reason's name
    G.add_node(i, x=i + 1, y=i, size=i + 20, label=lab)
    # labeles.append(lab)
last_id = i + 1

mas_edge = []
mas_hyp = []

for i in range(leng):
    for j in range(lengmass):
        if t1[i].value[j] == True:
            lab = 'Hyp ' + str(i)  # Hypotheses name
            hyp_id = last_id + i
            edge_id = j
            G.add_node(hyp_id, x=i, y=i, size=45, label=lab, color='blue')  # add hypotheses
            mas_edge.append(j)
            mas_hyp.append(hyp_id)
            # labeles.append(lab)

s1 = len(mas_edge)
for i in range(s1):
    G.add_edge(mas_hyp[i], mas_edge[i], id=i + 1)

pos = nx.circular_layout(G)

leng = len(G.node)
for i in range(leng):
    x_t = pos[i][0]
    y_t = pos[i][1]
    G.node[i]['x'] = x_t
    G.node[i]['y'] = y_t

d = json_graph.node_link_data(G)
d['edges'] = d['links']
d['links'] = []

json.dump(d, open('data.json', 'w'))
import json

s = json.dumps(d)
print(s)

nx.draw_networkx(G, pos=pos, with_labels=True)
plt.show()

f = open('test.html', 'w')
stroka0 = '''
<html>
<head>
<style type="text/css">
  #container {
    max-width: 500px;
    height: 500px;
    margin: auto;
  }
</style>
</head>
<body>
<br><br>
<p align="center">This place for graph</p>
<div id="container" style="background-color:#DFEAFB"></div>
<script src="sigma.min.js"></script>
<script src="sigma.parsers.json.min.js"></script>
  <textarea id = "myid2" rows="10" cols="45" name="text" style="height:350">
  '''
stroka1 = s
stroka2 = '''
  </textarea>
<p id="result"></p>
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
<p>end</p>
</body>
</html>
'''
f.write(stroka0 + stroka1 + stroka2)
