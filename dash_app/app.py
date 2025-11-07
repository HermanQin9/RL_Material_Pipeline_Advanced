#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时监控仪表盘应用
Real-time Monitoring Dashboard Application

使用 Plotly 和 Dash 构建的材料科学 ML 管线监控系统
Material Science ML Pipeline Monitoring System built with Plotly & Dash
"""

import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import json

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import plotly.express as px

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import LOG_DIR, MODEL_DIR

# 初始化 Dash 应用
app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
app.title = "MatFormPPO 监控仪表盘"

# 颜色主题
colors = {
    'background': '#1e1e1e',
    'text': '#ffffff',
    'primary': '#00d4ff',
    'secondary': '#ff6b6b',
    'success': '#51cf66',
    'warning': '#ffd43b',
}

# 应用布局
app.layout = html.Div(style={'backgroundColor': colors['background'], 'fontFamily': 'Arial, sans-serif'}, children=[
    
    # 标题栏
    html.Div(style={'padding': '20px', 'backgroundColor': '#2c2c2c'}, children=[
        html.H1(
            'MatFormPPO 实时监控仪表盘',
            style={'color': colors['primary'], 'textAlign': 'center', 'margin': '0'}
        ),
        html.P(
            'PPO 驱动的材料科学 AutoML 管线监控系统',
            style={'color': colors['text'], 'textAlign': 'center', 'margin': '10px 0 0 0'}
        ),
    ]),
    
    # 实时刷新设置
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # 每5秒更新一次
        n_intervals=0
    ),
    
    # 主要指标卡片
    html.Div(style={'padding': '20px'}, children=[
        html.Div(style={'display': 'grid', 'gridTemplateColumns': 'repeat(auto-fit, minmax(250px, 1fr))', 'gap': '20px', 'marginBottom': '20px'}, children=[
            
            # 训练状态卡片
            html.Div(style={'backgroundColor': '#2c2c2c', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'}, children=[
                html.H3('训练状态', style={'color': colors['text'], 'marginTop': '0'}),
                html.Div(id='training-status', children=[
                    html.P('等待数据加载...', style={'color': colors['text'], 'fontSize': '24px', 'fontWeight': 'bold'})
                ])
            ]),
            
            # 成功率卡片
            html.Div(style={'backgroundColor': '#2c2c2c', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'}, children=[
                html.H3('成功率', style={'color': colors['text'], 'marginTop': '0'}),
                html.Div(id='success-rate', children=[
                    html.P('计算中...', style={'color': colors['success'], 'fontSize': '24px', 'fontWeight': 'bold'})
                ])
            ]),
            
            # 平均奖励卡片
            html.Div(style={'backgroundColor': '#2c2c2c', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'}, children=[
                html.H3('平均奖励', style={'color': colors['text'], 'marginTop': '0'}),
                html.Div(id='avg-reward', children=[
                    html.P('计算中...', style={'color': colors['primary'], 'fontSize': '24px', 'fontWeight': 'bold'})
                ])
            ]),
            
            # 训练回合数卡片
            html.Div(style={'backgroundColor': '#2c2c2c', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'}, children=[
                html.H3('训练回合', style={'color': colors['text'], 'marginTop': '0'}),
                html.Div(id='episode-count', children=[
                    html.P('0', style={'color': colors['warning'], 'fontSize': '24px', 'fontWeight': 'bold'})
                ])
            ]),
        ]),
        
        # 学习曲线图表
        html.Div(style={'backgroundColor': '#2c2c2c', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)', 'marginBottom': '20px'}, children=[
            html.H3('PPO 学习曲线', style={'color': colors['text'], 'marginTop': '0'}),
            dcc.Graph(id='learning-curve')
        ]),
        
        # 奖励分布和回合长度
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '20px', 'marginBottom': '20px'}, children=[
            html.Div(style={'backgroundColor': '#2c2c2c', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'}, children=[
                html.H3('奖励分布', style={'color': colors['text'], 'marginTop': '0'}),
                dcc.Graph(id='reward-distribution')
            ]),
            html.Div(style={'backgroundColor': '#2c2c2c', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'}, children=[
                html.H3('回合长度趋势', style={'color': colors['text'], 'marginTop': '0'}),
                dcc.Graph(id='episode-length')
            ]),
        ]),
        
        # 模型性能对比
        html.Div(style={'backgroundColor': '#2c2c2c', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 4px 6px rgba(0,0,0,0.3)'}, children=[
            html.H3('模型性能对比', style={'color': colors['text'], 'marginTop': '0'}),
            dcc.Graph(id='model-comparison')
        ]),
    ]),
    
    # 页脚
    html.Div(style={'padding': '20px', 'textAlign': 'center', 'color': '#666'}, children=[
        html.P('MatFormPPO v2.0 | 多伦多大学夏季研究项目 2025')
    ])
])


# 回调函数：更新训练状态
@app.callback(
    [Output('training-status', 'children'),
     Output('success-rate', 'children'),
     Output('avg-reward', 'children'),
     Output('episode-count', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_metrics(n):
    """更新主要指标卡片"""
    try:
        # 查找最新的检查点
        model_files = list(MODEL_DIR.glob('ppo_agent*.pth'))
        if not model_files:
            return (
                html.P('未开始训练', style={'color': colors['warning'], 'fontSize': '24px', 'fontWeight': 'bold'}),
                html.P('N/A', style={'color': colors['text'], 'fontSize': '24px', 'fontWeight': 'bold'}),
                html.P('N/A', style={'color': colors['text'], 'fontSize': '24px', 'fontWeight': 'bold'}),
                html.P('0', style={'color': colors['warning'], 'fontSize': '24px', 'fontWeight': 'bold'})
            )
        
        latest_checkpoint = max(model_files, key=lambda p: p.stat().st_mtime)
        
        # 加载训练数据
        import torch
        checkpoint = torch.load(latest_checkpoint, map_location='cpu')
        
        episode_rewards = checkpoint.get('episode_rewards', [])
        episode_lengths = checkpoint.get('episode_lengths', [])
        
        if not episode_rewards:
            return (
                html.P('训练中...', style={'color': colors['primary'], 'fontSize': '24px', 'fontWeight': 'bold'}),
                html.P('计算中...', style={'color': colors['text'], 'fontSize': '24px', 'fontWeight': 'bold'}),
                html.P('计算中...', style={'color': colors['text'], 'fontSize': '24px', 'fontWeight': 'bold'}),
                html.P('0', style={'color': colors['warning'], 'fontSize': '24px', 'fontWeight': 'bold'})
            )
        
        # 计算指标
        total_episodes = len(episode_rewards)
        successful_episodes = sum(1 for r in episode_rewards if r > -0.95)
        success_rate = (successful_episodes / total_episodes * 100) if total_episodes > 0 else 0
        avg_reward = np.mean(episode_rewards) if episode_rewards else 0
        
        # 训练状态
        status_text = html.P('训练进行中', style={'color': colors['success'], 'fontSize': '24px', 'fontWeight': 'bold'})
        
        # 成功率
        success_color = colors['success'] if success_rate >= 70 else colors['warning'] if success_rate >= 50 else colors['secondary']
        success_text = html.P(f'{success_rate:.1f}%', style={'color': success_color, 'fontSize': '24px', 'fontWeight': 'bold'})
        
        # 平均奖励
        reward_color = colors['success'] if avg_reward > -0.5 else colors['warning'] if avg_reward > -0.8 else colors['secondary']
        reward_text = html.P(f'{avg_reward:.3f}', style={'color': reward_color, 'fontSize': '24px', 'fontWeight': 'bold'})
        
        # 回合数
        episode_text = html.P(str(total_episodes), style={'color': colors['primary'], 'fontSize': '24px', 'fontWeight': 'bold'})
        
        return status_text, success_text, reward_text, episode_text
        
    except Exception as e:
        error_msg = html.P(f'错误: {str(e)[:30]}', style={'color': colors['secondary'], 'fontSize': '14px'})
        return error_msg, error_msg, error_msg, error_msg


# 回调函数：更新学习曲线
@app.callback(
    Output('learning-curve', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_learning_curve(n):
    """更新PPO学习曲线"""
    try:
        model_files = list(MODEL_DIR.glob('ppo_agent*.pth'))
        if not model_files:
            return create_empty_figure('等待训练数据...')
        
        latest_checkpoint = max(model_files, key=lambda p: p.stat().st_mtime)
        
        import torch
        checkpoint = torch.load(latest_checkpoint, map_location='cpu')
        episode_rewards = checkpoint.get('episode_rewards', [])
        
        if not episode_rewards:
            return create_empty_figure('加载训练数据中...')
        
        # 创建学习曲线
        episodes = list(range(1, len(episode_rewards) + 1))
        
        # 计算移动平均
        window = min(10, len(episode_rewards) // 5) if len(episode_rewards) > 5 else 1
        if window > 1:
            moving_avg = pd.Series(episode_rewards).rolling(window=window, min_periods=1).mean()
        else:
            moving_avg = episode_rewards
        
        fig = go.Figure()
        
        # 原始奖励
        fig.add_trace(go.Scatter(
            x=episodes,
            y=episode_rewards,
            mode='lines+markers',
            name='原始奖励',
            line=dict(color=colors['primary'], width=1),
            marker=dict(size=4),
            opacity=0.5
        ))
        
        # 移动平均
        fig.add_trace(go.Scatter(
            x=episodes,
            y=moving_avg,
            mode='lines',
            name=f'移动平均 (窗口={window})',
            line=dict(color=colors['success'], width=3)
        ))
        
        # 成功阈值线
        fig.add_hline(y=-0.95, line_dash="dash", line_color=colors['secondary'], 
                     annotation_text="失败阈值", annotation_position="right")
        
        fig.update_layout(
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#2c2c2c',
            font=dict(color=colors['text']),
            xaxis_title='训练回合',
            yaxis_title='奖励值',
            hovermode='x unified',
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)'),
            margin=dict(l=40, r=20, t=20, b=40)
        )
        
        return fig
        
    except Exception as e:
        return create_empty_figure(f'错误: {str(e)}')


# 回调函数：更新奖励分布
@app.callback(
    Output('reward-distribution', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_reward_distribution(n):
    """更新奖励分布直方图"""
    try:
        model_files = list(MODEL_DIR.glob('ppo_agent*.pth'))
        if not model_files:
            return create_empty_figure('等待数据...')
        
        latest_checkpoint = max(model_files, key=lambda p: p.stat().st_mtime)
        
        import torch
        checkpoint = torch.load(latest_checkpoint, map_location='cpu')
        episode_rewards = checkpoint.get('episode_rewards', [])
        
        if not episode_rewards:
            return create_empty_figure('加载数据中...')
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=episode_rewards,
            nbinsx=30,
            marker_color=colors['primary'],
            opacity=0.75,
            name='奖励分布'
        ))
        
        fig.update_layout(
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#2c2c2c',
            font=dict(color=colors['text']),
            xaxis_title='奖励值',
            yaxis_title='频次',
            showlegend=False,
            margin=dict(l=40, r=20, t=20, b=40)
        )
        
        return fig
        
    except Exception as e:
        return create_empty_figure(f'错误: {str(e)}')


# 回调函数：更新回合长度
@app.callback(
    Output('episode-length', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_episode_length(n):
    """更新回合长度趋势"""
    try:
        model_files = list(MODEL_DIR.glob('ppo_agent*.pth'))
        if not model_files:
            return create_empty_figure('等待数据...')
        
        latest_checkpoint = max(model_files, key=lambda p: p.stat().st_mtime)
        
        import torch
        checkpoint = torch.load(latest_checkpoint, map_location='cpu')
        episode_lengths = checkpoint.get('episode_lengths', [])
        
        if not episode_lengths:
            return create_empty_figure('加载数据中...')
        
        episodes = list(range(1, len(episode_lengths) + 1))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=episodes,
            y=episode_lengths,
            mode='lines+markers',
            name='回合长度',
            line=dict(color=colors['warning'], width=2),
            marker=dict(size=6),
            fill='tozeroy',
            fillcolor='rgba(255, 212, 59, 0.2)'
        ))
        
        fig.update_layout(
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#2c2c2c',
            font=dict(color=colors['text']),
            xaxis_title='回合',
            yaxis_title='步数',
            showlegend=False,
            margin=dict(l=40, r=20, t=20, b=40)
        )
        
        return fig
        
    except Exception as e:
        return create_empty_figure(f'错误: {str(e)}')


# 回调函数：更新模型性能对比
@app.callback(
    Output('model-comparison', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_model_comparison(n):
    """更新模型性能对比图"""
    try:
        # 模拟模型性能数据（实际应从数据库或日志文件读取）
        models = ['Random Forest', 'XGBoost', 'CatBoost', 'Gradient Boosting']
        r2_scores = [0.87, 0.89, 0.88, 0.85]
        mae_scores = [0.15, 0.12, 0.13, 0.16]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='R² Score',
            x=models,
            y=r2_scores,
            marker_color=colors['success'],
            text=[f'{v:.3f}' for v in r2_scores],
            textposition='auto',
        ))
        
        fig.add_trace(go.Bar(
            name='MAE',
            x=models,
            y=mae_scores,
            marker_color=colors['secondary'],
            text=[f'{v:.3f}' for v in mae_scores],
            textposition='auto',
            yaxis='y2'
        ))
        
        fig.update_layout(
            plot_bgcolor='#1e1e1e',
            paper_bgcolor='#2c2c2c',
            font=dict(color=colors['text']),
            xaxis_title='模型类型',
            yaxis=dict(title='R² Score', side='left'),
            yaxis2=dict(title='MAE', side='right', overlaying='y'),
            barmode='group',
            legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0.5)'),
            margin=dict(l=40, r=40, t=20, b=40)
        )
        
        return fig
        
    except Exception as e:
        return create_empty_figure(f'错误: {str(e)}')


def create_empty_figure(message):
    """创建空图表并显示消息"""
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color=colors['text'])
    )
    fig.update_layout(
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#2c2c2c',
        xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    return fig


# 主程序入口
if __name__ == '__main__':
    print("=" * 60)
    print("启动 MatFormPPO 实时监控仪表盘")
    print("=" * 60)
    print(f"访问地址: http://localhost:8050")
    print(f"日志目录: {LOG_DIR}")
    print(f"模型目录: {MODEL_DIR}")
    print("=" * 60)
    
    # 启动服务器
    app.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )
