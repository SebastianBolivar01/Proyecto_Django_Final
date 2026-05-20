# Requirements Document

## Introduction

El **Sistema de Gestión Hospitalaria y Consultas Médicas** es una aplicación web que permite administrar de forma integral pacientes, médicos, citas médicas e historias clínicas. La plataforma está orientada a centros de salud y clínicas que necesitan digitalizar sus procesos administrativos y clínicos. Ofrece roles diferenciados (Administrador, Médico, Paciente), un dashboard con estadísticas visuales, exportación de reportes en PDF y Excel, y un sistema de autenticación seguro.

El sistema se construye con Django 5+ (Python 3.12+), PostgreSQL en producción, Bootstrap 5 para la interfaz y se despliega en Render o Railway.

---

## Glossary

- **Sistema**: La aplicación web "Sistema de Gestión Hospitalaria y Consultas Médicas".
- **Administrador**: Usuario con rol de administrador que tiene acceso completo a todas las funcionalidades del Sistema.
- **Médico**: Usuario con rol de médico que puede gestionar sus citas y editar historias clínicas de sus pacientes.
- **Paciente**: Usuario con rol de paciente que puede registrarse, solicitar citas y consultar su historial médico.
- **Cita**: Registro de una consulta médica programada entre un Paciente y un Médico en una fecha y hora específicas.
- **Historia_Clínica**: Registro médico asociado a un Paciente que contiene diagnósticos, tratamientos y notas clínicas.
- **Especialidad**: Categoría médica que agrupa a los Médicos según su área de práctica (e.g., Cardiología, Pediatría).
- **Dashboard**: Panel de control administrativo con estadísticas y gráficos del Sistema.
- **Reporte**: Documento exportable en formato PDF o Excel que contiene datos filtrados del Sistema.
- **Auth_System**: Módulo de autenticación del Sistema basado en Django Authentication.
- **Validator**: Componente del Sistema responsable de validar datos de entrada en formularios y modelos.
- **Scheduler**: Componente del Sistema responsable de gestionar la disponibilidad y reserva de Citas.
- **Notifier**: Componente del Sistema responsable de enviar notificaciones por correo electrónico.
- **Report_Generator**: Componente del Sistema responsable de generar exportaciones en PDF y Excel.
- **Chart_Engine**: Componente del Sistema responsable de proveer datos para los gráficos del Dashboard.

---

## Requirements

### Requirement 1: Autenticación y Gestión de Sesiones

**User Story:** Como usuario del sistema, quiero registrarme, iniciar sesión y cerrar sesión de forma segura, para que pueda acceder a las funcionalidades correspondientes a mi rol.

#### Acceptance Criteria

1. THE Auth_System SHALL permitir el registro de nuevos usuarios con los campos obligatorios: nombre (máx. 100 caracteres), apellido (máx. 100 caracteres), correo electrónico (formato válido, máx. 254 caracteres), contraseña (mínimo 8 caracteres) y rol seleccionado de la lista predefinida: Administrador, Médico o Paciente.
2. WHEN un usuario envía credenciales válidas, THE Auth_System SHALL iniciar una sesión autenticada y redirigir al Dashboard correspondiente a su rol en menos de 2 segundos.
3. IF un usuario envía credenciales inválidas, THEN THE Auth_System SHALL mostrar el mensaje genérico "Correo electrónico o contraseña incorrectos" sin indicar cuál campo es incorrecto.
4. IF un usuario falla la autenticación 5 veces consecutivas desde la misma cuenta, THEN THE Auth_System SHALL bloquear temporalmente el acceso a esa cuenta durante 15 minutos y mostrar un mensaje informando el tiempo de espera.
5. WHEN un usuario autenticado solicita cerrar sesión, THE Auth_System SHALL terminar la sesión activa e invalidar la cookie de sesión, y redirigir a la página de inicio de sesión.
6. WHEN un usuario solicita recuperación de contraseña con un correo registrado, THE Auth_System SHALL enviar un enlace de restablecimiento al correo electrónico proporcionado; dicho enlace expirará a las 24 horas de su generación.
7. IF un usuario no autenticado intenta acceder a una ruta protegida, THEN THE Auth_System SHALL redirigir al usuario a la página de inicio de sesión preservando la URL de destino como parámetro `next`.
8. THE Auth_System SHALL aplicar protección CSRF en todos los formularios del Sistema.
9. WHEN un usuario completa el registro, THE Auth_System SHALL almacenar la contraseña usando el algoritmo de hashing por defecto de Django (PBKDF2) sin guardar la contraseña en texto plano.
10. IF el correo electrónico proporcionado durante el registro ya existe en la base de datos, THEN THE Auth_System SHALL rechazar el registro y mostrar el mensaje "Este correo electrónico ya está registrado".
11. IF un usuario intenta usar un enlace de recuperación de contraseña expirado o inválido, THEN THE Auth_System SHALL mostrar el mensaje "El enlace de recuperación ha expirado o no es válido" y ofrecer la opción de solicitar un nuevo enlace.

