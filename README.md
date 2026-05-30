# Secure Notes — Demo DevSecOps

Aplicación web de baja complejidad (CRUD de notas) que integra **base de datos**, un **flujo CI/CD con controles de seguridad (DevSecOps)** y despliegue en **nube con monitoreo**.

## Arquitectura

```
Usuario ──HTTPS──> Render (Web Service) ──> Flask (Gunicorn) ──> PostgreSQL (Render)
                          │
                          └── /health  ← monitoreo / uptime checks
```

- **Backend:** Python 3.12 + Flask
- **ORM / BD:** SQLAlchemy + PostgreSQL (SQLite en local)
- **Servidor:** Gunicorn
- **CI/CD:** GitHub Actions
- **Nube:** Render (capa gratuita)

## Controles de seguridad implementados

| Capa | Control | Herramienta |
|------|---------|-------------|
| Datos | Consultas parametrizadas (anti SQL injection) | SQLAlchemy ORM |
| Datos | Secretos fuera del código (variables de entorno) | `os.environ` + `.gitignore` |
| App | Cabeceras HTTP de seguridad (CSP, X-Frame-Options) | Flask-Talisman |
| App | Límite de peticiones (anti abuso / fuerza bruta) | Flask-Limiter |
| App | Validación de entrada | Lógica en `app.py` |
| CI/CD | SAST (análisis estático) | Bandit, Semgrep |
| CI/CD | Dependencias vulnerables (SCA) | pip-audit, Dependabot |
| CI/CD | Escaneo de secretos | Gitleaks |
| CI/CD | Escaneo de contenedor | Trivy |
| Nube | HTTPS/TLS automático | Render |
| Nube | Monitoreo de salud | `/health` + UptimeRobot |

## Ejecutar en local

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # edita SECRET_KEY
python app.py
# Abre http://localhost:5000
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/` | Interfaz web |
| GET | `/health` | Estado del servicio y BD |
| GET | `/api/notes` | Lista notas |
| POST | `/api/notes` | Crea nota `{title, content}` |
| DELETE | `/api/notes/<id>` | Elimina nota |

## CI/CD

El pipeline (`.github/workflows/ci-cd.yml`) ejecuta en cada push: lint, pruebas, SAST, escaneo de dependencias, escaneo de secretos y escaneo de contenedor. Si todo pasa en `main`, despliega a Render.

## Licencia

MIT.
