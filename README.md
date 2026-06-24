# Steam 游戏大数据分析平台

> 大数据分析与应用课程 · 期末大作业  
> 基于 Kaggle 真实 Steam 数据集的全链路数据分析平台

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-1.1-000000?logo=flask)](https://flask.palletsprojects.com)
[![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?logo=pandas)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.6-3F4F75?logo=plotly)](https://plotly.com)
[![SQLite](https://img.shields.io/badge/SQLite-3.38-003B57?logo=sqlite)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 快速开始

```bash
# 克隆项目
git clone https://github.com/leon6657/steam-game-analysis-kaggle.git
cd steam-game-analysis-kaggle

# 安装依赖
pip install pandas numpy flask plotly

# 启动（首次自动生成数据库）
python run_server.py
```

浏览器打开 **http://127.0.0.1:5000**

---

## 项目概览

从 Kaggle 采集 **125,854 条** Steam 游戏原始记录，经清洗后入库 **124,637 款**游戏，构建了一个完整的"采集 → 存储 → 处理 → 分析 → 可视化"大数据应用闭环。

### 数据字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `app_id` | int | Steam 应用唯一标识 |
| `name` | str | 游戏名称 |
| `release_date` | date | 发行日期 |
| `price` | float | 当前价格 (USD) |
| `positive_ratings` | int | 好评数 |
| `negative_ratings` | int | 差评数 |
| `rating_score` | float | 好评率 (%) |
| `average_playtime` | float | 平均游玩时长（分钟） |
| `owners` | int | 拥有者估算数 |
| `developer` | str | 开发商 |
| `publisher` | str | 发行商 |
| `genres` | str | 游戏类型标签 |
| `platforms` | str | 支持平台 |
| `metacritic_score` | int | Metacritic 评分 |

---

## 技术栈

| 组件 | 选型 | 用途 |
|------|------|------|
| 数据处理 | Pandas + NumPy | 12 万条数据清洗、聚合与特征工程 |
| 数据存储 | SQLite | 零配置单文件数据库，支持索引 |
| 分析引擎 | Pandas GroupBy | 6 大维度交叉统计分析 |
| 可视化 | Plotly | 交互式图表（缩放 / 悬停 / 筛选） |
| Web 框架 | Flask + Jinja2 | RESTful API + 服务端模板渲染 |
| 前端 UI | Bootstrap 5 + Plotly.js | 响应式设计，5 页面仪表盘 |
| 数据来源 | Kaggle + Steam API | 124,637 款真实 Steam 游戏数据 |

---

## 六大分析模块

| 模块 | 分析内容 | 关键图表 |
|------|----------|----------|
| 市场总览 | 游戏总量、均价、总评价数、好评率 | KPI 指标卡 + 饼图 + 时序图 + 热力图 |
| 类型分析 | 类型排行、交叉对比、年度趋势 | 柱状图 + 堆叠趋势图 |
| 价格分析 | 价格分布、免费/付费对比、价格-好评率关系 | 直方图 + 饼图 + 气泡散点图 |
| 开发商洞察 | Top 15 开发商排名、游戏数量 vs 好评率 | 柱状图 + 双轴图 |
| 评价分析 | 好评率分布、特征相关性 | 分布直方图 + 相关性热力图 |
| 发行趋势 | 年度发行量、平台支持趋势 | 时序图 + 堆叠趋势图 |

---

## 仪表盘页面

| 页面 | 路由 | 功能 |
|------|------|------|
| 总览看板 | `/` | 7 个 KPI 指标 + 4 张核心图表 |
| 游戏探索 | `/games` | 搜索、筛选、分页浏览（2500+页），点击查看详情 |
| 类型分析 | `/genres` | Top 6 游戏类型 + 年度趋势 + 统计表 |
| 开发商洞察 | `/developers` | Top 15 开发商排名 + 双轴图 + 数据表 |
| 价格分析 | `/price` | 价格分布 + 免费/付费对比 + 价格-好评率散点图 |

---

## API 接口

| 端点 | 说明 |
|------|------|
| `GET /api/overview` | 市场总览 + KPI 指标 |
| `GET /api/charts` | 全部图表 JSON（预计算缓存） |
| `GET /api/games` | 游戏列表（支持 search、genre、price 筛选 + 分页） |
| `GET /api/games/<id>` | 游戏详情 |
| `GET /api/genres` | 类型分析数据 |
| `GET /api/developers` | 开发商排行（缓存） |
| `GET /api/price` | 价格分析数据 |
| `GET /api/ratings` | 评价分析 + 相关性矩阵 |
| `GET /api/trends` | 发行趋势数据 |
| `GET /api/genre_list` | 全类型列表（用于筛选下拉框） |

---

## 项目结构

```
steam-game-analysis/
├── data/
│   ├── raw/steam_games.csv       # 转换后数据集（14列，125,854条）
│   └── processed/steam.db        # SQLite 数据库（.gitignore 排除）
├── src/
│   ├── data_pipeline.py           # ETL 管道：加载、清洗、存储
│   ├── analyzer.py                # 6 大分析引擎
│   └── visualizer.py              # Plotly 图表生成
├── web/
│   ├── app.py                     # Flask 应用入口
│   ├── routes.py                  # RESTful API（10+ 接口）
│   ├── templates/                 # 5 个 HTML 仪表盘
│   └── static/css/style.css       # 自定义样式
├── run_server.py                  # 一键启动
├── README.md
└── .gitignore
```

---

## 开发说明

### 依赖安装

```bash
pip install pandas>=1.0 numpy>=1.19 flask>=1.1 plotly>=5.0
```

### 重新生成数据

SQLite 数据库（23MB）被 `.gitignore` 排除，首次启动自动从 CSV 生成。如需重新生成：

```bash
Remove-Item data/processed/steam.db
python run_server.py
```

### 使用 Kaggle 原始数据

如需从 Kaggle 原始数据集重新生成：

```bash
pip install kagglehub
python -c "import kagglehub; print(kagglehub.dataset_download('fronkongames/steam-games-dataset'))"
```

---

## 数据质量

Kaggle 原始数据集（fronkongames/steam-games-dataset）存在列偏移问题：部分游戏的长文本描述含换行符，导致 CSV 解析时部分行的列对齐错误。已通过以下方式缓解：

- 使用 pandas 以正确的引号解析方式读取
- 对正/负评价数列做错位检测与自动修正
- 好评率用 SQL `NULLIF` 防止除零错误
- 对特定游戏（如 Terraria）通过 Steam 官方 API 直接获取准确数据

---

## 扩展方向

- 接入 Steam 实时 API，获取最新游戏评分
- 增加协同过滤推荐算法
- 云服务器部署（Gunicorn + Nginx）
- 替换为 Spark / Polars 处理百万级数据
- 玩家评论 NLP 情感分析
- 接入 SteamSpy API 获取更精确的玩家数量
