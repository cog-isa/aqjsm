from gui import graph_gen as gg

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
    str2 = gg.s
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

if __name__ == '__main__':
    print("hello world")
