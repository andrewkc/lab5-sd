# Laboratorio 5 — Sistemas de marketing y predicciones

Repositorio con las soluciones desarrolladas para el Laboratorio 5 de Análisis y Diseño de Software.

## Aplicaciones

### App1 — Champions Predictor

Aplicación web en arquitectura de tres capas para gestionar partidos de la Champions League. Permite:

- Sincronizar partidos desde una fuente simulada.
- Guardar partidos en PostgreSQL.
- Registrar predicciones con ganador y marcador.
- Consultar partidos y predicciones.
- Ejecutarse con Docker Compose.
- Desplegarse en AWS EC2.

Documentación completa:

[README de App1](./app1/README.md)

### App2 — Marketing Studio

Aplicación web para marketing empresarial. Permite:

- Recibir una foto de un producto o empresa.
- Proponer tres guiones.
- Seleccionar una propuesta.
- Generar tres imágenes y un video MP4.
- Seleccionar Instagram o TikTok.
- Registrar una publicación simulada.
- Persistir campañas y archivos multimedia.
- Ejecutarse con Docker Compose y PostgreSQL.
- Desplegarse en AWS EC2.

Documentación completa:

[README de App2](./app2/README.md)

## Estructura del repositorio

```text
lab5-sd/
├── app1/       # Champions Predictor
├── app2/       # Marketing Studio
├── docs/       # Guía del laboratorio
├── .gitignore  # Secretos y archivos generados excluidos de Git
└── README.md   # Índice general del proyecto
```

## Seguridad

No subir al repositorio:

- .env
- claves privadas .pem
- bases de datos locales
- archivos generados en app2/instance o app2/storage

Las instrucciones de ejecución, Docker, publicación y despliegue están documentadas en los README individuales de cada aplicación.
