from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_BREAK
import json
import time
from resource_parser import (dict_networks, dict_nodes)


variables_file = open('terraform_output.json')
variables = json.loads(variables_file.read())
variables_file.close()
filename='./tests/origen.docx'
document = Document()



# Reemplaza las palabras que hemos definido en el terraform_output.json
def replace_keywords():
    for p in document.paragraphs:
        inline = p.runs
        for j in range(0,len(inline)):
            for keyword, variable in variables.items():
                
                ### Keyword lo utilizamos para encontrar el recurso, por ejemplo, las instancias. ###
                #####################################################################################



                inline[j].text = inline[j].text.replace(keyword, variable)
                #print(str(keyword))
        #print(inline[j].text)

# Creamos documentación a partir de los recursos del despliegue
def add_resources_info(dict_nodes, dict_networks):
    num_nodes = len(dict_nodes)
    num_networks = len(dict_networks)

    p = document.add_paragraph()
    # Titulo
    document.add_heading('Reporte de despliegue', 0)
    # Capítulo
    document.add_heading('''Despliegue actual (Hora: ''' + time.strftime("%H:%M:%S") + ''')''', level=1)
    # Info-texto
    introduction = '''En el despliegue realizado se han creado ''' + str(num_nodes) + ''' instancias y ''' + str(num_networks) + ''' redes. \n'''
    introduction +='''  Nodos: \n'''
    p = document.add_paragraph(introduction)

    for i in dict_nodes.keys():
        p = document.add_paragraph(" ", style='List Bullet')
        r=p.add_run()
        r.add_picture('./images/deployment_graph.png',width=Inches(6))
        p.add_run(str(i) + ''': ''').bold = True

        # Busco entre las posibles opciones de despliegue que tenemos en el equipo cual es la que estamos desplegando
        found_node=i.find("node")
        num_node=0
        if (found_node != -1):
            num_node += 1
            p.add_run('Nodo encontrado. Añadir descripción de la VNF si procede')
            p.add_run(' La(s) interface(s) de red tiene(n) acceso:\n')
            for j in dict_nodes[i].keys():
                p.add_run('''       - ''' + j + ''': Con IP ''' + dict_nodes[i][j] + '''.\n''')
        else:
            p.add_run('No se ha encontrado referencia a esa instancia')
    
   

def doc_generator(dict_nodes, dict_networks):
    p = document.add_paragraph()
    r = p.add_run()
    r.add_picture('./images/deployment_graph.png',width=Inches(6))
    #p = document.add_paragraph(" ")
    #run = p.add_run()
    #run.add_break(WD_BREAK.PAGE)
    add_resources_info(dict_nodes, dict_networks)
    replace_keywords()
    document.add_picture('./images/deployment_graph.png', width=Inches(6))
    document.save('./tests/demo.docx')