#!/usr/bin/env python3

import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import colors
from netCDF4 import Dataset
from os import path

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

def plot_graph(connections, clist, filename=None, show_fig=False):
    G = nx.from_edgelist(connections)
    pos = nx.circular_layout(G)

    fig = plt.figure(num=None, facecolor='w', edgecolor='k') #, tight_layout=True)
    # pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G,pos,node_size=700, node_color=clist)
    # edges
    nx.draw_networkx_edges(G,pos, width=6)
    # labels
    nx.draw_networkx_labels(G,pos,font_size=20,font_family='sans-serif')
    if show_fig:
        plt.show()
    if filename:
        fig.savefig(filename, bbox_inches='tight')


###########
## greedy coloring
###########


def greedycolors(graph):

    ## Initial color version
    # colors = ['Red', 'Blue', 'Green', 'Yellow',  'Black', 'Pink', 'Orange', 'White', 'Gray', 'Purple', 'Brown', 'Navy']

    ## gray and blue
    # colors = ['grey','#6A92D4','#1049A9','#052C6E']

    #YlGnBu05
    # colors = ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']

    ## http://soliton.vm.bytemark.co.uk/pub/cpt-city/cb/seq/tn/GnBu_09.png.index.html
    # colors = ['#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5', '#7bccc4', '#4eb3d3', '#2b8cbe', '#0868ac', '#084081']

    ## first blue than green
    colors = ['#4eb3d3', '#2b8cbe', '#0868ac', '#084081', '#7bccc4', '#f7fcf0', '#e0f3db', '#ccebc5', '#a8ddb5']

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

def plot_map(data, clist, filename=None, show_fig=False):
    cmap = colors.ListedColormap(clist)
    fig = plt.figure(num=None, facecolor='w', edgecolor='k') #, tight_layout=True)
    plt.imshow(data, interpolation='nearest', cmap=cmap)
    if show_fig:
        plt.show()
    if filename:
        fig.savefig(filename, bbox_inches='tight')

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


def export_cpt(gcolors, filename):
    ## We are luky. GMT4 already understands named colors. Thus we don't need to convert names to RGB values.
    f = open(filename,"w")
    ## cpt header
    f.write("#	cpt file created by: mincolor.py\n")
    f.write("#COLOR_MODEL = RGB\n")
    f.write("#\n")
    # ## cpt body
    # for key, color in gcolors.items():
    #     f.write("%d\t%s\t%d\t%s\n" % (key, color, key+1, color))
    ## cpt body
    cc = colors.ColorConverter().to_rgb
    for key, color in gcolors.items():
        r,g,b = cc(color)
        f.write("%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\n" % (key, r*255, g*255, b*255, key+1, r*255, g*255, b*255))

    ## cpt footer
    f.write("B\t0\t0\t0\n")       ## GMT defaults
    f.write("F\t255\t255\t255\n") ## GMT defaults
    f.write("N\t128\t128\t128\n") ## GMT defaults
    f.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate colors')
    parser.add_argument('ncfile', type=str,
                        help='NetCDF file to use')

    parser.add_argument('-v','--varname', dest='varname', default='z', type=str,
                        help='variable name of the regions in NetCDF')

    parser.add_argument('-n','--name', dest='name', default=None, type=str,
                    help='basename for all output files')

    parser.add_argument('-s', '--show_fig', dest='show_fig', action="store_true",
                        help='show figures on the screen (default: no)')

    parser.add_argument('-e', '--export_cpt', dest='export_cpt', action="store_true",
                        help='export color table as GMT cpt file')

    args = parser.parse_args()

    rootgrp = Dataset(args.ncfile, "r", format="NETCDF4")
    data = rootgrp.variables[args.varname][:]
    data = data.astype(int)
    rootgrp.close()

    if args.name:
        name = args.name
    else:
        name, ext = path.splitext(path.basename(args.ncfile))


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

    # a simple map
    fname = name + '_map.png'
    plot_map(data, clist, filename=fname, show_fig=args.show_fig)
    print("%s saved" % fname)

    # graph
    fname = name + '_graph.png'
    plot_graph(conns, clist, filename=fname, show_fig=args.show_fig)
    print("%s saved" % fname)

    # cpt file
    if args.export_cpt:
        fname = name + '.cpt'
        export_cpt(gcolors, fname)
        print("%s saved" % fname)


