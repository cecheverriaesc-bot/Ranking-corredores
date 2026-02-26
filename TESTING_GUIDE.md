# 🧪 Guía de Testing

Esta carpeta contiene los tests del proyecto Ranking Corredores.

---

## 📁 Estructura

```
tests/
├── __tests__/
│   └── components/
│       └── Login.test.tsx      # Tests del componente Login
├── tests/
│   └── test_auth_api.py        # Tests de la API de auth
jest.config.js                   # Configuración de Jest
jest.setup.js                    # Setup de mocks
babel.config.json                # Configuración de Babel
```

---

## 🚀 Comandos Disponibles

```bash
# Correr todos los tests
npm test

# Correr tests en modo watch (desarrollo)
npm run test:watch

# Correr tests con coverage
npm run test:coverage

# Correr tests en CI (sin watch, con coverage)
npm run test:ci
```

---

## 📝 Tests Existentes

### Frontend (React)

#### Login.test.tsx
Tests para el componente de Login:

- ✅ Renderizado correcto del formulario
- ✅ Validación de email vacío
- ✅ Validación de contraseña vacía
- ✅ Validación de dominio de email
- ✅ Login exitoso con credenciales válidas
- ✅ Manejo de errores de autenticación
- ✅ Rate limiting (429)
- ✅ Errores de red
- ✅ Soporte para múltiples dominios
- ✅ Estado de loading

**Cobertura objetivo:** >80%

### Backend (Python)

#### test_auth_api.py
Tests para la API de autenticación:

- ✅ Hash de contraseñas
- ✅ Generación de tokens
- ✅ Validación de tokens
- ✅ Rate limiting
- ✅ CORS headers

**Cobertura objetivo:** >70%

---

## 📊 Coverage Actual

Para ver el coverage actual:

```bash
npm run test:coverage
```

Esto generará un reporte en `coverage/` que puedes abrir en tu navegador.

---

## 🔧 Escribiendo Nuevos Tests

### Componentes React

```typescript
// __tests__/components/MyComponent.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import MyComponent from '../../components/MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText(/texto/i)).toBeInTheDocument();
  });
  
  it('should handle click', async () => {
    const handleClick = jest.fn();
    render(<MyComponent onClick={handleClick} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalled();
  });
});
```

### APIs Python

```python
# tests/test_my_api.py
import unittest
from api.my_api import handler

class TestMyAPI(unittest.TestCase):
    def test_get_endpoint(self):
        """Test GET endpoint"""
        # Tu código de test aquí
        pass
```

---

## 🎯 Buenas Prácticas

### 1. Nombres Descriptivos
```typescript
// ❌ MAL
it('should work', () => {});

// ✅ BIEN
it('should show error when email is invalid', () => {});
```

### 2. Tests Aislados
```typescript
beforeEach(() => {
  jest.clearAllMocks();
  localStorage.clear();
});
```

### 3. Usar Data Attributes
```typescript
// ❌ MAL
screen.getByText('Click me');

// ✅ BIEN
screen.getByTestId('submit-button');
```

### 4. Testear Comportamiento, No Implementación
```typescript
// ❌ MAL
expect(state.count).toBe(5);

// ✅ BIEN
expect(screen.getByText('Count: 5')).toBeInTheDocument();
```

---

## 🔍 Debugging Tests

### Ver logs detallados
```bash
npm test -- --verbose
```

### Correr un test específico
```bash
npm test -- Login.test.tsx
```

### Ver coverage de un archivo
```bash
npm run test:coverage -- --collectCoverageFrom='components/Login.tsx'
```

---

## 📈 Métricas de Calidad

### Mínimos Requeridos
- **Statements:** >50%
- **Branches:** >50%
- **Functions:** >50%
- **Lines:** >50%

### Objetivo Ideal
- **Statements:** >80%
- **Branches:** >70%
- **Functions:** >80%
- **Lines:** >80%

---

## 🐛 Troubleshooting

### Error: "Cannot use import statement outside a module"
**Solución:** Verificar que `babel.config.json` esté configurado correctamente.

### Error: "window is not defined"
**Solución:** Asegurar que `testEnvironment: 'jsdom'` esté en `jest.config.js`.

### Error: "localStorage is not defined"
**Solución:** El mock de localStorage está en `jest.setup.js`.

---

## 📚 Recursos

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library](https://testing-library.com/react)
- [Testing Library Best Practices](https://testing-library.com/docs/react-testing-library/intro/)

---

**Última actualización:** Febrero 2026
