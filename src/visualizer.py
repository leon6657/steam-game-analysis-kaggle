"""
图表生成器：将分析结果转为 Plotly JSON
"""

import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

_TEMPLATE = "plotly_white"
_COLORS = px.colors.qualitative.Plotly


def _fig_to_json(fig):
    return json.loads(fig.to_json())


def _bar(x, y, title="", xl="", yl="", color=None):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=x, y=y, marker_color=color or _COLORS[0]))
    fig.update_layout(template=_TEMPLATE, title=title,
                      xaxis_title=xl, yaxis_title=yl,
                      margin=dict(l=40, r=20, t=40, b=60), height=400)
    fig.update_xaxes(tickangle=-45)
    fig.update_yaxes(tickformat=",")
    return _fig_to_json(fig)


def _pie(labels, values, title=""):
    if len(labels) > 6:
        top = 6
        top_labels = list(labels[:top])
        top_values = list(values[:top])
        top_labels.append("Other")
        top_values.append(sum(values[top:]))
        labels = top_labels
        values = top_values
    fig = go.Figure(data=[go.Pie(labels=labels, values=values,
                                  textinfo="label+percent",
                                  textfont=dict(size=11))])
    fig.update_layout(template=_TEMPLATE, title=title,
                      margin=dict(l=10, r=10, t=40, b=10), height=400,
                      showlegend=False)
    return _fig_to_json(fig)


def _line(df, x, y, color, title="", xl="", yl=""):
    fig = px.line(df, x=x, y=y, color=color, template=_TEMPLATE,
                  title=title, markers=True,
                  labels={x: xl, y: yl})
    fig.update_layout(margin=dict(l=40, r=20, t=40, b=40), height=400)
    return _fig_to_json(fig)


def _heatmap(z, x, y, title=""):
    fig = go.Figure(data=go.Heatmap(z=z, x=x, y=y,
                                     colorscale="YlOrRd",
                                     text=z, texttemplate="%{text}",
                                     textfont=dict(color="black", size=9)))
    fig.update_layout(template=_TEMPLATE, title=title,
                      margin=dict(l=100, r=20, t=40, b=100), height=500)
    return _fig_to_json(fig)


def genre_pie(data):
    return _pie([r["genre"] for r in data], [r["count"] for r in data],
                "游戏类型分布")


def yearly_releases_bar(data):
    return _bar([r["release_year"] for r in data],
                [r.get("total", r.get("count", 0)) for r in data],
                "每年游戏发行量", "年份", "发行数量", _COLORS[1])


def price_dist_bar(data):
    return _bar([r["range"] for r in data], [r["count"] for r in data],
                "价格区间分布", "价格区间", "游戏数量", _COLORS[2])


def price_rating_scatter(df):
    sample = df[df["price"] <= 20].sample(min(1500, len(df)))
    fig = px.scatter(sample, x="price", y="rating_score",
                     color="rating_score", size="owners",
                     hover_name="name", color_continuous_scale="RdBu_r",
                     template=_TEMPLATE,
                     title="价格 vs 好评率 (气泡大小=拥有者数)",
                     labels={"price": "价格 ($)", "rating_score": "好评率 (%)"},
                     opacity=0.8, size_max=45)
    fig.update_xaxes(range=[0, 20], dtick=5)
    fig.update_yaxes(range=[0, 100], dtick=20)
    fig.update_layout(margin=dict(l=50, r=20, t=40, b=60), height=420)
    return _fig_to_json(fig)


def genre_stats_chart(data):
    return _bar([r["genre"] for r in data], [r["count"] for r in data],
                "类型排行", "类型", "游戏数量", _COLORS[3])


def genre_trend_chart(data):
    if not data:
        return {}
    df = pd.DataFrame(data)
    return _line(df, "release_year", "count", "genre",
                 "热门类型年度趋势", "年份", "游戏数量")