---

### Requirement 2: Gestión de Roles y Permisos

**User Story:** Como administrador, quiero que cada rol tenga permisos diferenciados, para que los usuarios solo puedan acceder a las funcionalidades que les corresponden.

#### Acceptance Criteria

1. THE Sistema SHALL soportar exactamente tres roles: Administrador, Médico y Paciente.
2. WHILE un usuario tiene rol Administrador, THE Sistema SHALL permitirle acceso completo a todas las vistas, modelos y operaciones CRUD del Sistema.
3. WHILE un usuario tiene rol Médico, THE Sistema SHALL permitirle ver, crear, editar y eliminar únicamente las Citas asignadas a él, y crear y editar (sin eliminar) las Historias_Clínicas de sus propios Pacientes.
4. WHILE un usuario tiene rol Paciente, THE Sistema SHALL permitirle ver su propio perfil, solicitar y cancelar sus propias Citas, y consultar su propia Historia_Clínica en modo solo lectura.
5. IF un usuario intenta acceder a una vista o endpoint de API del servidor para la que no tiene permiso, THEN THE Sistema SHALL retornar una respuesta HTTP 403 y mostrar una página de acceso denegado.
6. THE Sistema SHALL aplicar verificación de permisos en el servidor para cada vista y endpoint protegido, independientemente de los controles de la interfaz de usuario.

---

### Requirement 3: Gestión de Pacientes

**User Story:** Como administrador, quiero gestionar el registro completo de pacientes, para que el sistema mantenga un directorio actualizado de todos los pacientes atendidos.

#### Acceptance Criteria

1. THE Sistema SHALL permitir crear un registro de Paciente con los campos obligatorios: nombre (máx. 100 caracteres), apellido (máx. 100 caracteres), fecha de nacimiento, género (selección de lista: Masculino, Femenino, Otro), número de identificación (único, máx. 20 caracteres), teléfono (máx. 20 caracteres) y correo electrónico (formato válido); y el campo opcional: dirección (máx. 255 caracteres).
2. WHEN un Administrador solicita la lista de Pacientes, THE Sistema SHALL mostrar los registros paginados con un máximo de 20 registros por página, ordenados por apellido de forma ascendente por defecto.
3. WHEN un Administrador ingresa un término de búsqueda de al menos 2 caracteres en el campo de búsqueda, THE Sistema SHALL retornar en ≤500ms únicamente los Pacientes cuyo nombre, apellido o número de identificación contengan el término, sin recargar la página completa.
4. WHEN un Administrador actualiza los datos de un Paciente y el formulario es válido, THE Sistema SHALL guardar los cambios y mostrar el mensaje de confirmación "Paciente actualizado correctamente".
5. IF el formulario de actualización contiene errores de validación, THEN THE Sistema SHALL retornar el formulario con mensajes de error específicos por campo sin guardar cambios.
6. IF el número de identificación de un Paciente ya existe en la base de datos, THEN THE Sistema SHALL rechazar el registro o actualización y mostrar el mensaje "Este número de identificación ya está registrado".
7. WHEN un Administrador solicita eliminar un Paciente, THE Sistema SHALL mostrar un diálogo de confirmación antes de ejecutar la eliminación.
8. WHEN la eliminación es confirmada y el Paciente no tiene dependencias, THE Sistema SHALL eliminar el registro y mostrar el mensaje "Paciente eliminado correctamente".
9. IF un Paciente tiene Citas o Historias_Clínicas asociadas, THEN THE Sistema SHALL impedir la eliminación y mostrar un mensaje indicando el número de Citas e Historias_Clínicas dependientes.

---

### Requirement 4: Gestión de Médicos y Especialidades

