CODE_TMPL = '*GRAPH_TMPL*'
BR_TMPL = 'br'


def generate_cause_html(s):
    tmpl = open('templates/cause_template.html')
    text = tmpl.read()
    tmpl.close()

    text = text.replace(CODE_TMPL, s)

    dest = open('templates/cause_net.html', 'w', encoding='utf-8')
    dest.write(text)
    dest.close()
