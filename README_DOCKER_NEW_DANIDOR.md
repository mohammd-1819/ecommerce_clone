# Docker setup for your `new_danidor` Django project

This setup is tailored to the project structure you provided:

```text
accounts/
cart/
core/
landing/
new_danidor/
order/
product/
statics/
templates/
media/
```

Your Django settings module is:

```text
new_danidor.settings
```

Your WSGI app is:

```text
new_danidor.wsgi:application
```

Your Celery app should be:

```text
new_danidor
```

## Files to copy into your project root

Copy these into the same folder where `manage.py` exists:

```text
Dockerfile
docker-compose.yml
.dockerignore
.env.docker.example
requirements.docker.txt
docker/entrypoint.sh
new_danidor/celery.py
```

Then copy the content of:

```text
new_danidor/__init__.py.snippet
```

into your real:

```text
new_danidor/__init__.py
```

## Important settings change

Read:

```text
settings_docker_patch.md
```

and apply those changes to:

```text
new_danidor/settings.py
```

The critical changes are:

```python
POSTGRES_HOST=db
REDIS_CACHE_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
```

Inside Docker, service names become hostnames. So Django must connect to `db` and `redis`, not `localhost`.

## Prepare env file

```bash
cp .env.docker.example .env.docker
```

For local Docker testing, these values are fine:

```env
POSTGRES_DB=new_danidor
POSTGRES_USER=new_danidor
POSTGRES_PASSWORD=change-this-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_CACHE_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
```

For real deployment, change:

```env
DJANGO_SECRET_KEY
POSTGRES_PASSWORD
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## Run

On a machine that has Docker Engine:

```bash
docker compose up --build
```

The app will be available at:

```text
http://localhost:8000
```

## Services included

```text
web             Django + Gunicorn
celery_worker   Celery background worker
celery_beat     Celery scheduler for CELERY_BEAT_SCHEDULE
redis           Redis for cache and Celery broker
db              PostgreSQL
```

## Useful commands

Create superuser:

```bash
docker compose run --rm web python manage.py createsuperuser
```

Run migrations manually:

```bash
docker compose run --rm web python manage.py migrate
```

Collect static manually:

```bash
docker compose run --rm web python manage.py collectstatic --noinput
```

View logs:

```bash
docker compose logs -f web
docker compose logs -f celery_worker
docker compose logs -f celery_beat
```

Stop:

```bash
docker compose down
```

Delete containers and database/cache volumes:

```bash
docker compose down -v
```

## Windows note

If Docker Engine cannot be installed on your Windows machine, you cannot run these containers locally on that machine.

You can still:

- commit these files to Git
- test on a Linux VPS
- ask someone with Docker to run it
- run it in CI
- deploy it to a server with Docker
