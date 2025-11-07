"""PostgreSQL数据库管理器 - 生产环境版本"""

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor, execute_batch
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
from contextlib import contextmanager
import pandas as pd

logger = logging.getLogger(__name__)

class PostgresDBManager:
    """
    PostgreSQL数据库管理器
    
    特性:
    - 连接池管理 (线程安全)
    - 批量操作优化
    - 事务管理
    - 性能监控
    """
    
    def __init__(self, config: Dict):
        """
        初始化PostgreSQL连接池
        
        Args:
            config: 数据库配置
                {
                    'host': 'rds-endpoint.amazonaws.com',
                    'port': 5432,
                    'database': 'matformppo',
                    'user': 'admin',
                    'password': 'password',
                    'minconn': 2,
                    'maxconn': 20
                }
        """
        self.config = config
        
        try:
            self.pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=config.get('minconn', 2),
                maxconn=config.get('maxconn', 20),
                host=config['host'],
                port=config.get('port', 5432),
                database=config['database'],
                user=config['user'],
                password=config['password'],
                cursor_factory=RealDictCursor,
                connect_timeout=10
            )
            logger.info(f"PostgreSQL连接池已创建: {config['host']}:{config.get('port', 5432)}/{config['database']}")
        except Exception as e:
            logger.error(f"创建PostgreSQL连接池失败: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """从池中获取连接的上下文管理器"""
        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, commit=True):
        """获取游标的上下文管理器"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor
                if commit:
                    conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"数据库操作失败: {e}")
                raise
            finally:
                cursor.close()
    
    # ==========================================
    # 材料数据方法
    # ==========================================
    
    def insert_material(self, material_data: Dict) -> int:
        """
        插入单条材料数据
        
        Args:
            material_data: 材料属性字典
            
        Returns:
            插入的记录ID
        """
        query = """
        INSERT INTO materials (
            material_id, formula, formation_energy_per_atom,
            band_gap, density, volume, crystal_system, space_group
        ) VALUES (
            %(material_id)s, %(formula)s, %(formation_energy_per_atom)s,
            %(band_gap)s, %(density)s, %(volume)s, 
            %(crystal_system)s, %(space_group)s
        )
        ON CONFLICT (material_id) DO UPDATE SET
            formation_energy_per_atom = EXCLUDED.formation_energy_per_atom,
            updated_at = CURRENT_TIMESTAMP
        RETURNING id
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(query, material_data)
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def bulk_insert_materials(self, materials: List[Dict], batch_size: int = 1000) -> int:
        """
        批量插入材料数据 (性能优化)
        
        Args:
            materials: 材料数据列表
            batch_size: 批处理大小
            
        Returns:
            插入的记录数
        """
        query = """
        INSERT INTO materials (
            material_id, formula, formation_energy_per_atom,
            band_gap, density, volume, crystal_system, space_group
        ) VALUES (
            %(material_id)s, %(formula)s, %(formation_energy_per_atom)s,
            %(band_gap)s, %(density)s, %(volume)s,
            %(crystal_system)s, %(space_group)s
        )
        ON CONFLICT (material_id) DO NOTHING
        """
        
        with self.get_cursor() as cursor:
            execute_batch(cursor, query, materials, page_size=batch_size)
        
        logger.info(f"批量插入 {len(materials)} 条材料数据")
        return len(materials)
    
    def get_materials(self, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        """
        查询材料数据
        
        Args:
            limit: 返回记录数
            offset: 偏移量
            
        Returns:
            材料数据DataFrame
        """
        query = """
        SELECT * FROM materials 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
        """
        
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(limit, offset))
    
    def query_materials_by_formula(self, formula: str) -> pd.DataFrame:
        """按化学式查询材料"""
        query = """
        SELECT * FROM materials 
        WHERE formula ILIKE %s
        ORDER BY formation_energy_per_atom
        """
        
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(f"%{formula}%",))
    
    # ==========================================
    # 实验跟踪方法
    # ==========================================
    
    def start_experiment(self, experiment_id: str, pipeline_config: Dict,
                        episode_number: int, total_samples: int) -> int:
        """
        开始新实验
        
        Args:
            experiment_id: 实验唯一ID
            pipeline_config: 管道配置字典
            episode_number: PPO训练轮次
            total_samples: 数据集大小
            
        Returns:
            实验记录ID
        """
        query = """
        INSERT INTO experiments (
            experiment_id, pipeline_config, episode_number,
            started_at, status, total_samples
        ) VALUES (
            %s, %s, %s, CURRENT_TIMESTAMP, 'running', %s
        )
        RETURNING id
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (
                experiment_id,
                json.dumps(pipeline_config),
                episode_number,
                total_samples
            ))
            result = cursor.fetchone()
            logger.info(f"实验已开始: {experiment_id} (episode {episode_number})")
            return result['id'] if result else None
    
    def complete_experiment(self, experiment_id: str, training_time: float):
        """
        标记实验完成
        
        Args:
            experiment_id: 实验ID
            training_time: 训练时长(秒)
        """
        query = """
        UPDATE experiments 
        SET status = 'completed',
            completed_at = CURRENT_TIMESTAMP,
            training_time_seconds = %s
        WHERE experiment_id = %s
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (training_time, experiment_id))
        
        logger.info(f"实验已完成: {experiment_id} (用时 {training_time:.2f}秒)")
    
    def fail_experiment(self, experiment_id: str, error_message: str):
        """标记实验失败"""
        query = """
        UPDATE experiments 
        SET status = 'failed',
            completed_at = CURRENT_TIMESTAMP,
            notes = %s
        WHERE experiment_id = %s
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (error_message, experiment_id))
        
        logger.error(f"实验失败: {experiment_id} - {error_message}")
    
    # ==========================================
    # 结果记录方法
    # ==========================================
    
    def log_result(self, experiment_id: str, model_type: str,
                   metrics: Dict, hyperparameters: Dict = None) -> int:
        """
        记录模型训练结果
        
        Args:
            experiment_id: 实验ID
            model_type: 模型类型 ('rf', 'gbr', 'xgb', 'cat')
            metrics: 性能指标 {'mae': 0.15, 'rmse': 0.22, 'r2_score': 0.85}
            hyperparameters: 超参数配置
            
        Returns:
            结果记录ID
        """
        query = """
        INSERT INTO results (
            experiment_id, model_type, mae, rmse, r2_score,
            training_time_seconds, n_features, hyperparameters
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s
        )
        RETURNING id
        """
        
        with self.get_cursor() as cursor:
            cursor.execute(query, (
                experiment_id,
                model_type,
                metrics.get('mae'),
                metrics.get('rmse'),
                metrics.get('r2_score'),
                metrics.get('training_time'),
                metrics.get('n_features'),
                json.dumps(hyperparameters) if hyperparameters else None
            ))
            result = cursor.fetchone()
            logger.info(f"结果已记录: {model_type} in {experiment_id} (R²={metrics.get('r2_score', 0):.3f})")
            return result['id'] if result else None
    
    # ==========================================
    # 分析查询方法
    # ==========================================
    
    def get_best_models(self, limit: int = 10) -> pd.DataFrame:
        """获取最佳模型配置"""
        query = """
        SELECT * FROM v_best_models 
        ORDER BY r2_score DESC 
        LIMIT %s
        """
        
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(limit,))
    
    def get_experiment_stats(self) -> pd.DataFrame:
        """获取实验统计信息"""
        query = "SELECT * FROM v_experiment_stats ORDER BY experiment_id DESC"
        
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)
    
    def get_recent_experiments(self, days: int = 7) -> pd.DataFrame:
        """获取最近N天的实验"""
        query = """
        SELECT 
            e.*,
            COUNT(r.id) as num_results
        FROM experiments e
        LEFT JOIN results r ON e.experiment_id = r.experiment_id
        WHERE e.started_at >= CURRENT_DATE - INTERVAL '%s days'
        GROUP BY e.id
        ORDER BY e.started_at DESC
        """
        
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn, params=(days,))
    
    # ==========================================
    # 工具方法
    # ==========================================
    
    def get_table_count(self, table_name: str) -> int:
        """获取表记录数"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        
        with self.get_cursor(commit=False) as cursor:
            cursor.execute(query)
            result = cursor.fetchone()
            return result['count'] if result else 0
    
    def get_database_stats(self) -> Dict:
        """获取数据库统计信息"""
        return {
            'materials_count': self.get_table_count('materials'),
            'experiments_count': self.get_table_count('experiments'),
            'results_count': self.get_table_count('results'),
            'connection_pool': {
                'min_conn': self.config.get('minconn', 2),
                'max_conn': self.config.get('maxconn', 20)
            }
        }
    
    def close(self):
        """关闭连接池"""
        if self.pool:
            self.pool.closeall()
            logger.info("PostgreSQL连接池已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()

# 使用示例
if __name__ == "__main__":
    import os
    
    logging.basicConfig(level=logging.INFO)
    
    # 从环境变量读取配置
    config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'matformppo'),
        'user': os.getenv('POSTGRES_USER', 'admin'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
        'minconn': 2,
        'maxconn': 20
    }
    
    # 使用数据库
    with PostgresDBManager(config) as db:
        # 测试连接
        stats = db.get_database_stats()
        print(f"\n数据库统计:")
        print(f"  材料数: {stats['materials_count']}")
        print(f"  实验数: {stats['experiments_count']}")
        print(f"  结果数: {stats['results_count']}")
