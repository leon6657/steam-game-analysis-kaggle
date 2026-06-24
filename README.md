# Steam 游戏大数据分析平台

大数据分析与应用课程期末大作业。

一个完整的 Steam 游戏数据分析平台，基于 Kaggle 真实数据集，涵盖从数据采集、ETL 清洗、多维统计分析到交互式可视化仪表盘的全流程。

---

## 数据来源

本平台使用 Kaggle Steam Games Dataset（fronkongames 版本），包含 **125,854 条**原始 Steam 游戏记录。数据涵盖 14 个核心字段：

| 字段 | 说明 |
|------|------|
| app_id | Steam 应用唯一标识 |
| name | 游戏名称 |
| release_date | 发行日期 |
| price | 当前价格 (USD) |
| positive_ratings | 好评数 |
| negative_ratings | 差评数 |
| rating_score | 好评率 (%) |
| average_playtime | 平均游玩时长（分钟） |
| owners | 拥有者估算数 |
| developer | 开发商 |
| publisher | 发行商 |
| genres | 游戏类型标签 |
| platforms | 支持平台 |
| metacritic_score | Metacritic 评分 |

清洗后入库 **124,637 款**游戏。

---

## 项目结构

`
steam-game-analysis/
├── data/
│   ├── raw/steam_games.csv       # 转换后的游戏数据（14列，125,854条）
│   └── processed/steam.db        # SQLite 数据库（124,637条）
├── src/
│   ├── data_pipeline.py           # ETL 管道：加载/清洗/SQLite存储
│   ├── analyzer.py                # 6 大分析引擎
│   └── visualizer.py              # Plotly 图表生成
├── web/
│   ├── app.py                     # Flask 应用入口
│   ├── routes.py                  # RESTful API（10+接口）
│   ├── templates/                 # 5 个仪表盘页面
│   └── static/css/style.css       # 自定义样式
├── run_server.py                  # 一键启动
├── README.md
└── .gitignore
`

---

## 快速启动

`
cd steam-game-analysis
python run_server.py
`

首次启动会自动加载并清洗数据，等待输出 **分析就绪: 124637 条游戏数据** 后，浏览器打开 **http://127.0.0.1:5000**

---

## 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 数据处理 | Pandas + NumPy | 12万条数据清洗/聚合/特征工程 |
| 数据存储 | SQLite | 零配置，支持索引 |
| 分析引擎 | Pandas GroupBy | 6 大维度交叉分析 |
| 可视化 | Plotly | 交互式图表（缩放/悬停/筛选） |
| Web 框架 | Flask | 轻量 RESTful API |
| 前端 UI | Bootstrap 5 + Plotly.js | 响应式 5 页面仪表盘 |
| 数据源 | Kaggle + Steam API | 124,637 款真实游戏数据 |

---

## 六大分析模块

| 模块 | 分析内容 | 关键图表 |
|------|----------|----------|
| 市场总览 | 游戏总量/均价/总评价数/好评率 | KPI 指标卡 + 饼图 + 时序图 + 热力图 |
| 类型分析 | 类型排行/交叉对比/年度趋势 | 柱状图 + 趋势图 |
| 价格分析 | 价格分布/免费vs付费/价格-好评率关系 | 直方图 + 饼图 + 气泡散点图 |
| 开发商洞察 | Top 15开发商/游戏数量vs好评率 | 柱状图 + 双轴图 |
| 评价分析 | 好评率分布/特征相关性 | 分布直方图 + 相关性热力图 |
| 发行趋势 | 年度发行量/平台支持趋势 | 时序图 + 趋势图 |

---

## Web 页面

| 页面 | 路由 | 功能 |
|------|------|------|
| 总览看板 | / | 7 个 KPI + 4 张核心图表 |
| 游戏探索 | /games | 搜索/筛选/分页（2500+页），详情弹窗 |
| 类型分析 | /genres | Top 6 类型 + 年度趋势 + 统计表 |
| 开发商洞察 | /developers | Top 15 + 双轴图 + 排名表 |
| 价格分析 | /price | 分布 + 饼图 + 散点图 |

## API 接口

| 端点 | 说明 |
|------|------|
| /api/overview | 市场总览 + KPI |
| /api/charts | 全部图表 JSON |
| /api/games | 游戏列表（支持 search/genre/price 筛选+分页） |
| /api/games/<id> | 游戏详情 |
| /api/genres | 类型分析数据 |
| /api/developers | 开发商排行（缓存） |
| /api/price | 价格分析数据 |
| /api/ratings | 评价分析 + 相关性矩阵 |
| /api/trends | 发行趋势数据 |
| /api/genre_list | 全类型列表（用于筛选下拉框） |

---

## 本地开发

依赖：pandas / numpy / flask / plotly

重新生成数据：
`
Remove-Item data/processed/steam.db
python run_server.py
`

---

## 扩展方向

- 接入 Steam 实时 API
- 增加推荐算法
- 云服务器部署
- 替换为 Spark/Polars
- NLP 情感分析
- 接入 SteamSpy API
