import networkx as nx
import os
import numpy as np
import argparse
import json
from collections import Counter
import time
from tqdm import tqdm

def parse_args():
    parser = argparse.ArgumentParser(description="Obj to graph")

    # Debug 20200522 hxy : add configure_file

    parser.add_argument('--configure_file', default='./combustion_topology_analysis.json',
                        help='configure json file')

    args = parser.parse_args()

    configure_json_file = args.configure_file

    f = open(configure_json_file)
    json_content = json.load(f)

    args.volume_type = json_content['volumes']['dtype']
    args.volume_dimension = json_content['volumes']['dimension']
    args.volume_file_path = json_content['volumes']['file_path']
    args.volume_file_names = json_content['volumes']['file_names']
    args.data_byte_order = json_content['volumes']['data_byte_order']
    args.persistence_threshold_low = json_content['contour_trees']['persistence_threshold_low']
    args.obj_path = json_content['contour_trees']['obj_path']

    if args.obj_path[-1] == '/' or args.obj_path[-1] == '\\':
        args.obj_path = args.obj_path[:-1]
    args.obj_path = args.obj_path + '_p_' + str(args.persistence_threshold_low) + '/'

    args.graph_path = json_content['graphs']['graph_path']
    if args.graph_path[-1] == '/' or args.graph_path[-1] == '\\':
        args.graph_path = args.graph_path[:-1]
    args.graph_path = args.graph_path + '_p_' + str(args.persistence_threshold_low) + '/'
    args.node_vector_length = json_content['graphs']['scalar_value_dimension']
    args.volume_sample_ratio = json_content['graphs']['volume_sample_ratio']

    return args


def loadObj(file_name: str):
    if not os.path.exists(file_name):
        print("Error: File not exists.")
        return
    points = []
    edges = []
    with open(file_name, 'r') as f:
        while True:
            l = f.readline()
            if not l:
                break
            strings = l.split(" ")
            if strings[0] == "v":
                points.append((int(strings[1]), int(strings[2]), int(strings[3])))
            elif strings[0] == 'f' or strings == 'l':
                edges.append([int(strings[1]), int(strings[2])])
    return np.array(points), np.array(edges)

def loadVolume(file_name:str, dimension, dtype, histogram_size, byte_order='BigEndian'):
    if dtype == 'unsigned char' or dtype == 'uchar' or dtype == 'uint8':
        dtype = 'uint8'
    elif dtype == 'float' or dtype == 'float32':
        dtype = 'float32'
    elif dtype == 'unsigned short' or dtype == 'ushort':
        dtype = 'uint16'
    else:
        print("Error: dtype of {} is not fit the process.".format(dtype))
        return None
    volume = np.fromfile(file_name, dtype=dtype)
    volume = volume.reshape(dimension[::-1])
    if dtype != 'uint8':
        volume = (volume - volume.min())/(volume.max() - volume.min())*(histogram_size-1)
    else:
        volume = volume*(histogram_size/256)
    volume = volume.astype('uint8')
    return volume

def getDistribution(volume, histogram_size):
    distribution = np.zeros(histogram_size)
    cnt = Counter(volume)

    for index in cnt:
        distribution[index] = cnt[index]
    distribution /= volume.shape[0]
    return distribution


def process_bar(percent, start_str='', end_str='', total_length=0):
    bar = ''.join(["\033[31m%s\033[0m" % '   '] * int(percent * total_length)) + ''
    bar = '\r' + start_str + bar.ljust(total_length) + ' {:0>4.1f}%|'.format(percent * 100) + end_str
    print(bar, end='', flush=True)


def obj2Graph(nodes, edges, volume, volume_sample_ratio, histogram_size):
    G = nx.Graph()
    shape = np.array(list(volume.shape))
    sample_shape = np.ceil(shape/volume_sample_ratio).astype('int') // 2

    for i in range(len(sample_shape)):
        sample_shape[i] = max(sample_shape[i], 1)

    idx = 0
    for point in tqdm(nodes):
        # tqdm.set_description("Node {}".format(idx))
        low_bound = point[::-1] - sample_shape
        high_bound = point[::-1] + sample_shape
        low_bound[low_bound < 0] = 0
        for i in range(len(high_bound)):
            high_bound[i] = min(high_bound[i], shape[i])
        distribution = getDistribution(volume[low_bound[0]:high_bound[0], low_bound[1]:high_bound[1],
                                       low_bound[2]:high_bound[2]].flatten(), histogram_size)

        G.add_node(idx, cls=-1)
        for j in range(distribution.shape[0]):
            G.node[idx][j] = distribution[j]
        idx += 1
    for s, t in edges:
        G.add_edge(s-1, t-1)
    return G

if __name__ == '__main__':
    args = parse_args()
    if not os.path.exists(args.obj_path):
        print("Error: Could not find the obj path.")
        exit()
    if not os.path.exists(args.graph_path):
        os.makedirs(args.graph_path)

    for name in args.volume_file_names:

        volume_name = os.path.join(args.volume_file_path, name)
        print('Translating obj to graph : {}'.format(volume_name.split('/')[-1].split('.')[0]))

        buf_name = name.replace('/', '_')
        obj_name = os.path.join(args.obj_path, buf_name.split('.')[0] + '_contour.obj')
        graph_name = os.path.join(args.graph_path, buf_name.split('.')[0] + '.gexf')

        points, edges = loadObj(obj_name)
        # print(points.shape, edges.shape)

        volume = loadVolume(volume_name, args.volume_dimension, args.volume_type, args.node_vector_length)
        G = obj2Graph(points, edges, volume, args.volume_sample_ratio, args.node_vector_length)
        print(G)
        nx.write_gexf(G, graph_name)


