import os


# Según el número de nodos y redes el dibujo será dimensionado de una forma u otra
def calculate_size():
    num_nodes = len(dict_nodes)
    num_networks = len(dict_networks) - 1 # Quito la externa que va en el ultimo nivel
    
    # Calculo el tamaño del eje y del dibujo
    global size_y
    if num_nodes <= num_networks:
        size_y = num_networks
    else:
        size_y = num_nodes
    
    # Ahora, del eje x
    global size_x
    size_x = -1 
    for i in range(len(levels)):
        if len(levels[i]):
            size_x += 2
    
    # This is for the case we have too less nodes and networks, to avoid tags being write up on another
    if num_nodes < 5 or num_networks < 5:
        size_x = size_x * 2



def insert_icons():
    icons = ''
    # Añado los nodos
    x = 0
    y = 0
    for i in dict_nodes.keys():
        icons += '  ' + i + ': {<<: *servers, x: ' + str(x) + ', y: ' + str(y) + '}\n'
        y += 1
    # Creo un network element para conectar cada red
    x = int(size_x/2)
    y = 0
    for i in dict_networks.keys():
        if i != "public1":
            icons += '  ' + i + '-NE: {<<: *cisco, x: ' + str(x) + ', y: ' + str(y) + ', icon: "router"}\n'
            y += 1
        else:
            icons += '  public1-router: {<<: *cisco, x: ' + str(size_x - 1) + ', y: ' + str(int(size_y/2)) + ', icon: "router"}\n'

    return icons

def insert_connections():
    connections = ''
    # Añado las conexiones nodo a nodo
    for i in dict_nodes.keys():
        for j in dict_nodes[i].keys():
            # Tambien habría forma de diferenciar ifaces
            connections += '  - { <<: *connection, endpoints: ["'+ i + ':' + dict_nodes[i][j] + '", "' + j +'-NE"] }\n'

    # Conecto todos los networks elements a la red publica (esto podría no ser asi siempre)
    for i in dict_networks.keys():
        if i != "public1":
            connections += '  - { <<: *connection, endpoints: ["'+ i + '-NE", "public1-router"] }\n' #Harcoded the name of external net
    return connections


def graph_file_gen(nodes, networks, all_levels):
    # Aqui generamos el fichero que leerá la aplicación que generará la imagen de la topologia del despliegue
    # Necesitamos saber los nodos que tenemos y las redes a las que estan conectados en esta primera version basica
    global dict_networks, dict_nodes, levels
    dict_networks = networks
    dict_nodes = nodes
    levels = all_levels
    
    calculate_size()
    if os.path.exists("graph_creator.yaml"):
        os.remove("graph_creator.yaml")
    f= open("graph_creator.yaml","w+") # Creo el fichero

    template= '''
diagram:
  fill: "linen"
  rows: '''+ str(size_y)  + ''' #7
  columns: ''' + str(size_x) + ''' #5
  gridLines: false
  gridPaddingInner: .2
  groupPadding: .8
title:
  type: "bar"
  text: "First Example"
  author: "Victor CM"
  color: black
  logoFill: none
  fill: none
  stroke: "black"

defaults: &defaults
  color: "black"
  fill: "#555555"
  iconFamily: "azureEnterprise"
  iconFill: "black"
  iconStroke: "black"
  stroke: "#004BAF"
cisco: &cisco
  color: "#004BAF"
  fill: "white"
  iconFamily: "cisco"
  iconFill: "#004BAF"
  iconStrokeWidth: .25
  stroke: "#004BAF"
  preserveWhite: true
servers: &servers
  <<: *defaults
  fill: "white"
  icon: "webserver"
icons:
  # Aqui tengo que añadir los nodos. Algoritmo basico creado para que ordene según el número de nodos y nets
''' + insert_icons() + '''
connection: &connection
  stroke: "black"
  strokeDashArray: "0,0"
  color: "black"
connections:
  # Aqui añado las distintas conexiones. Por ahora solo van de nodos a routers intermedios y de estos al exterior
''' + insert_connections()

    f.write(template)


    f.close() 