
import numpy as np
import os

def create_dir_not_exist(path):
    if not os.path.exists(path):
        os.mkdir(path)


def getVtiFiles(dir: str):
    datanames = os.listdir(dir)
    ls = []
    for dataname in datanames:
        if os.path.splitext(dataname)[1] == '.vti':
            ls.append(dataname)
    return ls

def normalizeVolume(volume, histogram_size, dtype):
    return np.array((volume-volume.min())
                                 /(volume.max()-volume.min())*(histogram_size-1),
                                 dtype)

def parse_args(description):
    import argparse
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--directory', default='I:/science data/4 Combustion',
                        help='The directory that need to transfer')
    parser.add_argument('--name', default='None',
                        help='The name that need to transfer. Do not set value to traverse all files in the current directory.')
    parser.add_argument('--dtype', default='float', help='The raw file stored type.', choices=['float', 'uint8'])
    args = parser.parse_args()
    return args


def listFiles(path:str, variable_name:str, suffix='.dat'):
    file_names = []
    for dirpath, dirs, files in os.walk(path):
        for name in files:
            if os.path.splitext(name)[1] == suffix and variable_name in name:
                filename = os.path.join(dirpath, name)
                file_names.append(filename)
    return file_names

def getGlobalRange(file_names, dtype):

    max_value = -1000000000
    min_value = 1000000000

    index = 0
    for name in file_names:
        buf = np.fromfile(name, dtype)
        max_value = max(buf.max(), max_value)
        min_value = min(buf.min(), min_value)
        if index % 10 == 0:
            print('Process for calculating range: {}, global max: {}, global min: {}'.format(name.split('\\')[-1], max_value, min_value))
        index += 1

    return [min_value, max_value]

def regularizationVolume(origin_variable_name, origin_dtype, global_range):
    origin_volume = np.fromfile(origin_variable_name, origin_dtype)
    new_variable_name = origin_variable_name.split('.')[0]+'_char.raw'
    new_volume = normalizeVolume(origin_volume, 256, 'uint8')
    # new_volume = np.array((origin_volume - global_range[0])/(global_range[1] - global_range[0])*255, dtype=np.uint8)
    new_volume.tofile(new_variable_name)

def regularizationVolumes(origin_variable_names, origin_dtype, global_rage):
    index = 0
    for name in origin_variable_names:
        regularizationVolume(name, origin_dtype, global_rage)
        if index % 10 == 0:
            print('Process for regularization of volume: {}'.format(name))
        index += 1


def main():

    hp = parse_args('regularization for raw.')
    variable_names = ['chi', 'mixfrac', 'vort', 'Y_OH']
    dtype = hp.dtype
    directory = hp.directory

    for variable_name in variable_names:
        variable_files = listFiles(directory, variable_name)
        ranges = getGlobalRange(variable_files, 'float32')
        regularizationVolumes(variable_files, 'float32', ranges)


if __name__ == '__main__':
    main()