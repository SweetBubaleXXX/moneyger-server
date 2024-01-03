## Configuration

You can create `.env` file in project root directory.

#### Following env variables are required:

- [`SECRET_KEY`](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key)
- [`ALLOWED_HOSTS`](https://docs.djangoproject.com/en/4.2/ref/settings/#secret-key) when not `DEBUG`
- [`DATABASE_URL`](https://django-environ.readthedocs.io/en/latest/types.html#environ-env-db-url)
- [`CELERY_BROKER_URL`](https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-url)
- [`CELERY_RESULT_BACKEND`](https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-backend)
- [`RABBITMQ_URL`](https://pika.readthedocs.io/en/stable/examples/using_urlparameters.html)

#### Optional variables:

- [`CACHE_URL`](https://django-environ.readthedocs.io/en/latest/types.html#environ-env-cache-url)
- [`EMAIL_CONFIG`](https://django-environ.readthedocs.io/en/latest/types.html#environ-env-search-url)
- [`WEBSOCKET_CHANNEL_LAYERS`](https://channels.readthedocs.io/en/latest/topics/channel_layers.html#redis-channel-layer)
- `CORS_ALLOW_ALL_ORIGINS` *boolean*
- `CORS_ALLOWED_ORIGINS` *list*
- `CSRF_TRUSTED_ORIGINS` *list*
- `XFF_TRUSTED_PROXY_DEPTH` *number*
- `JWT_REFRESH_TOKEN_COOKIE`
- `AUTH_COOKIE_SECURE` *boolean*
- `AUTH_COOKIE_HTTP_ONLY` *boolean*
- `AUTH_COOKIE_SAMESITE`
- `CURRENCY_RATES_PROVIDER` must be a subclass of `core.services.rates_providers.BaseRates`
- `ALFA_BANK_NATIONAL_RATES_URL`

## Docker

These variables must be present in your `.env` file:

- `SECRET_KEY`
- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `RABBITMQ_USER`
- `RABBITMQ_PASSWORD`

### Development

To run development containers:

```bash
docker compose -f ./docker-compose.dev.yml up -d --build
```

### Production

To run production containers:

```bash
docker compose up -d
```
