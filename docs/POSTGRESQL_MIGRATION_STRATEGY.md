# PostgreSQL 数据库迁移策略文档
# PostgreSQL Migration Strategy for MatFormPPO

## 概述

本文档描述了从 SQLite 开发环境迁移到 PostgreSQL 生产环境的完整策略。

## 当前状态

### SQLite 实现（开发环境）
- **数据库文件**: `data/materials_pipeline.db`
- **表结构**: 3个核心表（materials, experiments, results）
- **连接管理**: `sql/db_manager.py` - MaterialsDBManager 类
- **索引**: 10+ 个优化索引
- **视图**: 2个分析视图

### 目标架构（生产环境）
- **数据库**: Amazon RDS PostgreSQL 15.x
- **连接池**: pgbouncer / SQLAlchemy 连接池
- **高可用性**: Multi-AZ 部署
- **备份策略**: 自动备份 + 时间点恢复
- **性能**: 读写分离、查询缓存

## 迁移步骤

### 第一阶段：环境准备（1周）

#### 1. 安装 PostgreSQL 依赖
```bash
pip install psycopg2-binary sqlalchemy alembic
```

#### 2. 创建数据库连接配置
```python
# config.py 添加
DATABASE_TYPE = os.getenv("DB_TYPE", "sqlite")  # sqlite 或 postgresql
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "matformppo")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

if DATABASE_TYPE == "postgresql":
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
else:
    DATABASE_URL = f"sqlite:///{PROC_DIR}/materials_pipeline.db"
```

#### 3. 使用 Alembic 管理数据库迁移
```bash
# 初始化 Alembic
alembic init alembic

# 创建初始迁移
alembic revision --autogenerate -m "初始数据库模式"

# 应用迁移
alembic upgrade head
```

### 第二阶段：模式转换（3-5天）

#### 1. PostgreSQL 特定优化

**SQLite → PostgreSQL 类型映射**:
| SQLite | PostgreSQL | 说明 |
|--------|-----------|------|
| INTEGER | SERIAL / INTEGER | 自增主键 |
| TEXT | VARCHAR(n) / TEXT | 文本字段 |
| REAL | DOUBLE PRECISION | 浮点数 |
| TIMESTAMP | TIMESTAMP WITH TIME ZONE | 时间戳 |

**修改后的 schema.sql（PostgreSQL 版本）**:
```sql
-- 材料数据表
CREATE TABLE IF NOT EXISTS materials (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(50) UNIQUE NOT NULL,
    formula VARCHAR(200) NOT NULL,
    formation_energy_per_atom DOUBLE PRECISION,
    band_gap DOUBLE PRECISION,
    density DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    crystal_system VARCHAR(50),
    space_group INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 索引优化（PostgreSQL 支持部分索引）
CREATE INDEX CONCURRENTLY idx_materials_formula ON materials(formula);
CREATE INDEX CONCURRENTLY idx_materials_formation_energy 
    ON materials(formation_energy_per_atom) WHERE formation_energy_per_atom IS NOT NULL;
```

#### 2. 触发器和函数

```sql
-- 自动更新 updated_at 字段
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_materials_updated_at
    BEFORE UPDATE ON materials
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 第三阶段：代码适配（1周）

#### 1. 更新 MaterialsDBManager

```python
# sql/db_manager.py 修改
import sqlalchemy as sa
from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

