import argparse
import json
from ttk_contour import calculateContourTree
import os
import time
import csv

def writeLog(data=[], file_name='log.csv'):
    f = open(file_name,'w',encoding='utf-8')
    csv_writer = csv.writer(f)
    csv_writer.writerow(data)
    f.close()

def parse_args():
    parser = argparse.ArgumentParser(description="Volume-TA")

    # Debug 20200522 hxy : add configure_file

    parser.add_argument('--configure_file', default='./combustion_topology_analysis.json',
                        help='configure json file')

    args = parser.parse_args()

    configure_json_file = args.configure_file

    f = open(configure_json_file)
    json_content = json.load(f)

    args.volume_type = json_content['volumes']['dtype']
    args.volume_space = json_content['volumes']['space']
    args.volume_dimension = json_content['volumes']['dimension']
    args.volume_file_path = json_content['volumes']['file_path']
    args.volume_file_names = json_content['volumes']['file_names']

    args.persistence_threshold_low = json_content['input_parameters']['persistence_threshold_low']
    args.persistence_threshold_high = json_content['input_parameters']['persistence_threshold_high']
    args.data_byte_order = json_content['volumes']['data_byte_order']

    args.obj_path = json_content['output_parameters']['obj_path']
    if args.obj_path[-1] == '/' or args.obj_path[-1] == '\\':
        args.obj_path = args.obj_path[:-1]
    args.obj_path = args.obj_path + '_p_' + str(args.persistence_threshold_low) + '/'
    return args

if __name__ == "__main__":
    args = parse_args()

    if not os.path.exists(args.obj_path):
        os.makedirs(args.obj_path)

    for name in args.volume_file_names:
        volume_name = os.path.join(args.volume_file_path, name)
        buf_name = name.replace('/', '_')
        obj_name = os.path.join(args.obj_path, buf_name.split('.')[0]+'_contour.obj')
        print("Start calculating the contour tree for volume ***{}***".format(name))
        start_time = time.time()

        if not os.path.isfile(volume_name):
            continue

        if os.path.isfile(obj_name):
            print('Skipping... The obj {} has been calculated.'.format(obj_name))
            continue
        calculateContourTree(volume_name, args.volume_type, args.volume_dimension, 
                            args.volume_space, obj_name, 
                            args.persistence_threshold_low, args.persistence_threshold_high,
                            args.data_byte_order)
        end_time = time.time()
        writeLog([buf_name.split('.')[0], "{:.2f}".format(end_time-start_time)])
        print("The contour tree has been saved in {}".format(obj_name))
        print("Time : {:.2f}s".format(end_time-start_time))
        time.sleep(2)
        

        
