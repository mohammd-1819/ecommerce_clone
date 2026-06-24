# Ecommerce Clone

A Django template-based ecommerce website for selling coffee beans, tea, hot chocolate, and similar products. The project is inspired by [Danidorco](https://danidorco.com/) and focuses on a classic storefront experience with product browsing, OTP login, user addresses, cart management, checkout, Redis caching, Celery background jobs, and Docker support.

> This is a clone-style educational/portfolio project and is not affiliated with Danidorco.

## Features

- Django template-based storefront
- Product listing and product detail pages
- Product categories, variants, weights, images, attributes, and reviews
- Phone-number OTP login
- Custom user model using `phone_number` as the login field
- User profile area
- User address management
- Cart management flow
- Checkout flow with address selection, coupon support, tax/shipping calculation, and order creation
- Order history and order detail pages
- Redis-backed caching for product categories
  - Product list page sidebar/filter categories
  - Header/search modal categories
- Celery scheduled tasks for cart cleanup
  - Mark old active carts as abandoned
  - Delete abandoned carts older than 30 days
- PostgreSQL database
- Dockerized setup with:
  - Django + Gunicorn web service
  - PostgreSQL
  - Redis
  - Celery worker
  - Celery beat

## Tech Stack

- Python 3.12
- Django 6
- PostgreSQL
- Redis
- Celery
- Docker / Docker Compose
- HTML, CSS, JavaScript

## Project Structure

```text
.
├── accounts/            # Custom user, OTP login, profiles, addresses
├── cart/                # Cart models, views, and cleanup tasks
├── core/                # Shared base models/utilities
├── landing/             # Landing/home pages
├── new_danidor/         # Django project settings, URLs, Celery config
├── order/               # Checkout, coupons, payment methods, orders
├── product/             # Products, categories, variants, reviews, caching
├── statics/             # Static source files
├── templates/           # Django templates
├── media/               # Uploaded media files
├── Dockerfile
├── docker-compose.yml
├── entrypoint.sh        # Docker startup script
├── manage.py
└── requirements.txt
```

## Environment Variables

The project reads database, Redis, and Celery configuration from environment variables.

For local development, Django loads variables from `.env`.

For Docker, `docker-compose.yml` loads variables from `.env.docker`.

### Required variables

```env
POSTGRES_DB=ecommerce_clone
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=ecommerce_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_CACHE_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=
```

### Using `.env.example`

If the repository contains `.env.example`, copy it before running the project.

For local development:

```bash
cp .env.example .env
```

For Docker:

```bash
cp .env.example .env.docker
```

Then update the values according to the setup you are using.

## Docker Entrypoint

The project includes a root-level `entrypoint.sh` file. This script is used by Docker when a container starts.

It does four things:

1. Waits until PostgreSQL is available.
2. Runs database migrations automatically unless `DOCKER_RUN_MIGRATIONS=0`.
3. Collects static files automatically unless `DOCKER_COLLECTSTATIC=0`.
4. Starts the actual container command, such as Gunicorn, Celery worker, or Celery beat.

For the `web` service, this means migrations and static collection can run automatically when the container starts.

For `celery_worker` and `celery_beat`, `docker-compose.yml` sets:

```env
DOCKER_RUN_MIGRATIONS=0
DOCKER_COLLECTSTATIC=0
```

This prevents Celery containers from running migrations or collecting static files.

### Important Dockerfile path

Because `entrypoint.sh` is in the project root, the Dockerfile should copy it like this:

```dockerfile
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

If your Dockerfile currently contains this line:

```dockerfile
COPY docker/entrypoint.sh /entrypoint.sh
```

replace it with:

```dockerfile
COPY entrypoint.sh /entrypoint.sh
```

Otherwise Docker will look for `docker/entrypoint.sh` and the build can fail.

## Running the Project with Docker

### Prerequisites

- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/mohammd-1819/ecommerce_clone.git
cd ecommerce_clone
```

### 2. Create the Docker environment file

```bash
cp .env.example .env.docker
```

If `.env.example` is not available yet, create `.env.docker` manually:

```bash
touch .env.docker
```

Then add:

```env
POSTGRES_DB=ecommerce_clone
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=ecommerce_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_CACHE_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=
```

### 3. Make sure the entrypoint file is executable

On macOS/Linux:

```bash
chmod +x entrypoint.sh
```

On Windows, this is usually handled by Docker during the image build because the Dockerfile runs `chmod +x /entrypoint.sh`.

### 4. Build and start the containers

```bash
docker compose up --build -d
```

This starts:

- `web` - Django app served by Gunicorn
- `db` - PostgreSQL
- `redis` - Redis server
- `celery_worker` - Celery worker process
- `celery_beat` - Celery scheduler process

### 5. Run migrations

If the Dockerfile is using `entrypoint.sh`, migrations run automatically when the `web` container starts.

You can also run migrations manually:

```bash
docker compose exec web python manage.py migrate
```

### 6. Collect static files

If the Dockerfile is using `entrypoint.sh`, static files are collected automatically when the `web` container starts.

You can also run it manually:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

### 7. Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

This project uses `phone_number` as the user login field, so Django will ask for a phone number.

Example:

```text
+989123456789
```

### 8. Open the project

Website:

```text
http://localhost:8000/
```

Django admin:

```text
http://localhost:8000/admin/
```

### Useful Docker commands

View all logs:

```bash
docker compose logs -f
```

View web logs:

```bash
docker compose logs -f web
```

View Celery worker logs:

```bash
docker compose logs -f celery_worker
```

Stop containers:

```bash
docker compose down
```

Stop containers and remove volumes:

```bash
docker compose down -v
```

Run tests inside Docker:

```bash
docker compose exec web pytest
```

## Running the Project Without Docker

### Prerequisites

Install these on your machine:

- Python 3.12
- PostgreSQL
- Redis

### 1. Clone the repository

```bash
git clone https://github.com/mohammd-1819/ecommerce_clone.git
cd ecommerce_clone
```

### 2. Create and activate a virtual environment

macOS/Linux:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create the local environment file

```bash
cp .env.example .env
```

If `.env.example` is not available yet, create `.env` manually:

```bash
touch .env
```

Then add:

```env
POSTGRES_DB=ecommerce_clone
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=ecommerce_password
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

REDIS_CACHE_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=
```

### 5. Create the PostgreSQL database

Log in to PostgreSQL:

```bash
psql -U postgres
```

Create the database and user:

```sql
CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_password';
CREATE DATABASE ecommerce_clone OWNER ecommerce_user;
GRANT ALL PRIVILEGES ON DATABASE ecommerce_clone TO ecommerce_user;
\q
```

If your local PostgreSQL user/password is different, update `.env` to match it.

### 6. Start Redis

macOS with Homebrew:

```bash
brew services start redis
```

Linux with systemd:

```bash
sudo systemctl start redis
```

Windows users can run Redis through WSL or another Redis-compatible local server.

Check Redis:

```bash
redis-cli ping
```

Expected response:

```text
PONG
```

### 7. Run migrations

```bash
python manage.py migrate
```

### 8. Collect static files

```bash
python manage.py collectstatic --noinput
```

### 9. Create a superuser

```bash
python manage.py createsuperuser
```

Enter a phone number when prompted.

Example:

```text
+989123456789
```

### 10. Run the development server

```bash
python manage.py runserver
```

Website:

```text
http://127.0.0.1:8000/
```

Django admin:

```text
http://127.0.0.1:8000/admin/
```

## Running Celery Locally

Celery is used for scheduled cart cleanup tasks. Redis must be running before starting Celery.

Start the Celery worker:

```bash
celery -A new_danidor worker --loglevel=info
```

Start Celery beat in another terminal:

```bash
celery -A new_danidor beat --loglevel=info
```

The scheduled tasks are configured to:

- Mark active carts older than 7 days as abandoned.
- Delete abandoned carts older than 30 days.

## Redis Cache

The project uses Django's Redis cache backend.

Cached category data includes:

- Active product categories for the product list page
- Active product categories for the header/search modal

The category cache timeout is 24 hours.

If you update product categories in the admin and do not see changes immediately, clear the category cache from the Django shell:

```bash
python manage.py shell
```

```python
from product.cache import clear_all_product_category_caches

clear_all_product_category_caches()
```

Inside Docker:

```bash
docker compose exec web python manage.py shell
```

then run the same Python code.

## Main URLs

```text
/                  Landing page
/admin/            Django admin
/profile/          User profile, OTP login, addresses, orders
/cart/             Cart detail and cart actions
/order/            Checkout and order flow
/product/          Product list and product detail pages
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov
```

Inside Docker:

```bash
docker compose exec web pytest
```

## Common Issues

### Docker build fails because of `entrypoint.sh`

If you see an error about `docker/entrypoint.sh` not existing, update the Dockerfile.

Change:

```dockerfile
COPY docker/entrypoint.sh /entrypoint.sh
```

to:

```dockerfile
COPY entrypoint.sh /entrypoint.sh
```

Then rebuild:

```bash
docker compose build --no-cache
docker compose up -d
```

### Database connection error in Docker

Make sure `.env.docker` contains:

```env
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Then restart:

```bash
docker compose down
docker compose up --build -d
```

### Database connection error locally

Make sure PostgreSQL is running and that `.env` contains:

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
```

### Redis connection error

For local development, make sure Redis is running and `.env` contains:

```env
REDIS_CACHE_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
```

For Docker, use:

```env
REDIS_CACHE_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
```

### `psycopg2` installation error

Install PostgreSQL development headers.

Ubuntu/Debian:

```bash
sudo apt install libpq-dev python3-dev build-essential
```

macOS:

```bash
brew install postgresql
```

## Development Notes

- The Django project module is `new_danidor`.
- The project uses `accounts.User` as the custom user model.
- Authentication is phone-number OTP based.
- In development, the generated OTP code is included in the login page context for easier testing.
- The project language is configured as Persian/Farsi.
- The project timezone is configured as `Asia/Tehran`.
- Media files are served by Django only when `DEBUG=True`.

## License

No license file is currently included. Add a license if you plan to publish or distribute the project.
