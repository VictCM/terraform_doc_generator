# Pasos:
#   1º- Encontrar un recurso que sea una instancia
#   2º- Encontrar la info que queremos antes de acceder al siguiente recurso
#       ¿como se si se ha terminado e recurso?

import json
from pprint import pprint
import sys, getopt
import graph_file_creator as gfc
import doc_gen

# Los niveles son creados para poder separar los distintos nodos y routers en distintos puntos del eje x
# Si el nivel esta vacio se ignora. La idea es tener ya de base un orden, donde en el 0 van siempre los nodos 
# que se encuentran más en el edge de la red y en el 8 el router que da acceso a internet o al core de TEF
levels = {0: [], 
          1: [], 
          2: [], 
          3: [], 
          4: [], 
          5: [], 
          6: [], 
          7: [], 
          8: []}
levels[8].append("public1-router")

# Creo diccionario donde guardare la información de cada recurso (por ahora, solo VMs)
dict_nodes={}
dict_networks = {"public1": {}} #Harcoded, las networks tienen que añadirse aqui una vez las creo
glob_specific_resource = ""
num_nodes=0
num_networks=1 # Cuento con la externa ya

def read_args():
# Leo argumentos
    if len(sys.argv) <= 1:
        print("Faltan argumentos. Usa -h para ver ayuda")
        exit(1)
    # read commandline arguments, first
    fullCmdArguments = sys.argv

    # - further arguments
    argumentList = fullCmdArguments[1:]
    try:  
        arguments, values = getopt.getopt(argumentList, "hi:", ["input="])
        print("arguments: " + str(arguments))
    except getopt.error as err:  
        # output error, and return with an error code
        print ("Argumentos no válidos. Usa -h para ver ayuda \n" + str(err))
        sys.exit(2)
    
    for currentArgument, currentValue in arguments:
        print(currentArgument)
        if  currentArgument in ("-h", "--help"):
            print ("Necesitas incluir el fichero .json a utilizar como input con -i <file.json>")
        elif currentArgument in ("-i", "--input"):
            with open(currentValue) as data_file:    
                global data 
                data = json.load(data_file)

def check_network_resource(network_name):
    # Miro si ya existe el diccionario creado para esa network, si no lo creo
    if not network_name in dict_networks:
        global num_networks
        num_networks += 1
        levels[4].append(network_name)
        dict_networks[network_name] = {} # Creo dict
        dict_networks[network_name]["network_element"] = ""

def compute_instance():
    print(data["modules"][0]["resources"][glob_specific_resource]["type"]) # Acceso al tipo de cada recurso
    #pprint(data["modules"][0]["resources"][glob_specific_resource]) # Muestro la info de cada recurso
    name_node = data["modules"][0]["resources"][glob_specific_resource]["primary"]["attributes"]["name"]
    dict_nodes[name_node] = {} #Creo un dict para cada nodo
    levels[0].append(name_node) # Le añado al nivel 0
    global num_nodes
    num_nodes += 1

    num_networks = data["modules"][0]["resources"][glob_specific_resource]["primary"]["attributes"]["network.#"]
    for i in range(int(num_networks)):
        network_name = data["modules"][0]["resources"][glob_specific_resource]["primary"]["attributes"]["network.{0}.name".format(i)]
        network_IP = data["modules"][0]["resources"][glob_specific_resource]["primary"]["attributes"]["network.{0}.fixed_ip_v4".format(i)]
        dict_nodes[name_node][network_name] = network_IP
        check_network_resource(network_name)
        dict_networks[network_name][network_IP] = name_node

def aws_instance():
    print(data["modules"][0]["resources"][glob_specific_resource]["type"]) # Acceso al tipo de cada recurso
    #pprint(data["modules"][0]["resources"][glob_specific_resource]) # Muestro la info de cada recurso
    name_node = data["modules"][0]["resources"][glob_specific_resource]["primary"]["attributes"]["tags.Name"]
    dict_nodes[name_node] = {} #Creo un dict para cada nodo
    global num_nodes
    num_nodes += 1

    # En AWS es más complicado ver las redes. Siempre tiene una privada asociada al VPC
    # También puede tener una pública
    # Falta ver como afecta que el resto de interfaces sean definidas aqui y no en un recurso distinto aws_network_interface
    network_name = "private_net"
    network_IP = data["modules"][0]["resources"][glob_specific_resource]["primary"]["attributes"]["private_ip"]
    dict_nodes[name_node][network_name] = network_IP
    check_network_resource(network_name)
    dict_networks[network_name][network_IP] = name_node

def aws_network():
    print(data["modules"][0]["resources"][glob_specific_resource]["type"]) # Acceso al tipo de cada recurso
    # No se saca de la misma forma en OP que en AWS. AWS provee de mas de una forma de hacerlo, mas complicado parsear
    ##########

def compute_fip():
    print(data["modules"][0]["resources"][glob_specific_resource]["type"]) # Acceso al tipo de cada recurso
    #pprint(data["modules"][0]["resources"][glob_specific_resource]) # Muestro la info de cada recurso
    network_name = data["modules"][0]["resources"][glob_specific_resource]["primary"]["attributes"]["pool"]
    network_IP = data["modules"][0]["resources"][glob_specific_resource]["primary"]["attributes"]["address"]
    check_network_resource(network_name)
    dict_networks[network_name][network_IP] = ""


def default_resource():
    print(data["modules"][0]["resources"][glob_specific_resource]["type"]) # Acceso al tipo de cada recurso
    #pprint(data["modules"][0]["resources"][glob_specific_resource]) # Muestro la info de cada recurso

switcher = {
    # Recursos en openstack
    "openstack_compute_instance_v2": compute_instance,
    "openstack_compute_floatingip_v2": compute_fip,

    # Recursos en AWS
    "aws_instance": aws_instance
}

def reader():
    global glob_specific_resource
######## Si no existe el keyword al que intento acceder falla, importante porque no son los
######## mismos los que tiene un recurso compute_instance que uno compute_floatingip
# Localizo los recursos
    for i in data["modules"][0]["resources"].keys(): # Consigo el nombre de todos los recursos e itero sobre cada uno
        #pprint(data["modules"][0]["resources"])
        glob_specific_resource = i
        func = switcher.get(data["modules"][0]["resources"][i]["type"], default_resource)

        func()
        print('\n')
        glob_specific_resource = ""


if __name__ == "__main__":
    read_args()
    reader()
    pprint(dict_nodes)
    pprint(dict_networks)
    print(" En total hay " + str(num_nodes) + " nodos.")

    print(" En total hay " + str(num_networks) + " redes.")

    # Creo el fichero para ser enviado al programa que genera el .png del despliegue
    gfc.graph_file_gen(dict_nodes, dict_networks, levels)

    # Creo documentación con información sobre el despliegue

    doc_gen.doc_generator(dict_nodes, dict_networks)
    
