# Documentation Organization

## 📁 文档结构 / Documentation Structure

```
docs/
├── README.md                           # 本文件：文档导航
├── 10-NODE_ARCHITECTURE.md             # 核心架构文档
├── NODE_ARCHITECTURE_SUMMARY.md        # 架构总结
├── DATASET_INFO.md                     # 数据集信息
├── PPO_TRAINING_ANALYSIS.md            # PPO训练分析
├── PPO_VALIDATION_REPORT.md            # PPO验证报告
│
├── tutorials/                          # 教程文档（已整理）
│   ├── COMPLETE_TUTORIAL.py            # 完整教程和快速开始
│   ├── QUICK_REFERENCE_CARD.py         # 快速参考卡
│   ├── DOCUMENTATION_INDEX.py          # 文档索引
│   ├── VIEW_DOCUMENTATION.py           # 文档查看器
│   ├── GNN_FLOWCHART_AND_DECISION_TREE.py      # GNN流程图
│   ├── GNN_PPO_INTERACTION_DIAGRAM.py          # GNN+PPO交互图
│   ├── GNN_PURPOSE_AND_PPO_CHOICES.py          # GNN目的和PPO选择
│   ├── N4_GNN_INTEGRATION_INFO.py              # N4节点集成信息
│   └── PROJECT_COMPLETION_SUMMARY.py           # 项目完成总结
│
└── architecture/                       # 架构设计文档（预留）
    └── (future architecture designs)
```

## 🚀 快速开始

### 新手入门路线（20分钟）
1. `tutorials/QUICK_REFERENCE_CARD.py` (5分钟) - 快速了解系统
2. `tutorials/GNN_FLOWCHART_AND_DECISION_TREE.py` (8分钟) - 理解GNN工作原理
3. `tutorials/COMPLETE_TUTORIAL.py` (7分钟) - 完整教程

### 深入学习路线（1小时）
1. `10-NODE_ARCHITECTURE.md` - 核心架构设计
2. `tutorials/GNN_PPO_INTERACTION_DIAGRAM.py` - 系统交互细节
3. `PPO_TRAINING_ANALYSIS.md` - 训练分析

### 开发者参考
- `NODE_ARCHITECTURE_SUMMARY.md` - 节点架构快速参考
- `DATASET_INFO.md` - 数据集详情
- `tutorials/DOCUMENTATION_INDEX.py` - 完整文档索引

## 📊 文档分类

| 类别 | 文件 | 用途 |
|------|------|------|
| **核心架构** | `10-NODE_ARCHITECTURE.md` | 系统设计核心文档 |
| **快速参考** | `tutorials/QUICK_REFERENCE_CARD.py` | 5分钟速查 |
| **教程指南** | `tutorials/COMPLETE_TUTORIAL.py` | 完整学习路径 |
| **性能分析** | `PPO_TRAINING_ANALYSIS.md` | 训练性能报告 |
| **数据文档** | `DATASET_INFO.md` | 数据集说明 |

## 🔍 查找文档

### 我想了解...
- **GNN是什么？** → `tutorials/GNN_PURPOSE_AND_PPO_CHOICES.py`
- **系统怎么工作？** → `tutorials/GNN_PPO_INTERACTION_DIAGRAM.py`
- **快速入门** → `tutorials/QUICK_REFERENCE_CARD.py`
- **完整教程** → `tutorials/COMPLETE_TUTORIAL.py`
- **架构设计** → `10-NODE_ARCHITECTURE.md`
- **PPO训练** → `PPO_TRAINING_ANALYSIS.md`

## 📝 文档维护

### 已清理的冗余文件
- ❌ `README_GNN_PPO_SYSTEM.txt` - 删除（与README.md重复）
- ✅ 所有教程文档已移至 `docs/tutorials/`
- ✅ 所有测试文件已移至 `tests/`
- ✅ 架构文档已整理至 `docs/`

### 文档命名规范
- `.md` - Markdown文档（架构、设计）
- `.py` - Python文档（教程、可执行示例）
- `tutorials/` - 学习教程
- `architecture/` - 设计文档