**User Story:** Como administrador, quiero gestionar el directorio de médicos y sus especialidades, para que los pacientes puedan ser asignados al médico correcto.

#### Acceptance Criteria

1. THE Sistema SHALL permitir crear un registro de Médico con los campos obligatorios: nombre (máx. 100 caracteres), apellido (máx. 100 caracteres), número de colegiatura (único, máx. 30 caracteres), Especialidad (selección de lista existente), teléfono (máx. 20 caracteres), correo electrónico (formato válido) y horario de atención (días y horas de inicio y fin).
2. THE Sistema SHALL permitir crear Especialidades con nombre (obligatorio, máx. 100 caracteres) y descripción (opcional, máx. 500 caracteres); y editar y eliminar Especialidades existentes.
3. IF una Especialidad tiene Médicos asignados, THEN THE Sistema SHALL impedir su eliminación y mostrar el mensaje "No se puede eliminar: existen médicos asignados a esta especialidad".
4. WHEN un Administrador solicita la lista de Médicos, THE Sistema SHALL mostrar los registros paginados con un máximo de 20 registros por página e incluir la Especialidad de cada Médico.
5. WHEN un Administrador aplica un filtro por Especialidad o ingresa un término de búsqueda, THE Sistema SHALL retornar únicamente los Médicos cuyo nombre, apellido o número de colegiatura coincidan con los criterios.
6. IF el número de colegiatura de un Médico ya existe en la base de datos al crear o editar, THEN THE Sistema SHALL rechazar la operación y mostrar el mensaje "Este número de colegiatura ya está registrado".
7. WHEN un Administrador solicita eliminar un Médico, THE Sistema SHALL mostrar un diálogo de confirmación antes de ejecutar la eliminación.
8. IF un Médico tiene Citas asociadas, THEN THE Sistema SHALL impedir la eliminación y mostrar el mensaje indicando el número de Citas dependientes.

---

### Requirement 5: Gestión de Citas Médicas

**User Story:** Como paciente o administrador, quiero agendar, modificar y cancelar citas médicas, para que la atención médica esté organizada y sin conflictos de horario.

#### Acceptance Criteria

1. THE Sistema SHALL permitir crear una Cita con los campos obligatorios: Paciente, Médico, fecha, hora de inicio, duración (entre 15 y 120 minutos en intervalos de 15 minutos), motivo de consulta (máx. 500 caracteres) y estado inicial Pendiente.
2. WHEN un usuario solicita crear una Cita, THE Scheduler SHALL verificar que la fecha y hora solicitadas estén dentro del horario de atención registrado del Médico seleccionado.
3. IF la fecha y hora solicitadas están fuera del horario de atención del Médico, THEN THE Scheduler SHALL rechazar la solicitud y mostrar el mensaje "El médico no tiene disponibilidad en el horario seleccionado".
4. IF el intervalo de tiempo de una nueva Cita se superpone con una Cita existente del mismo Médico con estado Pendiente o Confirmada, THEN THE Scheduler SHALL rechazar la solicitud y mostrar el mensaje "El médico ya tiene una cita programada en ese horario".
5. IF la fecha y hora de inicio de una nueva Cita son anteriores a la fecha y hora actuales del servidor, THEN THE Validator SHALL rechazar la solicitud y mostrar el mensaje "No se pueden agendar citas en fechas u horas pasadas".
6. WHEN un Administrador o Médico confirma una Cita con estado Pendiente, THE Sistema SHALL actualizar el estado a Confirmada.
7. WHEN un usuario autorizado (Paciente propietario, Médico asignado o Administrador) cancela una Cita, THE Sistema SHALL actualizar el estado a Cancelada y registrar la fecha y hora exactas de la cancelación.
8. WHEN un usuario autorizado reprograma una Cita, THE Scheduler SHALL aplicar las mismas validaciones de disponibilidad, superposición y fechas pasadas que para una nueva Cita.
9. WHEN el estado de una Cita cambia a Confirmada o Cancelada, THE Notifier SHALL enviar un correo electrónico de notificación al Paciente y al Médico asociados dentro de los 5 minutos siguientes al cambio de estado.
10. WHEN un usuario solicita la lista de Citas, THE Sistema SHALL mostrar los registros paginados con 20 registros por página y filtros por rango de fechas, Médico, Paciente y estado.

---

### Requirement 6: Gestión de Historias Clínicas

