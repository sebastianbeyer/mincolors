#!/bin/env python

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

data = np.array([[ 0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1 ],
                 [ 0,0,0,0,0,0,1,1,1,1,1,2,2,2,1,1,1,1,0,0 ],
                 [ 0,0,0,0,0,0,0,1,1,1,2,2,2,2,2,1,1,1,0,0 ],
                 [ 0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0 ],
                 [ 0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0 ],
                 [ 0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0 ],
                 [ 0,0,0,6,6,0,0,0,0,3,3,3,3,0,0,0,0,0,0,0 ],
                 [ 0,0,0,0,0,0,0,0,0,3,3,3,3,0,0,0,0,0,0,0 ]])

# stencil for all 8 neighbors of a cell
stencil8 = np.array([
                    [0,-1],
                    [0,1],
                    [1,0],
                    [-1,0],
                    [-1,-1],
                    [1,-1],
                    [1,1],
                    [-1,1]
                    ])
# stencil for only cardinal neighbors
stencil4 = stencil8[0:4]

def neighbor_pairs(data, i, j):
    pair = list()
    for n in stencil4:
        ni = i+n[0]
        nj = j+n[1]
        if (ni < 0 or ni > data.shape[0]-1): continue
        if (nj < 0 or nj > data.shape[1]-1): continue
        if (data[i, j] != data[ni, nj]):
            pair.append((data[i, j], data[ni, nj]))
    return pair

def get_all_pairs(data):
    cell_pairs = list()
    for i in range(data.shape[0]-1):
        for j in range(data.shape[1]-1):
            cell_pairs = cell_pairs + neighbor_pairs(data, i, j)
    return cell_pairs

def sort_pairs(pairs):
    sorted_pairs = list()
    for pair in pairs:
        sorted_pair = tuple(sorted(pair))
        sorted_pairs.append(sorted_pair)
    return sorted_pairs 

def remove_dups(pairs):
    return list(set(pairs))

##########

def plot_graph(connections, clist):
    G = nx.from_edgelist(connections)
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos,node_size=700, node_color=clist)
    # edges
    nx.draw_networkx_edges(G,pos, width=6)
    # labels
    nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
    plt.show()

###########
## greedy coloring
###########


def greedycolors(graph):
    colors = ['Red', 'Blue', 'Green', 'Yellow',  'Black', 'Pink', 'Orange', 'White', 'Gray', 'Purple', 'Brown', 'Navy']
    colors_of_nodes = {}
    def coloring(node, color):
        for neighbor in graph.neighbors(node):
            color_of_neighbor = colors_of_nodes.get(neighbor, None)
            if color_of_neighbor == color:
                return False
            return True
        
    def get_color_for_node(node):
        for color in colors:
            if coloring(node, color):
                return color
    
    for node in graph.nodes():
        colors_of_nodes[node] = get_color_for_node(node)
    return colors_of_nodes

def make_colorlist(colordict):
    colorlist = list()
    for key, value in colordict.items():
        colorlist.append(value)
    return colorlist

#############

if __name__ == '__main__':
    
    all_pairs = get_all_pairs(data)
    sorted_pairs = sort_pairs(all_pairs)
    nodups = remove_dups(sorted_pairs)
    conns = nodups

    print("connections:")
    print(conns)

    print("generate graph")
    G = nx.from_edgelist(conns)

    gcolors = greedycolors(G)
    print(gcolors)
    clist = make_colorlist(gcolors)

    # graph
    plot_graph(conns, clist)
