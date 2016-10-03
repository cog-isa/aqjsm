import networkx as nx
import matplotlib.pyplot as plt
import json
from networkx.readwrite import json_graph

import jsm.jsm_analysis as jm  # include our tests



# t1 = jm.test1()
t1 = jm.test2()  # test square

reasons_square = []
propetis = []

r0 =' есть центр симметрии '
r1 =' есть ось симметрии '
r2 =' есть ось симметрии, которая является диагональю '
r3 =' есть ось симметрии, не являющаяся диагональю '
r4 =' ровно один поворот на 180⁰ переводит фигуру в себя '
r5 =' порядок группы симметрий равен двум '
r6 =' есть пара противолежащих прямых углов '
r7 =' нет прямого угла '
r8 =' нет оси симметрии или любая ось симметрии является диагональю '
s0 = ' описать окружность'
s1 = ' test 1'
s2 = ' test 2'


reasons_square.append(r0)
reasons_square.append(r1)
reasons_square.append(r2)
reasons_square.append(r3)
reasons_square.append(r4)
reasons_square.append(r5)
reasons_square.append(r6)
reasons_square.append(r7)
reasons_square.append(r8)
propetis.append(s0)
propetis.append(s1)
propetis.append(s2)

br = '<br>'

G = nx.Graph()

colors = ['gray', 'green', 'pink', 'yellow', 'blue', 'orange']

leng=len(t1) # count of pairs in hypotheses
lengmass=len(t1[0].value) # count of reasons


# labeles = []
# dict(labeles)
for i in range(lengmass):
    lab = 'Reas '+str(i) # reason's name
    G.add_node(i,x=i+1, y=i, size=i+20, label=lab)
    # labeles.append(lab)
last_id = i+1

mas_edge=[]
mas_prop=[]
select_color = 0
save_num_reas = []
save_reas =''''''


for i in range(leng):
    for j in range(lengmass):
        if t1[i].value[j] == True:
            save_num_reas.append(j)
            save_reas+=str(j)+'; '
            lab = 'Св-во ' + str(i)  # Prooertise name
            Prop_id = last_id + i
            edge_id = j
            G.add_node(Prop_id, x=i, y=i, size=45, label=lab, color=colors[select_color])  # add propetis

            mas_edge.append(j)
            mas_prop.append(Prop_id)
            # labeles.append(lab)
    select_color += 1
    save_reas+='<br>'

print(save_num_reas)

select_color=0
compare = mas_prop[0]
s1 = len(mas_edge)
for i in range(s1):
    if compare != mas_prop[i]:
        select_color += 1
    compare = mas_prop[i]
    G.add_edge(mas_prop[i], mas_edge[i], id=i+1, color=colors[select_color])



pos = nx.circular_layout(G)

leng=len(G.node)
for i in range(leng):
    x_t = pos[i][0]
    y_t = pos[i][1]
    G.node[i]['x'] = x_t
    G.node[i]['y'] = y_t


d = json_graph.node_link_data(G)
d['edges']=d['links']
d['links']=[]

json.dump(d, open('data.json', 'w'))
import json
s = json.dumps(d)
print(s)

nx.draw_networkx(G, pos=pos, with_labels=True)
plt.show()


f = open('test.html', 'w', encoding='utf-8')
str1='''

<html>
<head>
<meta charset="Utf-8">
  <style type="text/css">
  #container {
    max-width: 800px;
    height: 800px;
    margin-left: 15%;
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
  <table id="bigtable" border="2">
  <tr>
  <td style="min-width:200px; width:15%; background-color:#F7EC8D";>'''

str2='''<div>
  <p id="result"><b>Для выполнения целей: <br></b>'''
for i in range(len(propetis)):
    str2+=propetis[i]


str3= '''<b>Необходимо обладание причин: <br></b>'''+save_reas+'''</p></div>'''

str4='''
  </td>
  <td style="min-width:810px; width:60%; background-color:#A7FBA9;">
      <div id="container"></div>
  </td>

  <td style="min-width:200px; width:25%";>
  <div style="background-color:#8B98F9">
    <b>Цели:</b><br>
  '''

# for properties

str5 = ''''''
for i in range(len(propetis)):
    propetis[i]+=br
    str5+=str(i+1)+propetis[i]

str6 = '''
  </div>
    <div id="lefttext">
    <b>Список причин:</b><br>
    '''

# THIS  PLACE
tempstr = ''''''
for i in range(len(reasons_square)):
    reasons_square[i]+=br
    tempstr+=str(i)+reasons_square[i]

str7 = tempstr
str8 = ''' </div>
  </td>
    </tr>
  </table>
  <script src="sigma.min.js"></script>
  <script src="sigma.parsers.json.min.js"></script>
  <div id = "myid2" name="text" style="height:1px; width: 100%; visibility:hidden;">
  '''
str9=s
str10=  '''
  </div>'''




# str62=save_reas
# for i in range(len(reasons_square)):
#     str62=reasons_square[i]+'<br>'


str11='''
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
f.write(str1+str2+str3+str4+str5+str6+str7+str8+str9+str10+str11)
