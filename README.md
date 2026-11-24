# HAIR GRECIA · Actividad 4 — Desarrollo de Aplicaciones Web II


Aplicación web para gestionar las citas de una barbería, consultar servicios, conocer a los barberos y reservar horarios disponibles.

## Tecnologías utilizadas

- **Frontend:** ReactJS, Axios y React Router.
- **Backend:** Python y API REST.
- **Base de datos:** SQLite.
- **Documentación API:** OpenAPI y Swagger.

## Funcionalidades

- Consulta de servicios y barberos.
- Registro e inicio de sesión de usuarios.
- Consulta de horarios disponibles.
- Reserva y cancelación de citas.
- Administración de reservas.

## Instalación y ejecución

**Backend:**
```bash
python backend/server.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## Documentación

La documentación de la API se encuentra en `docs/openapi.yaml`.

## Estado del proyecto

Prototipo académico desarrollado con fines educativos para practicar la integración de frontend, backend y bases de datos.

## Autor

Proyecto académico – HAIR GRECIA.

## Estructura


HAIR_GRECIA
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

