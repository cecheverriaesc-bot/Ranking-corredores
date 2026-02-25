<div align="center">
  <img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
  
  # 🏆 Ranking de Corredores Assetplan 2026
  
  Dashboard interactivo para el seguimiento del rendimiento de corredores
  
  [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-org/ranking-corredores-rm)
</div>

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación Local](#-instalación-local)
- [Despliegue en Vercel](#-despliegue-en-vercel)
- [Configuración de Variables de Entorno](#-configuración-de-variables-de-entorno)
- [API Endpoints](#-api-endpoints)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Solución de Problemas](#-solución-de-problemas)

---

## ✨ Características

- 📊 **Ranking en Tiempo Real**: Visualiza el rendimiento de corredores actualizado
- 🎯 **Metas Personales**: Sistema de gestión de metas individuales
- 📈 **Estadísticas Diarias**: Seguimiento día a día del rendimiento
- 🏅 **Podium**: Top 3 destacados del mes
- 📱 **Diseño Responsivo**: Funciona en desktop y móvil
- 🔐 **Autenticación**: Login por email corporativo
- 🎨 **UI Moderna**: Animaciones y efectos visuales mejorados

---

## 🛠️ Requisitos Previos

- **Node.js** >= 18.0.0
- **Python** >= 3.9 (para APIs)
- **npm** o **yarn**
- Cuenta en **Vercel** (para despliegue)

---

## 💻 Instalación Local

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd ranking-corredores-rm---dashboard
```

### 2. Instalar dependencias

```bash
npm install
```

### 3. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DB_HOST=dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com
DB_PORT=3306
DB_NAME=assetplan_rentas
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
```

### 4. Ejecutar en modo desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:3000`

### 5. Build de producción

```bash
npm run build
npm run preview
```

---

## 🚀 Despliegue en Vercel

### Opción 1: Deploy Automático (Recomendado)

1. Haz clic en el botón **"Deploy with Vercel"** más arriba
2. Conecta tu repositorio de GitHub
3. Configura las variables de entorno en Vercel
4. Haz clic en **"Deploy"**

### Opción 2: Deploy Manual con Vercel CLI

```bash
# Instalar Vercel CLI
npm install -g vercel

# Login a Vercel
vercel login

# Deploy (primera vez)
vercel

# Deploy a producción
vercel --prod
```

### Configurar Variables de Entorno en Vercel

Ve a tu proyecto en Vercel → **Settings** → **Environment Variables** y agrega:

| Variable | Valor | Entornos |
|----------|-------|----------|
| `DB_HOST` | `dp-prod-bi.cluster-ro-czb4wih3oe0v.us-east-1.rds.amazonaws.com` | Production, Preview, Development |
| `DB_PORT` | `3306` | All |
| `DB_NAME` | `assetplan_rentas` | All |
| `DB_USER` | `tu_usuario` | All |
| `DB_PASSWORD` | `tu_contraseña` | All |

---

## 🔌 API Endpoints

### Ranking Data

```
GET /api/ranking?year=2026&month=2
```

**Respuesta:**
```json
{
  "ranking": [...],
  "others": [...],
  "daily_stats": [...],
  "last_update": "25/02/2026 22:04",
  "total_2025_ytd": 1234,
  "reservation_goal": 2174,
  "contract_goal": 2066
}
```

### Broker Goals

```
GET /api/v4_goals?month=2026-02&broker=Nombre+Apellido
POST /api/v4_goals
```

### Capacity Analysis

```
GET /api/v3_capacity?month=2026-02
```

### Intelligence

```
GET /api/v5_intelligence?month=2026-02
```

---

## 📁 Estructura del Proyecto

```
ranking-corredores-rm---dashboard/
├── api/                      # Python API endpoints
│   ├── ranking.py           # API unificada de ranking
│   ├── v2_ranking.py        # API legacy de ranking
│   ├── v3_capacity.py       # Análisis de capacidad
│   ├── v4_goals.py          # Gestión de metas
│   └── v5_intelligence.py   # Business intelligence
├── components/               # Componentes React
│   ├── SquadLaboratory.tsx
│   ├── StrategicLab.tsx
│   ├── GoalSettingModal.tsx
│   └── Login.tsx
├── public/                   # Assets estáticos
│   └── logo_white.png
├── .env                      # Variables de entorno (no commitear)
├── .env.local                # Variables locales
├── constants.ts              # Datos estáticos del dashboard
├── types.ts                  # Tipos TypeScript
├── App.tsx                   # Componente principal
├── index.tsx                 # Entry point
├── index.css                 # Estilos globales
├── package.json              # Dependencias Node
├── requirements.txt          # Dependencias Python
├── vercel.json               # Configuración Vercel
└── vite.config.ts            # Configuración Vite
```

---

## 🔧 Solución de Problemas

### Error: "Cannot connect to database"

1. Verifica que las variables de entorno estén configuradas correctamente
2. Asegúrate de que tu IP tenga acceso a la base de datos RDS
3. Verifica las credenciales en AWS RDS

### Error: "Python module not found"

```bash
# Instalar dependencias de Python
pip install -r requirements.txt
```

### Error de build en Vercel

1. Verifica que `package.json` tenga el script `vercel-build`
2. Revisa los logs de build en el dashboard de Vercel
3. Asegúrate de que `requirements.txt` esté en la raíz del proyecto

### API retorna 500 Error

1. Revisa los logs de funciones en Vercel
2. Verifica la conexión a la base de datos
3. Comprueba que los queries SQL sean correctos

---

## 📊 Actualización de Datos

Los datos se actualizan automáticamente desde:
- **assetplan_rentas**: Reservas, leads, agendas
- **bi_assetplan**: Contratos y datos históricos

La frecuencia de actualización depende de la sincronización de las bases de datos.

---

## 🔐 Seguridad

- Las credenciales de base de datos **NUNCA** deben commitearse
- Usa variables de entorno en Vercel
- El archivo `.env` está en `.gitignore`
- Los endpoints de API requieren CORS configurado

---

## 📞 Soporte

Para problemas o consultas:
1. Revisa este README
2. Verifica los logs en Vercel
3. Contacta al equipo de desarrollo

---

<div align="center">
  <strong>Assetplan © 2026 - Ranking de Corredores</strong>
</div>
