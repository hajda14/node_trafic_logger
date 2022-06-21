from os import environ
from node import Node, NODE_TYPE

if __name__ == "__main__":
    node = Node(NODE_TYPE[environ.get("NODE_TYPE","MASTER")])
    