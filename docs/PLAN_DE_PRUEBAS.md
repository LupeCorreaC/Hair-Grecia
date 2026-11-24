# HAIR GRECIA — Plan de pruebas de la actividad 4

Este documento separa **pruebas que ya fueron ejecutadas** de **pruebas manuales pendientes** para que el equipo no confunda la presencia de código con una verificación completa.

## 1. Pruebas automatizadas del servidor (ejecutadas)

Desde la raíz del proyecto:

```powershell
py -m unittest discover -s tests -v
```

Resultado observado durante la preparación de la actividad: **6 pruebas, 6 aprobadas**.

Se revisaron servicios y barberos, horarios libres, domingo cerrado, reserva de una franja, rechazo de una reserva superpuesta, cancelación, datos inválidos, usuarios no autorizados, acceso a citas privadas, estadísticas de administración y cierre de sesión.

## 2. Pruebas manuales del front-end (pendientes de ejecutar en Windows)

Marca cada punto cuando lo compruebes en el navegador:

- [ ] **React / navegación:** se abren Inicio, Servicios, Equipo y Reservar. Al volver atrás no desaparece el encabezado.
- [ ] **useState / formulario:** al crear una cuenta, el mensaje de éxito aparece sin actualizar toda la página.
- [ ] **useContext / sesión:** al ingresar, aparecen Mis citas y Salir. Al salir, desaparecen y Mis citas vuelve a solicitar inicio de sesión.
- [ ] **useEffect / disponibilidad:** al cambiar el servicio, la fecha o el profesional, se actualiza la lista de horarios.
- [ ] **useReducer / selección:** al cambiar el barbero, se borra la hora que se había seleccionado.
- [ ] **Axios / errores:** al apagar el back-end, aparece un mensaje comprensible en lugar de una pantalla en blanco.
- [ ] **Reservas reales:** una cita confirmada aparece en Mis citas. Al cancelarla, su estado cambia.
- [ ] **Conflictos:** si dos clientes intentan reservar la misma hora, uno recibe aviso de hora no disponible y debe escoger otra.
- [ ] **Interfaz móvil:** comprobar funcionamiento en una pantalla angosta (por ejemplo, 390 px) y facilidad para abrir el menú.
- [ ] **Accesibilidad básica:** usar teclado Tab y Enter, comprobar enfoque visible y que cada control tenga un texto explicativo.
- [ ] **Swagger:** cargar `docs/openapi.yaml` en Swagger Editor, probar GET /services y comprobar las respuestas.
- [ ] **Build:** ejecutar `npm run build` y verificar que se cree `frontend/dist/` sin errores.

## 3. Pruebas recomendadas para una versión posterior

No se ha probado rendimiento en múltiples conexiones, accesibilidad con lector de pantalla, recuperación de contraseñas, correo/SMS, cifrado HTTPS ni despliegue público. Antes de usar datos reales hay que realizar una evaluación de seguridad y privacidad.
