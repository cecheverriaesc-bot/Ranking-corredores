# 📋 Instrucciones de Implementación
## Sistema de Metas Personales para Corredores

---

## 🗄️ PASO 1: Crear Tabla en Base de Datos

Ejecuta el siguiente script SQL en la base de datos `assetplan_rentas`:

```bash
# Conéctate a la base de datos
mysql -h dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com \
      -u carlos.echeverria \
      -p \
      assetplan_rentas < scripts/create_goals_table.sql
```

O ejecuta manualmente el contenido de `scripts/create_goals_table.sql` en tu cliente MySQL.

---

## 🚀 PASO 2: Desplegar API Endpoint

El archivo `api/v4_goals.py` ya está creado. Solo necesitas hacer deploy en Vercel:

```bash
# Desde la carpeta del dashboard
cd ranking-corredores-rm---dashboard

# Ejecuta el script de sync (esto sube los cambios a Vercel)
../run_sync.bat
```

O haz deploy manual:
```bash
vercel --prod
```

---

## ✅ PASO 3: Verificar Funcionamiento

### 3.1 Testear API directamente

```bash
# Obtener metas del mes actual
curl "https://TU-DOMINIO.vercel.app/api/v4_goals?month=2026-02-01"

# Calcular meta sugerida para un corredor
curl "https://TU-DOMINIO.vercel.app/api/v4_goals/suggest?broker=Rosangela+Cirelli&month=2026-02-01"

# Guardar una meta (POST)
curl -X POST "https://TU-DOMINIO.vercel.app/api/v4_goals" \
  -H "Content-Type: application/json" \
  -d '{
    "broker_name": "Rosangela Cirelli",
    "goal_month": "2026-02-01",
    "personal_goal": 49,
    "commitment_comment": "Mi compromiso es contactar 20 leads por semana"
  }'
```

### 3.2 Verificar en el Dashboard

1. Abre el dashboard en tu navegador
2. Busca un corredor en la tabla de ranking
3. Haz clic en el botón **"Configurar"** o **"Editar Meta"** (columna "Mi Meta")
4. Debería abrirse el modal de configuración de metas

---

## 🎯 CARACTERÍSTICAS IMPLEMENTADAS

### 1. Modal de Configuración de Metas
- ✅ Meta sugerida calculada por IA (basada en histórico + proyección)
- ✅ Input para meta personalizada
- ✅ Campo de comentario/compromiso
- ✅ Visualización de progreso actual vs meta
- ✅ Animación de confetti al guardar
- ✅ Botón "Usar Meta Sugerida"

### 2. Columna "Mi Meta" en Ranking
- ✅ Botón para editar meta personal
- ✅ Muestra la meta configurada (si existe)
- ✅ Muestra comentario/compromiso debajo del botón
- ✅ Indicador visual si no hay meta configurada

### 3. Vista Laboratorio Estratégico
- ✅ Nueva columna "Meta Personal" en la matriz de asignación
- ✅ Tooltip con el compromiso del corredor al hacer hover
- ✅ Integración con datos de la API

### 4. API Endpoint `/api/v4_goals`
- ✅ GET: Obtener todas las metas del mes
- ✅ GET por corredor: `/api/v4_goals?month=2026-02-01&broker=Nombre`
- ✅ GET meta sugerida: `/api/v4_goals/suggest?broker=Nombre&month=2026-02-01`
- ✅ POST: Guardar/actualizar meta personal

---

## 📊 FÓRMULA DE META SUGERIDA

La meta sugerida se calcula con:

```
Meta Sugerida = (Promedio 3 meses * 0.4) + 
                (Rendimiento año anterior * 0.2) + 
                (Proyección ritmo actual * 0.4)
```

**Factores:**
- **Histórico (40%)**: Promedio de reservas últimos 3 meses
- **Año Anterior (20%)**: Mismo mes del año previo
- **Proyección (40%)**: Ritmo actual proyectado al fin del mes

**Niveles de Confianza:**
- **Alta**: ≥3 meses de datos históricos + datos año anterior
- **Media**: ≥2 meses de datos históricos
- **Baja**: Pocos datos, usa default o proyección

---

## 🎨 UX/UI IMPLEMENTADA

