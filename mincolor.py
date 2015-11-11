#!/bin/env python

import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors
from netCDF4 import Dataset

exampledata = np.array([[ 0,0,0,0,0,1,1,1,1,1,2,2,2,2,2,1,1,1,1,1 ],
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
    for n in stencil8:
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
    pos = nx.circular_layout(G)
    # pos = nx.spring_layout(G)
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

def plot_map(data, clist):
    cmap = colors.ListedColormap(clist)
    plt.imshow(data, interpolation='nearest', cmap=cmap)
    plt.show()

def print_cpt(gcolors):
    def makecpt_footer():
        """ Print the footer """
        print('B\t127.5')
        print('F\t127.5')
        print('N\t127.5')
    def makecpt_body(gcolors):
        for key, color in gcolors.items():
            print('{0}\t{1}\t{2}\t{3}'.format(key, color, key+1, color))

    makecpt_body(gcolors)
    makecpt_footer()
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate colors')
    parser.add_argument('ncfile', type=str,
                        help='NetCDF file to use')
    args = parser.parse_args()

    print(args.ncfile)
    rootgrp = Dataset(args.ncfile, "r", format="NETCDF4")

    varname = 'basins'

    data = rootgrp.variables[varname][:]
    data = data.astype(int)

    print("getting all pairs from data (this may take some while)")
    all_pairs = get_all_pairs(data)
    print("sorting pairs")
    sorted_pairs = sort_pairs(all_pairs)
    print("removing duplicates")
    nodups = remove_dups(sorted_pairs)
    conns = nodups

    print("connections:")
    print(conns)

    print("generate graph")
    G = nx.from_edgelist(conns)

    gcolors = greedycolors(G)
    print(gcolors)
    clist = make_colorlist(gcolors)

    plot_map(data, clist)

    # graph
    plot_graph(conns, clist)
    rootgrp.close()