class MaterialsDBManager:
    def __init__(self, db_url: str = None):
        self.db_url = db_url or DATABASE_URL
        
        # 创建连接池
        if "postgresql" in self.db_url:
            self.engine = create_engine(
                self.db_url,
                poolclass=pool.QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # 连接健康检查
                echo=False
            )
        else:
            self.engine = create_engine(self.db_url)
        
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self):
        """上下文管理器获取数据库会话"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def insert_material(self, material_data: Dict):
        """插入材料数据（支持 PostgreSQL UPSERT）"""
        with self.get_session() as session:
            # PostgreSQL 使用 ON CONFLICT
            query = """
            INSERT INTO materials (
                material_id, formula, formation_energy_per_atom,
                band_gap, density, volume, crystal_system, space_group
            ) VALUES (:material_id, :formula, :formation_energy, 
                      :band_gap, :density, :volume, :crystal_system, :space_group)
            ON CONFLICT (material_id) DO UPDATE SET
                formation_energy_per_atom = EXCLUDED.formation_energy_per_atom,
                updated_at = CURRENT_TIMESTAMP
            """
            session.execute(sa.text(query), material_data)
```

### 第四阶段：数据迁移（2-3天）

#### 1. 导出 SQLite 数据

```python
# scripts/export_sqlite_data.py
import sqlite3
import pandas as pd

def export_sqlite_to_csv():
    """导出 SQLite 数据到 CSV"""
    conn = sqlite3.connect('data/materials_pipeline.db')
    
    # 导出每个表
    tables = ['materials', 'experiments', 'results']
    for table in tables:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        df.to_csv(f'data/migration/{table}.csv', index=False)
        print(f"导出 {table}: {len(df)} 条记录")
    
    conn.close()
```

#### 2. 导入到 PostgreSQL

```python
# scripts/import_to_postgresql.py
import pandas as pd
from sqlalchemy import create_engine

def import_csv_to_postgresql():
    """从 CSV 导入数据到 PostgreSQL"""
    engine = create_engine(DATABASE_URL)
    
    tables = ['materials', 'experiments', 'results']
    for table in tables:
        df = pd.read_csv(f'data/migration/{table}.csv')
        df.to_sql(table, engine, if_exists='append', index=False)
        print(f"导入 {table}: {len(df)} 条记录")
```

### 第五阶段：性能优化（1周）

#### 1. 查询优化

```sql
-- 创建物化视图加速复杂查询
CREATE MATERIALIZED VIEW mv_best_models AS
SELECT 
    e.experiment_id,
    e.episode_number,
    r.model_type,
    r.r2_score,
    r.mae,
    e.pipeline_config,
    e.started_at
FROM results r
JOIN experiments e ON r.experiment_id = e.experiment_id
WHERE r.r2_score = (
    SELECT MAX(r2_score) 
    FROM results 
    WHERE experiment_id = r.experiment_id
);

-- 定期刷新
CREATE INDEX ON mv_best_models(r2_score DESC);
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_best_models;
```

#### 2. 连接池配置

```python
# 生产环境连接池设置
engine = create_engine(
    DATABASE_URL,
    pool_size=20,              # 基础连接数
    max_overflow=40,           # 最大溢出连接
    pool_timeout=30,           # 连接超时（秒）
    pool_recycle=3600,         # 连接回收时间
    pool_pre_ping=True,        # 连接健康检查
    echo_pool=True             # 连接池调试日志
)
```

### 第六阶段：测试验证（1周）

#### 1. 功能测试

```python
# tests/test_postgresql_migration.py
def test_database_connection():
    """测试数据库连接"""
    with MaterialsDBManager() as db:
        count = db.get_table_count('materials')
        assert count >= 0

def test_data_integrity():
    """测试数据完整性"""
    # 对比 SQLite 和 PostgreSQL 记录数
    sqlite_count = get_sqlite_record_count()
    postgres_count = get_postgres_record_count()
    assert sqlite_count == postgres_count

def test_query_performance():
    """测试查询性能"""
    start_time = time.time()
    results = db.get_best_models(limit=100)
    duration = time.time() - start_time
    assert duration < 1.0  # 查询应在1秒内完成
```

#### 2. 性能基准测试

```python
# scripts/benchmark_databases.py
def benchmark_query_performance():
    """对比 SQLite 和 PostgreSQL 查询性能"""
    queries = [
        "SELECT * FROM materials LIMIT 1000",
        "SELECT * FROM experiments WHERE status = 'completed'",
        "SELECT * FROM v_best_models ORDER BY r2_score DESC LIMIT 10"
    ]
    
    for query in queries:
        # SQLite 性能
        sqlite_time = measure_query_time(sqlite_conn, query)
        
        # PostgreSQL 性能
        postgres_time = measure_query_time(postgres_conn, query)
        
        improvement = (sqlite_time - postgres_time) / sqlite_time * 100
        print(f"查询: {query[:50]}...")
        print(f"  SQLite: {sqlite_time:.3f}s")
        print(f"  PostgreSQL: {postgres_time:.3f}s")
        print(f"  性能提升: {improvement:.1f}%")
```

## 部署计划

### 阶段性部署

1. **第1周**: 开发环境部署 PostgreSQL
2. **第2-3周**: 测试环境迁移和验证
3. **第4周**: 生产环境迁移（低峰时段）

### 回滚策略

```bash
# 如果迁移失败，快速回滚到 SQLite
export DB_TYPE=sqlite
python scripts/train_ppo.py
```

### 监控指标

- 数据库连接数
- 查询响应时间（P50, P95, P99）
- 慢查询日志
- 数据库 CPU/内存使用率
- 锁等待时间

## 成本估算

### AWS RDS PostgreSQL 成本（月度）

| 配置 | 实例类型 | 存储 | 月成本 |
|------|---------|------|--------|
| 开发环境 | db.t3.small | 20GB | $25 |
| 测试环境 | db.t3.medium | 50GB | $60 |
| 生产环境 | db.r5.large (Multi-AZ) | 100GB | $320 |

## 预期收益

### 性能提升
- 查询性能提升: **60-80%**
- 并发连接支持: **10x** （SQLite: 1个写入, PostgreSQL: 数百并发）
- 事务处理能力: **20x**

### 可扩展性
- 支持读写分离
- 支持水平分片（未来）
- 支持全文搜索（GIN 索引）
- 支持 JSON 字段查询

### 可靠性
- 自动备份和时间点恢复
- Multi-AZ 高可用性（99.95% SLA）
- 自动故障转移

## 风险评估

| 风险 | 影响 | 可能性 | 缓解措施 |
|-----|------|--------|---------|
| 数据迁移失败 | 高 | 低 | 完整备份 + 测试验证 |
| 性能下降 | 中 | 低 | 性能基准测试 + 索引优化 |
| 成本超支 | 低 | 中 | 使用预留实例 + 监控 |
| 停机时间 | 高 | 低 | 蓝绿部署 + 快速回滚 |

## 时间表

| 周次 | 任务 | 负责人 | 状态 |
|-----|------|--------|------|
| W1 | 环境准备 + 依赖安装 | DevOps | 进行中 |
| W2 | 模式转换 + 代码适配 | Backend | 计划中 |
| W3 | 数据迁移 + 验证 | DataEng | 计划中 |
| W4 | 性能优化 | Backend | 计划中 |
| W5 | 测试 + 部署 | 全团队 | 计划中 |

## 参考资源

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [AWS RDS 最佳实践](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html)
- [Alembic 数据库迁移](https://alembic.sqlalchemy.org/)
