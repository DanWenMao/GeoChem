# README
**scripts for data processing of MELTS results**

## Workflow

### 文件夹结构

Pressure

 - p*
   - Initial water (初始水含量)
     - mineral.tbl
     - melts-liquid.tbl # 逗号分隔文件

### 岩浆的成分演化

melts-liquid.tbl

1. 岩浆成分去除水，重新归一化，新的列：wt% Oxide_n，*_n代表重新归一化的值。

2. liq mass (g)等于岩浆的质量分数F，作为横坐标
3. 计算以下量，作为纵坐标
   1. wt% Na2O_n
   2. wt% K2O_n
   3. mol K_n/Na_n
   4. 总碱：wt% Na2O_n + wt% K2O_n
   5. Fe#：mol Fe_n/(Fe_n+Mg_n)
4. 将一个横坐标列和五个纵坐标列整理输出为csv表格，表格的每一行都写入压强和初始水含量
5. 处理所有Initial water下的melt-liquid.tbl
6. 绘制五张图件，在不同初始水含量情况下，岩浆的物理量随着岩浆的质量分数的变化。
