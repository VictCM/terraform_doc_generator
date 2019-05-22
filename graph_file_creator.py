


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



def insert_icons():
    icons = ''
    # Añado los nodos
    x = 0
    y = 2
    for i in dict_nodes.keys():
        icons += '  ' + i + ': {<<: *servers, x: ' + str(x) + ', y: ' + str(y) + '}\n'
        y += 2
    # Creo un switch para conectar cada red
    x = 2
    y = 0
    for i in dict_networks.keys():
        if i != "public1":
            icons += '  ' + i + '-switch: {<<: *cisco, x: ' + str(x) + ', y: ' + str(y) + ', icon: "nexus5000"}\n'
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
            connections += '  - { <<: *connection, endpoints: ["'+ i + ':' + dict_nodes[i][j] + '", "' + j +'-switch"] }\n'

    # Conecto todos los switches a la red publica (esto podría no ser asi siempre)
    for i in dict_networks.keys():
        if i != "public1":
            connections += '  - { <<: *connection, endpoints: ["'+ i + '-switch", "public1-router"] }\n' #Harcoded the name of external net
    return connections


def graph_file_gen(nodes, networks, all_levels):
    # Aqui generamos el fichero que leerá la aplicación que generará la imagen de la topologia del despliegue
    # Necesitamos saber los nodos que tenemos y las redes a las que estan conectados en esta primera version basica
    global dict_networks, dict_nodes, levels
    dict_networks = networks
    dict_nodes = nodes
    levels = all_levels
    
    calculate_size()
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
  color: black
  logoFill: none
  fill: none
  stroke: "black"

defaults: &defaults
  color: "white"
  fill: "#555555"
  iconFamily: "azureEnterprise"
  iconFill: "white"
  iconStroke: "none"
  stroke: "none"
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
  fill: "#58585B"
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