### Colores y Estados
| Elemento | Color | Estado |
|----------|-------|--------|
| Meta Sugerida | 🟡 Ámbar | Destacado |
| Meta Personal | 🩷 Rosa | Identificación |
| Progreso >100% | 🟢 Esmeralda | Cumplido |
| Progreso 70-99% | 🔵 Azul | En camino |
| Progreso <70% | ⚪ Gris | Inicial |

### Animaciones
- Confetti al guardar meta
- Pulse en progress bar cuando se completa
- Hover effects en botones
- Tooltips suaves con transición

---

## 🔧 ARCHIVOS CREADOS/MODIFICADOS

### Nuevos Archivos
```
├── api/v4_goals.py                          # API endpoint
├── components/GoalSettingModal.tsx          # Modal de configuración
└── scripts/create_goals_table.sql           # Script DB
```

### Archivos Modificados
```
├── App.tsx                                  # Integración modal + columna
├── components/SquadLaboratory.tsx           # Columna metas + compromisos
└── types.ts                                 # Interfaces TypeScript
```

---

## 📱 FLUJO DE USO

### Para el Corredor:
1. Ingresa al dashboard
2. Busca su nombre en el ranking
3. Hace clic en "Configurar" (columna Mi Meta)
4. Ve la meta sugerida por IA
5. Puede aceptar la sugerida o poner una personalizada
6. Escribe su compromiso (opcional)
7. Guarda y ve el progreso actualizado

### Para el Coordinador:
1. Ingresa al Laboratorio Estratégico
2. Ve la columna "Meta Personal" en la matriz
3. Hover en el ícono de mensaje para ver compromisos
4. Identifica corredores sin meta configurada
5. Puede hacer seguimiento personalizado

---

## ⚠️ CONSIDERACIONES

### Seguridad
- La API actual permite CORS abierto (`*`)
- No hay autenticación real (solo código secreto para Lab)
- **Recomendación**: Implementar autenticación por email/role

### Performance
- Las metas se cargan al cambiar de mes
- Cachea en el frontend para evitar llamadas repetidas
- **Recomendación**: Implementar SWR o React Query

### Datos
- La tabla `broker_goals` es independiente del ranking histórico
- Las metas no se borran al cambiar de mes
- **Recomendación**: Archivar metas de meses anteriores

---

## 🐛 TROUBLESHOOTING

### Error: "Failed to fetch"
```
Verifica que el API endpoint esté desplegado en Vercel
Revisa la consola del navegador para ver el error específico
```

### Error: "Table 'broker_goals' doesn't exist"
```
Ejecuta el script SQL en la base de datos assetplan_rentas
Verifica que tengas permisos de escritura
```

### El modal no abre
```
Verifica que el import de GoalSettingModal esté correcto
Revisa que no haya errores de TypeScript
```

### La meta sugerida no se calcula
```
Verifica que haya datos históricos en bi_assetplan
Revisa los logs del API endpoint en Vercel
```

---

## 📈 PRÓXIMAS MEJORAS SUGERIDAS

1. **Notificaciones Push/WhatsApp** cuando un corredor configura su meta
2. **Alertas automáticas** si el progreso está <50% a mitad de mes
3. **Gamificación**: Badges por cumplir metas consecutivas
4. **Comparativa**: Mostrar % de corredores con meta configurada
5. **Exportar**: PDF con metas y compromisos del squad
6. **Seguimiento**: Historial de metas por corredor (mes a mes)

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Ejecutar script SQL en `assetplan_rentas`
- [ ] Deploy del API endpoint `v4_goals.py`
- [ ] Verificar que el dashboard compile sin errores
- [ ] Testear flujo completo de configuración de meta
- [ ] Verificar que los compromisos se vean en el Laboratorio
- [ ] Validar cálculo de meta sugerida con datos reales
- [ ] Documentar proceso para corredores

---

## 📞 SOPORTE

Si encuentras errores, revisa:
1. Logs de Vercel: `vercel logs`
2. Consola del navegador (F12)
3. Errores de MySQL en la DB

---

**¡Listo! Tus corredores ahora pueden configurar sus metas personales y ver su progreso día a día.** 🎉
