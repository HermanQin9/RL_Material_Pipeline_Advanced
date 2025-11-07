-- Materials Science Data Warehouse Schema
-- Purpose: Store materials data, experiments, and results for analytics

-- ==========================================
-- Table 1: Materials Data
-- ==========================================
CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id TEXT UNIQUE NOT NULL,
    formula TEXT NOT NULL,
    formation_energy_per_atom REAL,
    band_gap REAL,
    density REAL,
    volume REAL,
    crystal_system TEXT,
    space_group INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_materials_formula ON materials(formula);
CREATE INDEX idx_materials_crystal_system ON materials(crystal_system);
CREATE INDEX idx_materials_formation_energy ON materials(formation_energy_per_atom);

-- ==========================================
-- Table 2: Pipeline Experiments
-- ==========================================
CREATE TABLE IF NOT EXISTS experiments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT UNIQUE NOT NULL,
    pipeline_config TEXT,  -- JSON string of node configuration
    episode_number INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    status TEXT CHECK(status IN ('running', 'completed', 'failed', 'cancelled')),
    total_samples INTEGER,
    training_time_seconds REAL,
    notes TEXT
);

CREATE INDEX idx_experiments_status ON experiments(status);
CREATE INDEX idx_experiments_episode ON experiments(episode_number);
CREATE INDEX idx_experiments_started_at ON experiments(started_at);

-- ==========================================
-- Table 3: Model Results
-- ==========================================
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    experiment_id TEXT NOT NULL,
    model_type TEXT NOT NULL,  -- 'rf', 'gbr', 'xgb', 'cat'
    mae REAL,
    rmse REAL,
    r2_score REAL,
    training_time_seconds REAL,
    n_features INTEGER,
    hyperparameters TEXT,  -- JSON string
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
);

CREATE INDEX idx_results_experiment ON results(experiment_id);
CREATE INDEX idx_results_model_type ON results(model_type);
CREATE INDEX idx_results_r2_score ON results(r2_score);

-- ==========================================
-- View: Best Models by Experiment
-- ==========================================
CREATE VIEW IF NOT EXISTS v_best_models AS
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

-- ==========================================
-- View: Experiment Summary Statistics
-- ==========================================
CREATE VIEW IF NOT EXISTS v_experiment_stats AS
SELECT 
    e.experiment_id,
    e.status,
    e.total_samples,
    COUNT(r.id) as num_models,
    AVG(r.r2_score) as avg_r2,
    MAX(r.r2_score) as best_r2,
    MIN(r.mae) as best_mae,
    e.training_time_seconds
FROM experiments e
LEFT JOIN results r ON e.experiment_id = r.experiment_id
GROUP BY e.experiment_id;
