# HAIR GRECIA · Actividad 4 — Desarrollo de Aplicaciones Web II

## Requisitos

- Windows con **Python 3.10 o posterior** (sin instalar librerías adicionales para el backend).
- **Node.js 20.19+ o 22.12+**, npm e Internet **solo para instalar las dependencias del frontend** la primera vez.
- Visual Studio Code recomendado.

## Abrir en Windows

1. Descomprimir la carpeta `HAIR_GRECIA_ACTIVIDAD4` y abrirla en Visual Studio Code.
2. Abrir la terminal 1, desde la raíz del proyecto, ejecutar:

   ```powershell
   py backend/server.py
   ```

   Verificar en el navegador: `http://localhost:8000/api/health` (debe responder `status: ok`).
3. Abrir una **segunda** terminal, desde la raíz:

   ```powershell
   cd frontend
   npm install
   npm run dev
   ```

4. Abrir `http://localhost:5173`. Crear una cuenta de cliente, entrar y reservar una cita.
5. Para ejecutar las pruebas del servidor, desde la raíz, en una tercera terminal:

   ```powershell
   py -m unittest discover -s tests -v
   ```

**Nota:** la primera vez que se inicie el backend, creará `backend/hair_grecia.sqlite3` con los servicios y barberos de ejemplo. No subas este archivo a GitHub porque puede contener datos registrados durante las pruebas.

## Usuario administrador (opcional)

En **PowerShell**, configura dos variables de entorno *antes de iniciar* `py backend/server.py` por primera vez:

```powershell
$env:HAIR_ADMIN_EMAIL = 'admin@ejemplo.com'
$env:HAIR_ADMIN_PASSWORD = 'una-clave-unica-de-12-o-mas-caracteres'
py backend/server.py
```

No hay contraseña de administrador predeterminada. La cuenta permite abrir `Resumen` y ver todas las citas. Solo usar datos inventados durante las pruebas.

## Swagger / documentación REST

- Contrato OpenAPI en `docs/openapi.yaml`, editable en cualquier editor de texto.
- Puedes abrir el **Swagger Editor** en `https://editor.swagger.io/` e importar el YAML. Necesita conexión a Internet.
- También puedes usar `docs/swagger.html`: ejecuta `py -m http.server 8081` desde `docs/` y abre `http://localhost:8081/swagger.html`. La interfaz Swagger UI se descarga de CDN, por lo que necesita Internet.
- Con Swagger puedes probar primero `GET /services`, `GET /barbers`, `GET /availability`, y luego `POST /auth/register` y `POST /auth/login`. Pega el `token` del inicio de sesión en **Authorize** para usar las rutas protegidas.

## Estructura

```text
HAIR_GRECIA_ACTIVIDAD4/
  backend/server.py             API, control de horarios, SQLite y sesiones
  backend/.env.example          Ejemplo de variables (no se carga automáticamente)
  frontend/src/App.jsx          Rutas, pantallas y formularios
  frontend/src/AuthContext.jsx  Context API, useState, useContext, useEffect
  frontend/src/BookingContext.jsx  useReducer para el formulario de citas
  frontend/src/api.js           Axios e interceptor de token
  frontend/src/styles.css       Diseño adaptable a móviles
  frontend/public/img/         Fotografías optimizadas del HTML original
  docs/openapi.yaml             Contrato OpenAPI (Swagger)
  docs/swagger.html             Interfaz Swagger opcional
  tests/test_api.py             Pruebas automáticas con unittest
```

## Alcance y límites

**Incluye:** servicios, precios de referencia, equipo, consulta de disponibilidad, registro, inicio y cierre de sesión, reservas con prevención de solapamientos, cancelaciones, vista de citas propias y resumen administrativo. Los datos persisten en SQLite.

**No incluye todavía:** pasarela de pagos, mensajes por SMS/correo, recordatorios automáticos, predicción de tiempos de espera, calificaciones verificadas, administración completa de horarios, perfiles de barbero con acceso propio, pruebas de carga ni despliegue público.

**Seguridad:** se usan contraseñas derivadas con PBKDF2 y tokens aleatorios con expiración, pero **no es un sistema listo para producción**. Antes de tratar datos reales hay que añadir HTTPS, configuración segura, protección contra abusos, políticas de privacidad, consentimiento de tratamiento de datos, gestión de respaldos y revisión de riesgos de seguridad. El servidor de desarrollo solo escucha `127.0.0.1`.

## GitHub

1. Crear un repositorio vacío, por ejemplo, `hair-grecia-actividad4`.
2. Desde la carpeta raíz del proyecto:

   ```powershell
   git init
   git add .
   git commit -m "Actividad 4: React, API REST, Swagger y reservas"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/hair-grecia-actividad4.git
   git push -u origin main
   ```

   Sustituye `TU_USUARIO` por el usuario y nombre real del repositorio creado en GitHub. **No se creó ni publicó un repositorio automáticamente.**

