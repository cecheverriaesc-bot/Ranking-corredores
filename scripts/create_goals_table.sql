-- ============================================
-- TABLA: broker_goals
-- Propósito: Almacenar metas personales mensuales
--            y comentarios/compromisos de corredores
-- ============================================

CREATE TABLE IF NOT EXISTS broker_goals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    
    -- Identificación del corredor
    broker_name VARCHAR(255) NOT NULL,
    broker_email VARCHAR(255),
    
    -- Período de la meta
    goal_month DATE NOT NULL,  -- Primer día del mes (ej: 2026-02-01)
    
    -- Meta personalizada
    personal_goal INT NOT NULL DEFAULT 0,
    
    -- Meta sugerida (calculada automáticamente)
    suggested_goal INT DEFAULT 0,
    
    -- Comentario/compromiso del corredor
    commitment_comment TEXT,
    
    -- Método de cálculo de la meta sugerida
    calculation_method VARCHAR(50) DEFAULT 'historical_avg',
    -- Opciones: 'historical_avg', 'projection', 'manual', 'coordinator_defined'
    
    -- Auditoría
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by VARCHAR(255) DEFAULT 'system',  -- 'system', 'broker', 'coordinator'
    
    -- Índices para búsquedas rápidas
    INDEX idx_broker_month (broker_name, goal_month),
    INDEX idx_goal_month (goal_month),
    INDEX idx_broker_email (broker_email)
    
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================
-- DATOS DE EJEMPLO (OPCIONAL)
-- ============================================
-- INSERT INTO broker_goals (broker_name, broker_email, goal_month, personal_goal, suggested_goal, commitment_comment, created_by)
-- VALUES 
--     ('Rosangela Cirelli', 'rosangela@example.com', '2026-02-01', 49, 45, 'Este mes me comprometo a mantener mi ritmo de 2 reservas/semana', 'broker'),
--     ('Juan Pérez', 'juan@example.com', '2026-02-01', 30, 35, 'Primera vez que supero las 30 reservas', 'broker');
