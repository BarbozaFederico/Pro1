# Pro1 - Centro de Kinesiologia

Entrega del TP1 de Programacion I. El repositorio contiene la estructura inicial funcional del backend y del frontend para una aplicacion web destinada a un centro de kinesiologia.

## Estructura

- `backend/`: API Flask, configuracion, base SQLite y coleccion de Postman.
- `frontend/`: estructura inicial del cliente web.
- `documentacion/`: modelo de datos y diseno inicial.

## Puesta en marcha

Desde una terminal Bash:

```bash
cd backend
bash install.sh
cp .env-example .env
bash boot.sh
```

La API quedara disponible en `http://127.0.0.1:5000`.

## Verificacion

- `GET /`: informacion basica de la API.
- `GET /health`: estado de la API y de la base SQLite.

La coleccion `backend/collection/TP1-Kinesiologia.postman_collection.json` permite probar ambos endpoints desde Postman.
