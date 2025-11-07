"""
Database Manager for Materials Science Pipeline
Provides interface for storing and querying materials data, experiments, and results
"""

import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)

class MaterialsDBManager:
    """
    Database manager for materials science data engineering pipeline
    
    Handles:
    - Materials data storage and retrieval
    - Experiment tracking
    - Model results logging
    - Analytics queries
    """
    
    def __init__(self, db_path: str = "data/materials_pipeline.db"):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._connect()
        self._initialize_schema()
    
    def _connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        logger.info(f"Connected to database: {self.db_path}")
    
    def _initialize_schema(self):
        """Initialize database schema from SQL file"""
        schema_path = Path("sql/schema.sql")
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            self.conn.executescript(schema_sql)
            self.conn.commit()
            logger.info("Database schema initialized")
        else:
            logger.warning(f"Schema file not found: {schema_path}")
    
    # ==========================================
    # Materials Data Methods
    # ==========================================
    
    def insert_material(self, material_data: Dict) -> int:
        """
        Insert material data into database
        
        Args:
            material_data: Dictionary with material properties
            
        Returns:
            Inserted row ID
        """
        query = """
        INSERT INTO materials (
            material_id, formula, formation_energy_per_atom,
            band_gap, density, volume, crystal_system, space_group
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(material_id) DO UPDATE SET
            formation_energy_per_atom = excluded.formation_energy_per_atom,
            updated_at = CURRENT_TIMESTAMP
        """
        
        cursor = self.conn.execute(query, (
            material_data.get('material_id'),
            material_data.get('formula'),
            material_data.get('formation_energy_per_atom'),
            material_data.get('band_gap'),
            material_data.get('density'),
            material_data.get('volume'),
            material_data.get('crystal_system'),
            material_data.get('space_group')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_materials(self, limit: int = 100) -> pd.DataFrame:
        """
        Retrieve materials data
        
        Args:
            limit: Maximum number of rows to return
            
        Returns:
            DataFrame with materials data
        """
        query = f"SELECT * FROM materials ORDER BY created_at DESC LIMIT {limit}"
        return pd.read_sql_query(query, self.conn)
    
    # ==========================================
    # Experiment Tracking Methods
    # ==========================================
    
    def start_experiment(self, experiment_id: str, pipeline_config: Dict, 
                        episode_number: int, total_samples: int) -> int:
        """
        Log start of new experiment
        
        Args:
            experiment_id: Unique experiment identifier
            pipeline_config: Dictionary of pipeline configuration
            episode_number: PPO episode number
            total_samples: Number of samples in dataset
            
        Returns:
            Inserted row ID
        """
        query = """
        INSERT INTO experiments (
            experiment_id, pipeline_config, episode_number,
            started_at, status, total_samples
        ) VALUES (?, ?, ?, ?, 'running', ?)
        """
        
        cursor = self.conn.execute(query, (
            experiment_id,
            json.dumps(pipeline_config),
            episode_number,
            datetime.now().isoformat(),
            total_samples
        ))
        self.conn.commit()
        logger.info(f"Started experiment: {experiment_id}")
        return cursor.lastrowid
    
    def complete_experiment(self, experiment_id: str, training_time: float):
        """
        Mark experiment as completed
        
        Args:
            experiment_id: Experiment identifier
            training_time: Total training time in seconds
        """
        query = """
        UPDATE experiments 
        SET status = 'completed',
            completed_at = ?,
            training_time_seconds = ?
        WHERE experiment_id = ?
        """
        
        self.conn.execute(query, (
            datetime.now().isoformat(),
            training_time,
            experiment_id
        ))
        self.conn.commit()
        logger.info(f"Completed experiment: {experiment_id}")
    
    def fail_experiment(self, experiment_id: str, error_message: str):
        """Mark experiment as failed"""
        query = """
        UPDATE experiments 
        SET status = 'failed',
            completed_at = ?,
            notes = ?
        WHERE experiment_id = ?
        """
        
        self.conn.execute(query, (
            datetime.now().isoformat(),
            error_message,
            experiment_id
        ))
        self.conn.commit()
        logger.error(f"Failed experiment: {experiment_id} - {error_message}")
    
    # ==========================================
    # Results Logging Methods
    # ==========================================
    
    def log_result(self, experiment_id: str, model_type: str, 
                   metrics: Dict, hyperparameters: Dict = None) -> int:
        """
        Log model training results
        
        Args:
            experiment_id: Experiment identifier
            model_type: Model type ('rf', 'gbr', 'xgb', 'cat')
            metrics: Dictionary with mae, rmse, r2_score, etc.
            hyperparameters: Optional model hyperparameters
            
        Returns:
            Inserted row ID
        """
        query = """
        INSERT INTO results (
            experiment_id, model_type, mae, rmse, r2_score,
            training_time_seconds, n_features, hyperparameters
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = self.conn.execute(query, (
            experiment_id,
            model_type,
            metrics.get('mae'),
            metrics.get('rmse'),
            metrics.get('r2_score'),
            metrics.get('training_time'),
            metrics.get('n_features'),
            json.dumps(hyperparameters) if hyperparameters else None
        ))
        self.conn.commit()
        logger.info(f"Logged result for {model_type} in {experiment_id}")
        return cursor.lastrowid
    
    # ==========================================
    # Analytics Queries
    # ==========================================
    
    def get_best_models(self, limit: int = 10) -> pd.DataFrame:
        """Get best performing models across all experiments"""
        query = f"""
        SELECT * FROM v_best_models 
        ORDER BY r2_score DESC 
        LIMIT {limit}
        """
        return pd.read_sql_query(query, self.conn)
    
    def get_experiment_stats(self) -> pd.DataFrame:
        """Get summary statistics for all experiments"""
        query = "SELECT * FROM v_experiment_stats ORDER BY experiment_id DESC"
        return pd.read_sql_query(query, self.conn)
    
    def query_materials_by_formula(self, formula: str) -> pd.DataFrame:
        """Query materials by chemical formula"""
        query = "SELECT * FROM materials WHERE formula LIKE ?"
        return pd.read_sql_query(query, self.conn, params=(f"%{formula}%",))
    
    # ==========================================
    # Utility Methods
    # ==========================================
    
    def get_table_count(self, table_name: str) -> int:
        """Get row count for a table"""
        query = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.conn.execute(query).fetchone()
        return result['count']
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

# ==========================================
# Example Usage
# ==========================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    with MaterialsDBManager() as db:
        # Insert sample material
        material = {
            'material_id': 'mp-1234',
            'formula': 'Fe2O3',
            'formation_energy_per_atom': -2.5,
            'band_gap': 2.1,
            'density': 5.26,
            'crystal_system': 'trigonal',
            'space_group': 167
        }
        db.insert_material(material)
        
        # Start experiment
        exp_id = 'exp_test_001'
        config = {'N2': 'default', 'N6': 'variance', 'N8': 'rf'}
        db.start_experiment(exp_id, config, episode_number=1, total_samples=100)
        
        # Log result
        metrics = {
            'mae': 0.15,
            'rmse': 0.22,
            'r2_score': 0.85,
            'training_time': 10.5,
            'n_features': 50
        }
        db.log_result(exp_id, 'rf', metrics)
        
        # Complete experiment
        db.complete_experiment(exp_id, training_time=15.3)
        
        # Query data
        print("\nBest Models:")
        print(db.get_best_models())
        
        print("\nExperiment Stats:")
        print(db.get_experiment_stats())
