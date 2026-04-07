 # Geochemistry Data Plotting
## 即开即用交互式投图界面（Python）

该仓库提供了一个基于 **Streamlit** 的地球化学 CSV 投图工具，支持：

- 上传 CSV（启动后默认不绘图，等待用户选择）。

- 在界面中选择横纵坐标列（数值列）。

- 按任意一列进行筛选，只绘制满足特征的数据。

- 按任意一列进行分类，不同类别使用不同颜色与符号。

- 一键保存当前投图为 PNG / SVG / PDF。

  ## 使用方法

1. 安装依赖：

```bash
   pip install -r requirements.txt
```

2. 启动界面：

```bash
   streamlit run app.py
```

3. 浏览器打开后上传 CSV 并设置参数。

## 输入数据说明

- 推荐 CSV 第一行为表头。
- 作为横纵坐标的列应为数值列（例如 `SiO2`, `K2O`, `Na2O` 等）。
- 分类列与筛选列可使用任意文本或数值列（例如 `Type`, `Sub type`, `country`）。
