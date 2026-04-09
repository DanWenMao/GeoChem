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

文件示例内容

Index,T (C),P (kbars),log(10) f O2,liq mass (gm),liq rho (gm/cc),wt% SiO2,wt% TiO2,wt% Al2O3,wt% Fe2O3,wt% Cr2O3,wt% FeO,wt% MnO,wt% MgO,wt% NiO,wt% CoO,wt% CaO,wt% Na2O,wt% K2O,wt% P2O5,wt% H2O,wt% CO2,wt% SO3,wt% Cl2O-1,wt% F2O-1,liq G (kJ),liq H (kJ),liq S (J/K),liq V (cc),liq Cp (J/K),activity SiO2,activity TiO2,activity Al2O3,activity Fe2O3,activity MgCr2O4,activity Fe2SiO4,activity MnSi0.5O2,activity Mg2SiO4,activity NiSi0.5O2,activity CoSi0.5O2,activity CaSiO3,activity Na2SiO3,activity KAlSiO4,activity Ca3(PO4)2,activity CO2,activity SO3,activity Cl2O-1,activity F2O-1,activity H2O,liq vis (log 10 poise),sol mass (gm),sol rho (gm/cc),sol G (kJ),sol H (kJ),sol S (J/K),sol V (cc),sol Cp (J/K),sys G (kJ),sys H (kJ),sys S (J/K),sys V (cc),sys Cp (J/K),sys dVdT (cc/K),sys dVdP (cc/bar),sys alpha (1/K),sys beta (1/bar),liq dVdT (cc/K),liq dVdP (cc/bar),liq alpha (1/K),liq beta (1/bar)
1,1465.82,20.000,-4.500,9.8644569194120e+01,2.8170,53.6250,0.7074,18.7129,1.0313,0.0000,6.4555,0.0000,5.5422,0.0000,0.0000,10.8256,2.7047,0.3953,0.0000,0.0000,0.0000,0.0000,0.0000,0.0000,-1.6288983170228e+03,-1.1382304859848e+03,2.8215998140450e+02,3.5017945257402e+01,1.4686619766452e+02,4.7213806e-01,1.5214931e-02,2.1002644e-02,3.9100534e-03,2.3634470e+00,6.3777822e-02,6.3191830e-01,4.7748308e-02,1.5515782e+00,7.0893756e-01,1.3175435e-01,2.9406247e-04,4.9387882e-03,1.9618685e+01,7.3722540e-01,6.7719165e-01,6.7719165e-01,6.7719165e-01,2.1428656e+00,1.9656,1.3539365527581e+00,3.6180,-2.2292758481613e+01,-1.6310411273225e+01,3.4401663820173e+00,3.7421988184000e-01,1.6406776261215e+00,-1.6511910755044e+03,-1.1545408972580e+03, 2.8560014778652e+02, 3.5392165139242e+01, 1.4850687529065e+02, 2.9888852818961e-03,-1.1924790336661e-04, 8.4450478520799e-05, 3.3693305537386e-06, 2.9756782454412e-03,-1.1904421715634e-04, 8.4975809504764e-05, 3.3995203396799e-06

1. 岩浆成分去除水，重新归一化，新的列：wt% Oxide_n，*_n代表重新归一化的值。
2. liq mass (g)等于岩浆的质量分数F，作为横坐标
3. 计算以下量，作为纵坐标
   1. wt% Na2O_n
   2. wt% K2O_n
   3. mol K_n/Na_n
   4. 总碱：wt% Na2O_n + wt% K2O_n
   5. Fe#：mol Fe_n/(Fe_n+Mg_n)
   6. 温度：T (C)
5. 将一个横坐标列和六个纵坐标列整理输出为csv表格，表格的每一行都写入压强和初始水含量
6. 处理所有Initial water下的melt-liquid.tbl
7. 绘制七张图件，在不同初始水含量情况下，岩浆的物理量随着岩浆的质量分数的变化。

### 矿物的成分演化

mineral.tbl，mineral={clinopyroxene, corundum, garnet, muscovite, quartz, feldspar}，或者匹配目标文件夹中除了melts-liquid.tbl的*.tbl文件，将文件名（去除tbl后缀）视为矿物名称

文件示例内容

Index,T (C),P (kbars),log(10) f O2,mass (gm),rho (gm/cc),wt% SiO2,wt% TiO2,wt% Al2O3,wt% Fe2O3,wt% Cr2O3,wt% FeO,wt% MnO,wt% MgO,wt% NiO,wt% CoO,wt% CaO,wt% Na2O,wt% K2O,wt% P2O5,wt% H2O,wt% CO2,wt% SO3,wt% Cl2O-1,wt% F2O-1,G (kJ),H (kJ),S (J/K),V (cc),Cp (J/K),     diopside,clinoenstatit, hedenbergite,alumino-buffo,    buffonite,     essenite,      jadeite
1,1363.87,13.000,-5.767,1.7214,3.2470,50.5687,0.1370,6.9536,1.6001,0.0000,7.3283,0.0000,17.7169,0.0000,0.0000,15.2267,0.4687,0.0000,0.0000,0.0000,0.0000,0.0000,0.0000,0.0000,-27.970,-20.923,4.305,0.530,2.089,0.212580,0.372771,0.223194,0.114511,-0.107006,0.150857,0.033093

1. 汇总所有矿物的温度T (C)、质量mass (gm)、成分wt% Oxide列，输出为csv表格，表格的每一行都写入矿物名称
2. 根据矿物的温度T (C)，匹配岩浆的质量分数F
3. 矿物的质量mass (gm)等于矿物的质量分数F_i
4. 处理所有Initial water下的mineral.tbl
5. 以岩浆的质量分数F为横坐标，绘制矿物堆叠面积图，示例代码：

`

minerals_order = [c for c in colors.keys() if c in df_pivot.columns]
ax1.stackplot(df_pivot.index, [df_pivot[m] for m in minerals_order],
              colors=[colors[m] for m in minerals_order],
              labels=minerals_order,
              linewidth=0.2)
ax1.set_xlabel('Melt Fraction')
#ax1.set_ylabel('Crystalline mass fraction (%)', color='black')
ax1.set_ylabel('Mineral Mass Fraction', color='black')
ax1.set_xlim(0, 100)
ax1.set_ylim(0, 100)
ax1.tick_params(axis='y', colors='black')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.tick_params(direction='out', length=4, width=1)

`
