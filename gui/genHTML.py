def write_html(s):

    reasons_square = []
    propetis = []
    br = '<br>'


# addd test

    save_reas = ''' save_REAS    text'''

    f = open('test.html', 'w', encoding='utf-8')
    str1 = '''

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

    str2 = '''<div>
      <p id="result"><b>Для выполнения целей:  УБРАТЬ !!!! <br></b>'''
    # for i in data['P']:
    #     if data[i] != 0 and data[i] !=1:
    #         str2 += ';    EMPTY PLACE'


    str3 = '''<br><b>Необходимо обладание причин: <br></b>''' + save_reas + '''</p></div>'''

    str4 = '''
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
        propetis[i] += br
        str5 += str(i + 1) + propetis[i]

    str6 = '''
      </div>
        <div id="lefttext">
        <b>Список причин:</b><br>
        '''

    # THIS  PLACE
    tempstr = ''''''
    for i in range(len(reasons_square)):
        reasons_square[i] += br
        tempstr += str(i) + reasons_square[i]

    str7 = tempstr
    str8 = ''' </div>
      </td>
        </tr>
      </table>
      <script src="sigma.js"></script>
      <script src="sigma.parsers.json.min.js"></script>
      <div id = "myid2" name="text" style="height:1px; width: 100%; visibility:hidden;">
      '''
    str9 = s
    str10 = '''
      </div>'''

    str11 = '''
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
    f.write(str1 + str2 + str3 + str4 + str5 + str6 + str7 + str8 + str9 + str10 + str11)