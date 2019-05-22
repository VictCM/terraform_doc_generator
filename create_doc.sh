#!/bin/bash

# Launch .py file that parse the .json file received from terraform and create a .yaml file
sudo python3 ./resource_parser.py -i openstack_example.json

# We inject the .yaml file that describes the graph to dld4 docker that creates the .png
cat graph_creator.yaml | curl -v -X POST -H "Content-Type: text/yaml"  --data-binary @- http://localhost:3030 > images/deployment_graph.png

cat graph_creator.yaml | curl -v -X POST -H "Content-Type: text/yaml" -H "Accept: image/svg+xml" --data-binary @- http://localhost:3030 > images/deployment_graph.svg

