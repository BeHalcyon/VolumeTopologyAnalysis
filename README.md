# VolumeTopologyAnalysis

## 1. 利用ttk生成体数据对应的轮廓树(contour_tree_extraction.py)

    -- 输入：体数据， persistence参数（包含在配置文件.json中），列表形式
    -- 输出：体数据对应的obj，列表形式
描述：该工具利用contour_tree_extraction模块批处理提取体数据中的轮廓树，并将其应用到体数据
需要利用ttk工具包的pvpython.exe编译运行，计算量大，比较耗内存

需要用到的json格式为：
```
{
    "volumes":{
        "dtype": "unsigned char", // one of ['unsigned char', 'float', 'unsigned short']
        "space": [1, 1, 1],
        "dimension": [480, 720, 120],
        "file_path": "G:/volume data/combustion/", //最好以'/'结尾
        "data_byte_order": "BigEndian", // 默认都是'BigEndian'， 其中combustion的float类型数据是'LittleEndian'
        "file_names": [
            ...
        ] // 体数据文件名的列表
    },
    //生成轮廓树的参数部分
    "contour_trees": {
        "persistence_threshold_low": 0.01, //最低的阈值，该阈值过滤较低的一致性值。
        "persistence_threshold_high": 510.0, //最高的阈值，该阈值过滤高的一致性值。
        "obj_path": "C:/Users/xiangyanghe/Desktop/paraview workspace/obj results/jet_chi/" // 拟生成轮廓树的目录，该目录需要先自定义生成
    },

}
```

调用命令如下:
```python
pvpython contour_tree_extraction.py --configure_file ../configure/topology_analysis_combustion_chi_uint8_p_0.01.json
```

TODO: 
1. persistenec_threshold_low和persistence_threshold_high两个值目前是恒定的，不能适配多个数据集，需要寻找ttk工具中能够计算并剥离计算最高及最低持续性值得接口；
2. 寻找如何生成持续性曲线的接口，实现可视化过滤的批处理生成。
 -----------
 ## 2. 将obj转为networkx图文件
    
    --输入：体数据对应的obj，列表形式
    --输出：obj对应的networkx图，列表形式

描述：该工具利用obj2graph模块批处理将obj文件转换为对应的gefx文件。算法支持对obj内所有点上下文的标量值分布提取，通过设定"graph"集中的"volume_sample_ratio"变量（提高该参数值能降低节点上下文的维度，降低该值能提高该上下文的维度，从经验上来说，上下文维度不易过小也不易过大，需要尝试调节及参数讨论）。节点的上下文分布特征已归一化处理。

需要用到json数据为：

```
{
    "graphs": {
        "volume_sample_ratio": 20,  //表示为节点的采样率，dimension/volume_sample_ratio表示采样数据的包围盒大小
        "scalar_value_dimension": 256 //拟生成节点的分布表征维度
    }
}
```

调用命令如下：
```python
python ./PreprocessingTools/obj2graph.py --configure_file ./configure/topology_analysis_combustion_Y_OH_uint8_p_0.01.json
```

TODO：
1. 体数据的分布一般比较集中，可尝试使用log归一化对上下文节点特征进行归一；
2. 尝试不同的volume_sample_ratio，判断其训练精度。