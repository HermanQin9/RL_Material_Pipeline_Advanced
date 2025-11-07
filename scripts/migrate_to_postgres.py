#!/usr/bin/env python3
"""
SQLite到PostgreSQL数据迁移工具
用于将开发环境数据迁移到生产PostgreSQL数据库
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_batch, RealDictCursor
import logging
import json
from pathlib import Path
from typing import Dict, List
import argparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseMigrator:
    """数据库迁移工具"""
    
    def __init__(self, sqlite_path: str, postgres_config: Dict):
        """
        初始化迁移器
        
        Args:
            sqlite_path: SQLite数据库文件路径
            postgres_config: PostgreSQL连接配置
        """
        self.sqlite_path = sqlite_path
        self.postgres_config = postgres_config
        
        # 连接SQLite
        logger.info(f"连接SQLite: {sqlite_path}")
        self.sqlite_conn = sqlite3.connect(sqlite_path)
        self.sqlite_conn.row_factory = sqlite3.Row
        
        # 连接PostgreSQL
        logger.info(f"连接PostgreSQL: {postgres_config['host']}:{postgres_config['port']}")
        self.pg_conn = psycopg2.connect(**postgres_config)
        self.pg_conn.autocommit = False
    
    def get_table_count(self, conn, table_name: str) -> int:
        """获取表记录数"""
        if isinstance(conn, sqlite3.Connection):
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        else:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
    
    def migrate_materials(self, batch_size: int = 1000) -> int:
        """
        迁移materials表
        
        Args:
            batch_size: 批处理大小
            
        Returns:
            迁移的记录数
        """
        logger.info("开始迁移materials表...")
        
        # 从SQLite读取
        sqlite_cursor = self.sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT * FROM materials")
        
        # PostgreSQL插入查询
        pg_cursor = self.pg_conn.cursor()
        insert_query = """
        INSERT INTO materials (
            id, material_id, formula, formation_energy_per_atom,
            band_gap, density, volume, crystal_system, space_group,
            created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (material_id) DO UPDATE SET
            formation_energy_per_atom = EXCLUDED.formation_energy_per_atom,
            updated_at = CURRENT_TIMESTAMP
        """
        
        total_rows = 0
        batch = []
        
        while True:
            rows = sqlite_cursor.fetchmany(batch_size)
            if not rows:
                break
            
            batch = [tuple(row) for row in rows]
            execute_batch(pg_cursor, insert_query, batch)
            
            total_rows += len(batch)
            logger.info(f"  已迁移 {total_rows} 条材料记录")
        
        self.pg_conn.commit()
        logger.info(f"materials表迁移完成: 总计 {total_rows} 条记录")
        
        return total_rows
    
    def migrate_experiments(self, batch_size: int = 500) -> int:
        """
        迁移experiments表
        
        Args:
            batch_size: 批处理大小
            
        Returns:
            迁移的记录数
        """
        logger.info("开始迁移experiments表...")
        
        sqlite_cursor = self.sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT * FROM experiments")
        
        pg_cursor = self.pg_conn.cursor()
        insert_query = """
        INSERT INTO experiments (
            id, experiment_id, pipeline_config, episode_number,
            started_at, completed_at, status, total_samples,
            training_time_seconds, notes
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (experiment_id) DO NOTHING
        """
        
        total_rows = 0
        batch = []
        
        while True:
            rows = sqlite_cursor.fetchmany(batch_size)
            if not rows:
                break
            
            batch = [tuple(row) for row in rows]
            execute_batch(pg_cursor, insert_query, batch)
            
            total_rows += len(batch)
            logger.info(f"  已迁移 {total_rows} 条实验记录")
        
        self.pg_conn.commit()
        logger.info(f"experiments表迁移完成: 总计 {total_rows} 条记录")
        
        return total_rows
    
    def migrate_results(self, batch_size: int = 1000) -> int:
        """
        迁移results表
        
        Args:
            batch_size: 批处理大小
            
        Returns:
            迁移的记录数
        """
        logger.info("开始迁移results表...")
        
        sqlite_cursor = self.sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT * FROM results")
        
        pg_cursor = self.pg_conn.cursor()
        insert_query = """
        INSERT INTO results (
            id, experiment_id, model_type, mae, rmse, r2_score,
            training_time_seconds, n_features, hyperparameters, created_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT DO NOTHING
        """
        
        total_rows = 0
        batch = []
        
        while True:
            rows = sqlite_cursor.fetchmany(batch_size)
            if not rows:
                break
            
            batch = [tuple(row) for row in rows]
            execute_batch(pg_cursor, insert_query, batch)
            
            total_rows += len(batch)
            logger.info(f"  已迁移 {total_rows} 条结果记录")
        
        self.pg_conn.commit()
        logger.info(f"results表迁移完成: 总计 {total_rows} 条记录")
        
        return total_rows
    
    def verify_migration(self) -> bool:
        """
        验证迁移完整性
        
        Returns:
            验证是否通过
        """
        logger.info("验证迁移结果...")
        
        tables = ['materials', 'experiments', 'results']
        all_match = True
        
        for table in tables:
            sqlite_count = self.get_table_count(self.sqlite_conn, table)
            pg_count = self.get_table_count(self.pg_conn, table)
            
            if sqlite_count == pg_count:
                logger.info(f"✓ {table}: SQLite={sqlite_count}, PostgreSQL={pg_count} - 匹配")
            else:
                logger.error(f"✗ {table}: SQLite={sqlite_count}, PostgreSQL={pg_count} - 不匹配!")
                all_match = False
        
        return all_match
    
    def migrate_all(self, verify: bool = True) -> bool:
        """
        执行完整迁移
        
        Args:
            verify: 是否验证迁移结果
            
        Returns:
            迁移是否成功
        """
        try:
            # 迁移所有表
            self.migrate_materials()
            self.migrate_experiments()
            self.migrate_results()
            
            # 验证
            if verify:
                if self.verify_migration():
                    logger.info("✓ 数据迁移验证通过")
                    return True
                else:
                    logger.error("✗ 数据迁移验证失败")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"迁移失败: {e}")
            self.pg_conn.rollback()
            return False
    
    def close(self):
        """关闭数据库连接"""
        self.sqlite_conn.close()
        self.pg_conn.close()
        logger.info("数据库连接已关闭")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='SQLite到PostgreSQL数据迁移工具')
    parser.add_argument('--sqlite-path', default='data/materials_pipeline.db',
                       help='SQLite数据库路径')
    parser.add_argument('--pg-host', required=True, help='PostgreSQL主机地址')
    parser.add_argument('--pg-port', type=int, default=5432, help='PostgreSQL端口')
    parser.add_argument('--pg-database', default='matformppo', help='PostgreSQL数据库名')
    parser.add_argument('--pg-user', default='admin', help='PostgreSQL用户名')
    parser.add_argument('--pg-password', required=True, help='PostgreSQL密码')
    parser.add_argument('--batch-size', type=int, default=1000, help='批处理大小')
    parser.add_argument('--no-verify', action='store_true', help='跳过验证')
    
    args = parser.parse_args()
    
    # PostgreSQL配置
    postgres_config = {
        'host': args.pg_host,
        'port': args.pg_port,
        'database': args.pg_database,
        'user': args.pg_user,
        'password': args.pg_password
    }
    
    # 执行迁移
    migrator = DatabaseMigrator(args.sqlite_path, postgres_config)
    
    try:
        success = migrator.migrate_all(verify=not args.no_verify)
        if success:
            logger.info("=" * 60)
            logger.info("数据迁移成功完成!")
            logger.info("=" * 60)
        else:
            logger.error("数据迁移失败")
            exit(1)
    finally:
        migrator.close()

if __name__ == "__main__":
    main()