**User Story:** Como médico, quiero registrar y actualizar la historia clínica de mis pacientes, para que exista un registro médico completo y accesible.

#### Acceptance Criteria

1. THE Sistema SHALL asociar cada entrada de Historia_Clínica a exactamente un Paciente y permitir hasta 1000 entradas por Paciente.
2. WHEN se marca una Cita como Completada, THE Sistema SHALL habilitar al Médico la opción de crear una nueva entrada de Historia_Clínica para el Paciente asociado a esa Cita.
3. WHILE un usuario tiene rol Médico, THE Sistema SHALL permitirle crear y editar únicamente las entradas de Historia_Clínica que él mismo registró.
4. WHILE un usuario tiene rol Administrador, THE Sistema SHALL permitirle crear y editar cualquier entrada de Historia_Clínica.
5. WHILE un usuario tiene rol Paciente, THE Sistema SHALL mostrarle sus entradas de Historia_Clínica en modo solo lectura sin opción de edición.
6. THE Sistema SHALL registrar en cada entrada de Historia_Clínica los campos obligatorios: fecha (auto-asignada al momento de creación), diagnóstico (máx. 500 caracteres), tratamiento prescrito (máx. 1000 caracteres) y el Médico responsable; y el campo opcional: observaciones (máx. 2000 caracteres).
7. IF un campo obligatorio de una entrada de Historia_Clínica está vacío al guardar, THEN THE Sistema SHALL retornar el formulario con mensajes de error específicos por campo sin persistir datos.
8. IF un usuario con rol Paciente intenta acceder a la vista de edición de una Historia_Clínica, THEN THE Sistema SHALL denegar el acceso y mostrar el mensaje "No tiene permisos para realizar esta acción".

---

### Requirement 7: Dashboard Administrativo

**User Story:** Como administrador, quiero ver un panel de control con estadísticas del sistema, para que pueda tomar decisiones basadas en datos actualizados.

#### Acceptance Criteria

1. WHILE un usuario tiene rol Administrador, THE Dashboard SHALL mostrar las siguientes métricas del mes calendario actual: total de Pacientes registrados en el sistema, total de Médicos activos, total de Citas del mes calendario actual y total de Citas con estado Pendiente.
2. WHILE un usuario tiene rol Administrador, THE Chart_Engine SHALL proveer datos para un gráfico de barras que muestre la distribución de Citas por Especialidad en el mes calendario actual.
3. WHILE un usuario tiene rol Administrador, THE Chart_Engine SHALL proveer datos para un gráfico de líneas que muestre la cantidad de Pacientes nuevos registrados por mes en los 12 meses calendario anteriores al mes actual (cada punto representa un mes completo).
4. WHEN el Dashboard se carga, THE Sistema SHALL obtener los datos de las métricas y gráficos desde el servidor en la misma solicitud HTTP de página y responder en ≤5 segundos.
5. IF la obtención de datos del Dashboard falla o supera el tiempo límite, THEN THE Sistema SHALL mostrar un mensaje de error "No se pudieron cargar los datos del panel" y ofrecer un botón de reintento manual.
6. THE Dashboard SHALL renderizar los gráficos utilizando la biblioteca Chart.js en el navegador del cliente.
7. WHILE un usuario tiene rol Médico, THE Dashboard SHALL mostrar únicamente las Citas del día calendario actual y las Citas con estado Pendiente asignadas a ese Médico.

---

### Requirement 8: Generación de Reportes

**User Story:** Como administrador, quiero exportar reportes de citas y pacientes en PDF y Excel, para que pueda compartir y analizar la información fuera del sistema.

#### Acceptance Criteria

