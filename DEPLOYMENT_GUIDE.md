# 🚀 Guía de Despliegue - Vercel 2026

## ✅ Checklist Pre-Despliegue

### Archivos Configurados
- [x] `vercel.json` - Configuración de Vercel
- [x] `package.json` - Scripts y dependencias
- [x] `requirements.txt` - Dependencias de Python
- [x] `.env` - Variables de entorno (NO commitear)
- [x] `.gitignore` - Archivos ignorados
- [x] `api/ranking.py` - API unificada
- [x] `index.css` - Estilos mejorados
- [x] `README.md` - Documentación actualizada

---

## 📋 Pasos para Desplegar

### Paso 1: Preparar el Repositorio

```bash
# Navegar al directorio del proyecto
cd "c:\Users\assetplan\Desktop\Nueva carpeta (3)\Ranking Enero 2026\Gobernanza_Ranking_2026\ranking-corredores-rm---dashboard"

# Verificar que todo esté commiteado
git status

# Agregar cambios
git add .

# Crear commit
git commit -m "Preparar despliegue a Vercel - Mejoras de diseño y API"

# Push al repositorio
git push origin main
```

### Paso 2: Conectar con Vercel

#### Opción A: Desde Vercel Dashboard
1. Ir a https://vercel.com/dashboard
2. Click en **"Add New Project"**
3. Importar repositorio desde GitHub
4. Seleccionar el repositorio `ranking-corredores-rm`

#### Opción B: Usando Vercel CLI
```bash
# Instalar Vercel CLI globalmente
npm install -g vercel

# Login
vercel login

# Iniciar despliegue
vercel

# Seguir las instrucciones en terminal
```

### Paso 3: Configurar Variables de Entorno

En el dashboard de Vercel:
1. Ir a **Project Settings** → **Environment Variables**
2. Agregar las siguientes variables:

| Nombre | Valor | Ambientes |
|--------|-------|-----------|
| `DB_HOST` | `dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com` | ✅ Production ✅ Preview ✅ Development |
| `DB_PORT` | `3306` | ✅ Production ✅ Preview ✅ Development |
| `DB_NAME` | `assetplan_rentas` | ✅ Production ✅ Preview ✅ Development |
| `DB_USER` | `[TU_USUARIO]` | ✅ Production ✅ Preview ✅ Development |
| `DB_PASSWORD` | `[TU_CONTRASEÑA]` | ✅ Production ✅ Preview ✅ Development |

### Paso 4: Configurar Python Runtime

Vercel automáticamente detectará `requirements.txt` e instalará las dependencias de Python.

Verificar que en **Settings** → **Functions** esté configurado:
- **Runtime**: Python 3.9
- **Memory**: 1024 MB (recomendado para APIs con DB)

### Paso 5: Build y Deploy

```bash
# Deploy a producción
vercel --prod
```

O desde el dashboard de Vercel, hacer click en **"Deploy"**

---

## 🔍 Verificación Post-Despliegue

### 1. Verificar Frontend
- [ ] El sitio carga correctamente
- [ ] El logo se muestra
- [ ] Los estilos CSS funcionan
- [ ] Las animaciones se reproducen

### 2. Verificar APIs
```bash
# Testear endpoint de ranking
curl https://tu-proyecto.vercel.app/api/ranking?year=2026&month=2

# Testear endpoint de goals
curl https://tu-proyecto.vercel.app/api/v4_goals?month=2026-02

# Testear endpoint de capacity
curl https://tu-proyecto.vercel.app/api/v3_capacity?month=2026-02
```

### 3. Verificar Logs
- Ir a **Vercel Dashboard** → **Project** → **Deployments**
- Click en el deployment activo
- Revisar **Function Logs** para errores

---

## 🐛 Solución de Problemas Comunes

### Error: "Module not found: mysql.connector"

**Solución:** Asegurar que `requirements.txt` esté en la raíz del proyecto y contenga:
```
mysql-connector-python==8.3.0
```

### Error: "Database connection failed"

**Solución:**
1. Verificar variables de entorno en Vercel
2. Confirmar que la IP de Vercel tenga acceso a RDS
3. En AWS RDS, agregar Security Group para Vercel

### Error: "Build failed"

**Solución:**
```bash
# Testear build localmente
npm run build

# Ver errores de TypeScript
npx tsc --noEmit
```

### Error: CORS en APIs

**Solución:** Verificar que todas las APIs incluyan:
```python
self.send_header('Access-Control-Allow-Origin', '*')
```

---

## 📊 URLs Importantes

| Ambiente | URL |
|----------|-----|
| **Producción** | `https://ranking-2026.vercel.app` |
| **Preview** | `https://ranking-2026-git-branch.vercel.app` |
| **Dashboard** | `https://vercel.com/dashboard` |

---

## 🔄 Actualizaciones Futuras

### Para actualizar el deployment:

```bash
# Cambios locales
git add .
git commit -m "Descripción de cambios"
git push origin main

# Vercel detectará automáticamente y desplegará
```

### Deploy manual:
```bash
vercel --prod
```

---

## 📈 Monitoreo y Analytics

### Vercel Analytics
1. Ir a **Project** → **Analytics**
2. Habilitar **Web Analytics**
3. Habilitar **Speed Insights**

### Function Metrics
1. Ir a **Project** → **Settings** → **Functions**
2. Ver **Execution Duration**
3. Ver **Error Rate**

---

## 🔐 Seguridad

### Buenas Prácticas
- ✅ NUNCA commitear `.env` con credenciales
- ✅ Usar variables de entorno en Vercel
- ✅ Habilitar protección de contraseña si es necesario
- ✅ Revisar logs regularmente

### IPs Permitidas en RDS
Agregar las IPs de Vercel al Security Group de RDS:
- Ver IPs en: https://vercel.com/docs/concepts/projects/project-configuration#ip-addresses

---

## 📞 Soporte

### Recursos de Vercel
- [Documentación](https://vercel.com/docs)
- [Templates](https://vercel.com/templates)
- [Community](https://github.com/vercel/vercel/discussions)

### Contacto Interno
- Equipo de Desarrollo: [tu-email@assetplan.cl]

---

<div align="center">
  <strong>🚀 Deploy exitoso = Usuarios felices</strong>
</div>
