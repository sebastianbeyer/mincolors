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
                 [ 0,0,0,0,0,0,0,0,0,3,3,3,3,0,0,0,0,0,0,0 ],
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
        if (ni < 0 or ni > data.shape[0]): continue
        if (nj < 0 or nj > data.shape[1]): continue
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

def plot_graph(connections):
    G = nx.from_edgelist(connections)
    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos,node_size=700, node_color='#A0CBE2')
    # edges
    nx.draw_networkx_edges(G,pos, width=6)
    # labels
    nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
    plt.show()