1. THE Report_Generator SHALL permitir exportar un reporte de Citas en formato PDF con filtros opcionales por rango de fechas (fecha inicio y fecha fin), Médico y estado de Cita.
2. THE Report_Generator SHALL permitir exportar un reporte de Citas en formato Excel (.xlsx) con los mismos filtros disponibles para el reporte PDF de Citas.
3. THE Report_Generator SHALL permitir exportar un reporte de Pacientes en formato PDF con filtros opcionales por rango de fechas de registro y Especialidad del Médico asignado.
4. THE Report_Generator SHALL permitir exportar un reporte de Pacientes en formato Excel (.xlsx) con los mismos filtros disponibles para el reporte PDF de Pacientes.
5. IF los filtros aplicados no producen ningún registro, THEN THE Report_Generator SHALL generar el archivo con el encabezado correspondiente y el mensaje "No se encontraron registros con los filtros aplicados", sin retornar un error.
6. IF los valores de filtro proporcionados son inválidos (e.g., fecha fin anterior a fecha inicio), THEN THE Sistema SHALL rechazar la solicitud y mostrar un mensaje de error descriptivo sin generar el archivo.
7. WHEN un Administrador solicita un reporte válido, THE Report_Generator SHALL generar el archivo en menos de 30 segundos para conjuntos de datos de hasta 10,000 registros.
8. THE Report_Generator SHALL incluir en cada reporte: encabezado con nombre del Sistema, fecha y hora de generación, filtros aplicados y número total de registros incluidos.
9. WHEN el archivo de reporte es generado, THE Sistema SHALL enviarlo al navegador del cliente como descarga directa con el tipo MIME `application/pdf` para PDF y `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` para Excel.

---

### Requirement 9: Interfaz de Usuario

**User Story:** Como usuario del sistema, quiero una interfaz moderna y responsiva, para que pueda usar el sistema cómodamente desde cualquier dispositivo.

#### Acceptance Criteria

1. THE Sistema SHALL renderizar todas las vistas utilizando Bootstrap 5 con un layout que incluya sidebar de navegación y navbar superior.
2. IF el ancho de pantalla del dispositivo es de al menos 320px, THEN THE Sistema SHALL adaptar el layout sin pérdida de funcionalidad ni contenido oculto involuntariamente.
3. WHEN el usuario completa una operación de creación, edición o eliminación, THE Sistema SHALL mostrar un mensaje de confirmación o error visible durante al menos 3 segundos y no más de 10 segundos.
4. WHILE una operación del servidor está en curso y ha superado los 500ms, THE Sistema SHALL mostrar un indicador de carga visible hasta que la operación concluya.
5. WHEN un usuario ingresa al menos 2 caracteres en el campo de búsqueda de las listas de Pacientes, Médicos o Citas, THE Sistema SHALL mostrar los resultados filtrados en ≤300ms sin recargar la página completa.
6. THE Sistema SHALL mostrar tablas responsivas con paginación de 25 filas por defecto en todas las vistas de listado.

---

### Requirement 10: Validaciones y Seguridad

**User Story:** Como administrador del sistema, quiero que todas las entradas sean validadas y el sistema sea seguro, para que los datos sean íntegros y el sistema esté protegido contra ataques comunes.

#### Acceptance Criteria

1. THE Validator SHALL validar todos los campos de formulario en el servidor antes de persistir datos en la base de datos, independientemente de las validaciones del lado cliente.
2. THE Sistema SHALL utilizar Django ModelForms para la validación de todos los formularios del Sistema.
3. THE Sistema SHALL aplicar protección contra inyección SQL mediante el uso exclusivo del Django ORM para todas las consultas a la base de datos, sin concatenación de cadenas en consultas.
4. THE Sistema SHALL aplicar protección CSRF en todos los formularios que realicen operaciones de escritura; IF una solicitud POST llega sin token CSRF válido, THEN THE Sistema SHALL retornar HTTP 403 y no procesar la operación.
5. IF un campo obligatorio de un formulario está vacío al enviarse, THEN THE Validator SHALL retornar el formulario con mensajes de error específicos por campo sin persistir datos.
6. THE Sistema SHALL usar el sistema de templates de Django con auto-escape activado para sanitizar todos los datos de entrada antes de renderizarlos en plantillas HTML, previniendo ataques XSS; cualquier desactivación del auto-escape deberá estar explícitamente justificada en el código.
7. THE Sistema SHALL almacenar las variables de entorno sensibles (SECRET_KEY, credenciales de base de datos, claves de API de correo) en un archivo `.env` excluido del repositorio Git mediante `.gitignore`, y nunca en el código fuente.

---

### Requirement 11: Pruebas Unitarias

**User Story:** Como desarrollador, quiero que el sistema tenga pruebas unitarias básicas, para que los cambios futuros no rompan funcionalidades existentes.

#### Acceptance Criteria

