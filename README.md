# Steam 游戏大数据分析平台

大数据分析与应用课程期末大作业。

基于 Steam 平台游戏数据，完成从数据采集、ETL 处理、多维分析到交互式可视化的完整大数据应用闭环。

## 项目结构

```
steam-game-analysis/
├── data/
│   ├── raw/               # 原始数据集 (CSV)
│   └── processed/         # 清洗后的数据库 (SQLite)
├── src/
│   ├── data_pipeline.py   # ETL 管道：加载 / 清洗 / 存储
│   ├── analyzer.py        # 分析引擎：6 大分析模块
│   └── visualizer.py      # Plotly 图表生成器
├── web/
│   ├── app.py             # Flask 应用入口
│   ├── routes.py          # 路由与 API 接口
│   ├── templates/         # 5 个 HTML 页面模板
│   └── static/            # CSS 样式
├── dataset_prep.py        # 数据集生成脚本
├── run_server.py          # 一键启动脚本
├── requirements.txt
└── README.md
```

## 快速启动

```bash
# 1. 进入项目目录
cd steam-game-analysis

# 2. 生成数据集 (8000 条模拟数据)
python dataset_prep.py

# 3. 运行 ETL 管道 (生成 SQLite 数据库)
python -c "from src.data_pipeline import run_pipeline; run_pipeline('data/raw/steam_games.csv', 'data/processed/steam.db')"

# 4. 启动 Web 服务器
python run_server.py

# 5. 浏览器打开 http://127.0.0.1:5000
```

> 说明：第 2-3 步也可跳过，直接执行 python run_server.py，系统会自动检查并生成数据。

## 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 数据处理 | Pandas + NumPy | 万级数据清洗、聚合与特征工程 |
| 数据存储 | SQLite | 单文件零配置，结构化查询 |
| 分析引擎 | Pandas GroupBy + 统计 | 6 大维度交叉分析 |
| 可视化 | Plotly | 交互式图表，支持缩放/悬停 |
| Web 框架 | Flask | 轻量后端，RESTful API |
| 前端 UI | Bootstrap 5 + Plotly.js | 响应式布局，5 页仪表盘 |

## 六大分析模块

1. 市场总览 - 游戏总数、均价、总评价数、综合好评率、类型分布饼图、年度发行量
2. 价格分析 - 价格区间分布、免费 vs 付费对比、价格-好评率散点图
3. 类型分析 - 类型排行、类型对比统计、热门类型年度趋势
4. 开发商洞察 - Top20 开发商排名、游戏数量 vs 好评率双轴图
5. 评价分析 - 好评率分布直方图、特征相关性热力图
6. 发行趋势 - 年度发行量时序图、平台支持趋势分析

## Web 页面

| 页面 | 路由 | 功能 |
|------|------|------|
| 总览看板 | / | KPI 指标卡 + 类型饼图 + 发行趋势 + 评分分布 + 相关性热力图 |
| 游戏探索 | /games | 搜索/筛选/排序游戏表 + 点击查看详情弹窗 |
| 类型分析 | /genres | 类型排行图 + 占比饼图 + 年度趋势 + 类型统计表 |
| 开发商洞察 | /developers | 开发商 Top20 + 游戏/好评率双轴图 + 开发商排名表 |
| 价格分析 | /price | 价格分布 + 免费/付费对比 + 价格-评分散点图 + 价格区间表 |

## API 接口

| 端点 | 说明 |
|------|------|
| /api/overview | 市场总览数据 + KPI |
| /api/charts | 全部 Plotly 图表 JSON |
| /api/games | 游戏列表（支持 search/genre/price 筛选 + 分页） |
| /api/games/id | 游戏详情 |
| /api/genres | 类型分析数据 |
| /api/developers | 开发商排行数据 |
| /api/price | 价格分析数据 |
| /api/ratings | 评价分析 + 相关性矩阵 |
| /api/trends | 发行趋势数据 |
| /api/genre_list | 全类型列表 |

## 数据字段

| 字段 | 类型 | 说明 |
|------|------|------|
| app_id | int | Steam 唯一标识 |
| name | str | 游戏名称 |
| release_date | date | 发行日期 |
| price | float | 价格 (USD) |
| positive_ratings | int | 好评数 |
| negative_ratings | int | 差评数 |
| average_playtime | float | 平均游玩时长 (分钟) |
| median_playtime | float | 中位数游玩时长 |
| owners | int | 拥有者估算数 |
| developer | str | 开发商 |
| publisher | str | 发行商 |
| genres | str | 类型标签 (JSON 数组) |
| platforms | str | 支持平台 |
| metacritic_score | float | Metacritic 评分 |

## 扩展建议

- 接入真实 Steam API 获取实时数据
- 增加推荐算法模块（协同过滤）
- 部署到云服务器（Flask + Nginx）
- 替换为 Spark/Polars 处理百万级数据
- 增加用户评论 NLP 情感分析