def developer_bar(data):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[r["developer"] for r in data],
                         y=[r["game_count"] for r in data],
                         marker_color=_COLORS[4]))
    fig.update_layout(template=_TEMPLATE,
                      title="开发商 Top 20",
                      xaxis_title="开发商",
                      yaxis=dict(title="游戏数量", tickformat=","),
                      margin=dict(l=60, r=20, t=40, b=150), height=450)
    fig.update_xaxes(tickangle=-45)
    return _fig_to_json(fig)


def developer_rating_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[r["developer"] for r in data],
                         y=[r["game_count"] for r in data],
                         name="游戏数量", marker_color=_COLORS[4]))
    fig.add_trace(go.Scatter(x=[r["developer"] for r in data],
                             y=[r["pos_rate"] for r in data],
                             name="好评率 (%)", yaxis="y2",
                             mode="lines+markers", marker_color=_COLORS[7]))
    fig.update_layout(template=_TEMPLATE,
                      title="开发商游戏数量 vs 好评率",
                      xaxis_title="开发商",
                      yaxis=dict(title="游戏数量", tickformat=","),
                      yaxis2=dict(overlaying="y", side="right",
                                  title="好评率 (%)", range=[0, 105],
                                  tickformat=".0f",
                                  ticksuffix="%"),
                      margin=dict(l=50, r=50, t=30, b=150), height=450)
    fig.update_xaxes(tickangle=-45)
    return _fig_to_json(fig)


def rating_dist_bar(data):
    return _bar([r["rating_bucket"] for r in data],
                [r["count"] for r in data],
                "好评率分布", "好评率区间", "游戏数量", _COLORS[5])


def correlation_heatmap(data, variables):
    df = pd.DataFrame(data)
    if "variable" in df.columns:
        df = df.set_index("variable")
    z = df[variables].values if all(c in df.columns for c in variables) else df.values
    return _heatmap(z, variables, variables, "特征相关性热力图")


def platform_trend_chart(data):
    if not data:
        return {}
    df = pd.DataFrame(data)
    return _line(df, "release_year", "count", "platform_group",
                 "平台支持趋势", "年份", "游戏数量")


def free_vs_paid_chart(data):
    return _pie([r["label"] for r in data], [r["count"] for r in data],
                "免费 vs 付费游戏占比")


def all_charts(analyzer):
    charts = {}
    overview = analyzer.market_overview()
    charts["overview"] = {
        "metrics": {"total_games": overview["total_games"],
                    "avg_price": overview["avg_price"],
                    "total_ratings": overview["total_ratings"],
                    "overall_pos_rate": overview["overall_pos_rate"],
                    "free_games": overview["free_games"],
                    "paid_games": overview["paid_games"],
                    "avg_playtime": overview["avg_playtime"]},
        "genre_pie": genre_pie(overview["genre_distribution"]),
        "yearly_releases": yearly_releases_bar(overview["yearly_releases"]),
    }
    price = analyzer.price_analysis()
    charts["price"] = {
        "price_dist": price_dist_bar(price["price_distribution"]),
        "free_vs_paid": free_vs_paid_chart(price["free_vs_paid"]),
        "price_rating_scatter": price_rating_scatter(analyzer.df),
    }
    genre = analyzer.genre_analysis()
    charts["genres"] = {
        "genre_stats": genre_stats_chart(genre["genre_stats"]),
        "genre_trend": genre_trend_chart(genre["genre_trends"]),
    }
    dev = analyzer.developer_analysis()
    charts["developers"] = {
        "developer_bar": developer_bar(dev["top_developers"]),
        "developer_rating": developer_rating_chart(dev["top_developers"]),
    }
    rating = analyzer.rating_analysis()
    charts["rating"] = {
        "rating_dist": rating_dist_bar(rating["rating_distribution"]),
        "correlation_heatmap": correlation_heatmap(rating["correlation_matrix"],
                                                   rating["corr_variables"]),
    }
    trends = analyzer.release_trends()
    charts["trends"] = {
        "yearly_releases": yearly_releases_bar(trends["yearly_releases"]),
        "platform_trends": platform_trend_chart(trends["platform_trends"]),
    }
    return charts