1. THE Sistema SHALL incluir pruebas unitarias que verifiquen la creación válida e inválida de instancias de los modelos: User, Patient, Doctor, Appointment y MedicalRecord, incluyendo validaciones de campos obligatorios y restricciones de unicidad.
2. THE Sistema SHALL incluir pruebas unitarias para el Scheduler que verifiquen: (a) rechazo de Citas con fecha u hora pasada, (b) rechazo de Citas que se superponen con una Cita existente del mismo Médico con estado Pendiente o Confirmada, y (c) aceptación de Citas en horarios válidos y disponibles.
3. THE Sistema SHALL incluir pruebas unitarias para el sistema de permisos por rol que verifiquen: (a) que un Administrador puede acceder a todas las vistas protegidas, (b) que un Médico recibe HTTP 403 al intentar acceder a vistas de administración, y (c) que un Paciente recibe HTTP 403 al intentar editar una Historia_Clínica.
4. WHEN se ejecuta la suite de pruebas con el comando `python manage.py test`, THE Sistema SHALL completar todas las pruebas sin errores en menos de 60 segundos en un entorno de desarrollo local con base de datos SQLite en memoria.
5. THE Sistema SHALL mantener una cobertura de código medida con `coverage.py` de al menos el 70% en los módulos: `appointments`, `patients` y `doctors`.

---

### Requirement 12: Despliegue y Configuración de Producción

**User Story:** Como administrador del sistema, quiero que la aplicación esté desplegada en producción con configuración adecuada, para que los usuarios puedan acceder al sistema desde internet.

#### Acceptance Criteria

1. THE Sistema SHALL seleccionar el motor de base de datos según el valor de la variable de entorno `DATABASE_URL`: si está definida, usará PostgreSQL con los parámetros de la URL; si no está definida, usará SQLite local.
2. THE Sistema SHALL incluir un archivo `requirements.txt` con versiones exactas (usando `==`) de todas las dependencias del proyecto, generado con `pip freeze`.
3. THE Sistema SHALL incluir un archivo `Procfile` con la instrucción `web: gunicorn <nombre_proyecto>.wsgi` para el despliegue en Render o Railway.
4. WHEN el Sistema se despliega en producción, THE Sistema SHALL servir archivos estáticos mediante WhiteNoise configurado en el middleware de Django.
5. WHEN el Sistema se ejecuta en producción (`DEBUG=False`), THE Sistema SHALL no exponer trazas de error ni información de depuración en las respuestas HTTP al cliente.
6. THE Sistema SHALL definir `ALLOWED_HOSTS` con los dominios autorizados; IF una solicitud HTTP llega con un encabezado `Host` no incluido en `ALLOWED_HOSTS`, THEN THE Sistema SHALL retornar HTTP 400 sin procesar la solicitud.
7. THE Sistema SHALL incluir un archivo `README.md` con instrucciones de: instalación local, configuración de variables de entorno, ejecución de migraciones, creación de superusuario y despliegue en producción.

---

### Requirement 13: Control de Versiones y Flujo Git

**User Story:** Como equipo de desarrollo, quiero seguir un flujo Git estructurado, para que el trabajo colaborativo sea ordenado y trazable.

#### Acceptance Criteria

1. THE Sistema SHALL utilizar un repositorio Git con las ramas: `main`, `dev`, `dev1`, `dev2`, `dev3` y `dev4`.
2. THE Sistema SHALL utilizar el formato de commits convencionales con los prefijos obligatorios: `feat:`, `fix:`, `refactor:`, `docs:`, `style:` y `test:`, seguidos de un scope entre paréntesis y una descripción en minúsculas (e.g., `feat(auth): implement login system`).
3. WHEN un desarrollador abre un Pull Request desde una rama `devN` hacia `dev`, THE Sistema SHALL requerir al menos una revisión aprobada antes de permitir el merge.
4. THE Sistema SHALL incluir un archivo `.gitignore` que excluya: entornos virtuales (`venv/`, `.venv/`), archivos `.env`, archivos de caché de Python (`__pycache__/`, `*.pyc`, `*.pyo`), archivos de base de datos SQLite (`*.sqlite3`, `db.sqlite3`) y archivos de cobertura (`.coverage`, `htmlcov/`).
5. IF un desarrollador intenta hacer merge directo desde una rama `devN` hacia `main` sin pasar por `dev`, THEN THE Sistema SHALL rechazar la operación mediante reglas de protección de rama configuradas en el repositorio remoto.
6. IF un mensaje de commit no sigue el formato convencional definido en el criterio 2, THEN THE Sistema SHALL rechazar el commit mediante un hook de Git pre-commit configurado en el repositorio.
