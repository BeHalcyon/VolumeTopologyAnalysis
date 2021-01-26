# state file generated using paraview version 5.8.1

# ----------------------------------------------------------------
# setup views used in the visualization
# ----------------------------------------------------------------

# trace generated using paraview version 5.8.1
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#### import the simple module from the paraview
from paraview.simple import *

def calculateContourTree(file_name, dtype, dimension, space, output_obj_name, 
                        persistence_low, persistence_high, data_byte_order='BigEndian'):
    #### disable automatic camera reset on 'Show'
    # paraview.simple._DisableFirstRenderCameraReset()
    # SetActiveView(None)
    # ----------------------------------------------------------------
    # setup the data processing pipelines
    # ----------------------------------------------------------------

    # create a new 'Image Reader'
    # TODO
    mixfracraw = ImageReader(FileNames=[file_name])
    if dtype == 'uint8' or dtype == 'uchar' or dtype == 'unsigned char':
        mixfracraw.DataScalarType = 'unsigned char'
    elif dtype == 'float':
        mixfracraw.DataScalarType = 'float'
    elif dtype == 'ushort' or dtype == 'unsigned short':
        mixfracraw.DataScalarType = 'unsigned short'
    else:
        print("Data type error. Please check the data type of {}".format(dtype))
        exit()
    mixfracraw.DataByteOrder = data_byte_order
    mixfracraw.DataExtent = [0, dimension[0]-1, 0, dimension[1]-1, 0, dimension[2]-1]

    # create a new 'TTK PersistenceDiagram'
    tTKPersistenceDiagram1 = TTKPersistenceDiagram(Input=mixfracraw)
    tTKPersistenceDiagram1.ScalarField = ['POINTS', 'ImageFile']
    tTKPersistenceDiagram1.InputOffsetField = ['POINTS', 'ImageFile']
    
    # create a new 'Threshold'
    threshold1 = Threshold(Input=tTKPersistenceDiagram1)
    threshold1.Scalars = ['CELLS', 'Persistence']
    threshold1.ThresholdRange = [persistence_low, persistence_high]
    # create a new 'Threshold'
    threshold2 = Threshold(Input=threshold1)
    threshold2.Scalars = ['CELLS', 'PairIdentifier']
    # threshold2.ThresholdRange = [0.0, 19164.0]
    # set the maximum value for threshold2
    threshold2.ThresholdRange = [0.0, 1000000000.0]

    # create a new 'TTK TopologicalSimplification'
    tTKTopologicalSimplification1 = TTKTopologicalSimplification(Domain=mixfracraw,
        Constraints=threshold2)
    tTKTopologicalSimplification1.ScalarField = ['POINTS', 'ImageFile']
    tTKTopologicalSimplification1.InputOffsetField = ['POINTS', 'ImageFile']
    tTKTopologicalSimplification1.VertexIdentifierField = ['POINTS', 'CriticalType']

    # create a new 'TTK Merge and Contour Tree (FTM)'
    tTKMergeandContourTreeFTM1 = TTKMergeandContourTreeFTM(Input=tTKTopologicalSimplification1)
    tTKMergeandContourTreeFTM1.ScalarField = ['POINTS', 'ImageFile']
    tTKMergeandContourTreeFTM1.InputOffsetField = ['POINTS', 'ImageFile']
    

    # find source
    # tTKMergeandContourTreeFTM1_2 = FindSource('TTKMergeandContourTreeFTM1')
    
    # set active source
    # tTKMergeandContourTreeFTM1_2 = GetActiveSource()
    # save data

    SaveData(output_obj_name, proxy=OutputPort(tTKMergeandContourTreeFTM1, 1))
    # SaveData(output_obj_name, proxy=OutputPort(tTKMergeandContourTreeFTM1_2, 1))


    SetActiveSource(tTKMergeandContourTreeFTM1)
    Delete(tTKMergeandContourTreeFTM1)
    del tTKMergeandContourTreeFTM1

    SetActiveSource(tTKTopologicalSimplification1)
    Delete(tTKTopologicalSimplification1)
    del tTKTopologicalSimplification1

    SetActiveSource(threshold2)
    Delete(threshold2)
    del threshold2

    SetActiveSource(threshold1)
    Delete(threshold1)
    del threshold1

    SetActiveSource(tTKPersistenceDiagram1)
    Delete(tTKPersistenceDiagram1)
    del tTKPersistenceDiagram1

    SetActiveSource(mixfracraw)
    Delete(mixfracraw)
    del mixfracraw

