<?php
/**
 * Script para crear la tabla broker_goals
 * Ejecutar desde el navegador: https://tu-dominio.com/create_goals_table.php
 * 
 * IMPORTANTE: Eliminar este archivo después de usarlo por seguridad.
 */

// Configuración de la base de datos
$host = 'dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com';
$db = 'assetplan_rentas';
$user = 'carlos.echeverria';
$pass = 'JS5tyLBSMBdAdzAQ9r6UF2g7';
$port = 3306;

header('Content-Type: text/html; charset=utf-8');
?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crear Tabla broker_goals</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; background: #101622; color: #e2e8f0; }
        .success { background: #166534; padding: 20px; border-radius: 12px; margin: 20px 0; }
        .error { background: #991b1b; padding: 20px; border-radius: 12px; margin: 20px 0; }
        .info { background: #1e40af; padding: 20px; border-radius: 12px; margin: 20px 0; }
        h1 { color: #3b82f6; }
        code { background: #1e293b; padding: 2px 8px; border-radius: 4px; }
        pre { background: #1e293b; padding: 15px; border-radius: 8px; overflow-x: auto; }
        .btn { display: inline-block; padding: 12px 24px; background: #3b82f6; color: white; text-decoration: none; border-radius: 8px; margin: 10px 5px; }
        .btn:hover { background: #2563eb; }
    </style>
</head>
<body>
    <h1>🗄️ Creación de Tabla broker_goals</h1>
    
    <?php
    try {
        // Crear conexión
        $dsn = "mysql:host=$host;port=$port;dbname=$db;charset=utf8mb4";
        $options = [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ];
        
        echo "<div class='info'>📡 Conectando a la base de datos...</div>";
        $pdo = new PDO($dsn, $user, $pass, $options);
        echo "<div class='success'>✅ Conexión exitosa a <code>$db</code></div>";
        
        // Leer el script SQL
        $sqlFile = __DIR__ . '/scripts/create_goals_table.sql';
        if (!file_exists($sqlFile)) {
            throw new Exception("No se encontró el archivo: $sqlFile");
        }
        
        $sql = file_get_contents($sqlFile);
        
        // Dividir en statements individuales
        $statements = array_filter(
            array_map('trim', explode(';', $sql)),
            function($stmt) {
                return !empty($stmt) && 
                       !preg_match('/^--/', $stmt) && 
                       !preg_match('/^\/\*/', $stmt);
            }
        );
        
        echo "<div class='info'>📋 Ejecutando " . count($statements) . " statements SQL...</div>";
        
        // Ejecutar cada statement
        $created = false;
        foreach ($statements as $statement) {
            if (stripos($statement, 'CREATE TABLE') !== false) {
                try {
                    $pdo->exec($statement);
                    $created = true;
                    echo "<div class='success'>✅ Tabla <code>broker_goals</code> creada exitosamente</div>";
                } catch (PDOException $e) {
                    if (strpos($e->getMessage(), 'already exists') !== false) {
                        echo "<div class='info'>ℹ️ La tabla <code>broker_goals</code> ya existe</div>";
                        $created = true;
                    } else {
                        throw $e;
                    }
                }
            }
        }
        
        if ($created) {
            // Verificar que la tabla existe
            $stmt = $pdo->query("SHOW TABLES LIKE 'broker_goals'");
            if ($stmt->rowCount() > 0) {
                echo "<div class='success'>";
                echo "<h2>🎉 ¡Tabla creada exitosamente!</h2>";
                echo "<p>La tabla <code>broker_goals</code> está lista para usarse en la base de datos <code>$db</code>.</p>";
                echo "<h3>Estructura de la tabla:</h3>";
                
                // Mostrar estructura
                $columns = $pdo->query("DESCRIBE broker_goals");
                echo "<table border='1' cellpadding='8' cellspacing='0' style='border-collapse: collapse; width: 100%; margin: 20px 0;'>";
                echo "<tr><th>Columna</th><th>Tipo</th><th>Nulo</th><th>Key</th><th>Default</th><th>Extra</th></tr>";
                foreach ($columns as $col) {
                    echo "<tr>";
                    echo "<td><code>{$col['Field']}</code></td>";
                    echo "<td><code>{$col['Type']}</code></td>";
                    echo "<td>{$col['Null']}</td>";
                    echo "<td>{$col['Key']}</td>";
                    echo "<td>" . ($col['Default'] ?? 'NULL') . "</td>";
                    echo "<td>{$col['Extra']}</td>";
                    echo "</tr>";
                }
                echo "</table>";
                
                echo "<h3>Próximos pasos:</h3>";
                echo "<ol>";
                echo "<li>✅ Tabla creada - ¡Listo!</li>";
                echo "<li>🌐 El API endpoint ya está desplegado en Vercel</li>";
                echo "<li>🎯 Prueba configurar una meta desde el dashboard</li>";
                echo "<li>🗑️ <strong>IMPORTANTE:</strong> Elimina este archivo después de usarlo</li>";
                echo "</ol>";
                
                echo "<div class='info'>";
                echo "<h4>📝 URLs:</h4>";
                echo "<ul>";
                echo "<li>Dashboard: <a href='https://ranking-2026.vercel.app' target='_blank'>https://ranking-2026.vercel.app</a></li>";
                echo "<li>API Goals: <code>https://ranking-2026.vercel.app/api/v4_goals</code></li>";
                echo "</ul>";
                echo "</div>";
            }
        }
        
    } catch (PDOException $e) {
        echo "<div class='error'>";
        echo "<h2>❌ Error de Base de Datos</h2>";
        echo "<p><strong>Mensaje:</strong> " . htmlspecialchars($e->getMessage()) . "</p>";
        echo "<p><strong>Código:</strong> " . $e->getCode() . "</p>";
        echo "<h3>Posibles causas:</h3>";
        echo "<ul>";
        echo "<li>Credenciales incorrectas</li>";
        echo "<li>Problemas de conexión con AWS RDS</li>";
        echo "<li>Permisos insuficientes</li>";
        echo "</ul>";
        echo "</div>";
    } catch (Exception $e) {
        echo "<div class='error'>";
        echo "<h2>❌ Error</h2>";
        echo "<p>" . htmlspecialchars($e->getMessage()) . "</p>";
        echo "</div>";
    }
    ?>
    
    <hr style="margin: 40px 0; border-color: #324467;">
    
    <div class="info">
        <h3>📚 Documentación:</h3>
        <ul>
            <li><a href="IMPLEMENTACION.md" target="_blank">IMPLEMENTACION.md</a> - Instrucciones técnicas</li>
            <li><a href="RESUMEN.md" target="_blank">RESUMEN.md</a> - Resumen ejecutivo</li>
            <li><a href="GUIA_CORREDORES.md" target="_blank">GUIA_CORREDORES.md</a> - Guía para corredores</li>
        </ul>
    </div>
    
    <div class="error" style="margin-top: 30px;">
        <h3>⚠️ SEGURIDAD</h3>
        <p><strong>Elimina este archivo inmediatamente después de usarlo.</strong></p>
        <p>Contiene credenciales de base de datos y no debe permanecer en el servidor.</p>
        <form method="post" onsubmit="return confirm('¿Estás seguro de eliminar este archivo?');">
            <input type="hidden" name="delete" value="1">
            <button type="submit" class="btn" style="background: #dc2626;">🗑️ Eliminar este archivo</button>
        </form>
        <?php
        if (isset($_POST['delete'])) {
            if (unlink(__FILE__)) {
                echo "<div class='success'>✅ Archivo eliminado correctamente</div>";
            }
        }
        ?>
    </div>
</body>
</html>
