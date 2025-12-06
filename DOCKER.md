# NeoRadio Docker Deployment Guide

This guide explains how to run NeoRadio using Docker for both development and production environments.

## Quick Start

### Development

```bash
docker-compose up dev
```

Access the application at: `http://localhost:5000/radio`

### Production

```bash
docker-compose up prod
```

Access the application at: `http://localhost:8080/radio`

## Docker Images

### Production Image (`Dockerfile`)

- Based on `python:3.11-slim`
- Runs with **gunicorn** (4 workers)
- Non-root user (`neoradio:1000`)
- Health checks enabled
- Optimized for production use
- Port: 5000 (mapped to 8080 on host)

### Development Image (`Dockerfile.dev`)

- Based on `python:3.11-slim`
- Runs with **Flask development server**
- Hot reload enabled (code changes reflect immediately)
- Debug mode enabled
- Port: 5000

## Environment Variables

Create a `.env` file in the project root:

```bash
# Required for production
SECRET_KEY=your-super-secret-key-here-change-this

# Optional overrides
DATABASE=/app/data/database.db
```

Use the provided [.env.example](.env.example) as a template:

```bash
cp .env.example .env
# Edit .env with your values
```

## Docker Compose Commands

### Start Services

```bash
# Development
docker-compose up dev

# Production
docker-compose up prod

# Detached mode (background)
docker-compose up -d prod
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs
docker-compose logs -f dev

# Last 100 lines
docker-compose logs --tail=100 prod
```

### Rebuild Images

```bash
# Rebuild dev image
docker-compose build dev

# Rebuild prod image
docker-compose build prod

# Force rebuild (no cache)
docker-compose build --no-cache prod
```

## Manual Docker Commands

### Build Images

```bash
# Development
docker build -f Dockerfile.dev -t neoradio:dev .

# Production
docker build -f Dockerfile -t neoradio:prod .
```

### Run Containers

#### Development

```bash
docker run -it --rm \
  -p 5000:5000 \
  -v $(pwd)/app.py:/app/app.py \
  -v $(pwd)/templates:/app/templates \
  -v $(pwd)/static:/app/static \
  -v neoradio-dev-data:/app/data \
  neoradio:dev
```

#### Production

```bash
docker run -d --rm \
  -p 8080:5000 \
  -e SECRET_KEY=your-secret-key \
  -v neoradio-prod-data:/app/data \
  --name neoradio-prod \
  neoradio:prod
```

## Volume Management

### List Volumes

```bash
docker volume ls | grep neoradio
```

### Inspect Volume

```bash
docker volume inspect neoradio-prod-data
```

### Backup Database

```bash
# Create backup
docker run --rm \
  -v neoradio-prod-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/neoradio-backup.tar.gz -C /data .

# Restore backup
docker run --rm \
  -v neoradio-prod-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/neoradio-backup.tar.gz -C /data
```

### Remove Volumes

```bash
# Warning: This deletes all data!
docker-compose down -v

# Or manually
docker volume rm neoradio-prod-data
docker volume rm neoradio-dev-data
```

## Health Checks

The production container includes health checks:

```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' neoradio-prod

# View health check logs
docker inspect --format='{{json .State.Health}}' neoradio-prod | jq
```

## Troubleshooting

### Container Won't Start

Check logs:
```bash
docker-compose logs dev
```

Verify image built correctly:
```bash
docker images | grep neoradio
```

### Port Already in Use

Change ports in `docker-compose.yml`:
```yaml
ports:
  - "5001:5000"  # Use 5001 instead of 5000
```

### Permission Issues

The production container runs as user `neoradio:1000`. Ensure volume permissions allow this:
```bash
# Check volume permissions
docker run --rm -v neoradio-prod-data:/data alpine ls -la /data
```

### Database Not Persisting

Verify volumes are mounted:
```bash
docker inspect neoradio-prod | grep -A 10 Mounts
```

### Hot Reload Not Working (Dev)

Ensure source code is mounted correctly:
```bash
docker-compose exec dev ls -la /app
```

## Production Deployment

### Using Docker Compose

1. **Set environment variables:**
   ```bash
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
   echo "SECRET_KEY=$SECRET_KEY" > .env
   ```

2. **Start production service:**
   ```bash
   docker-compose up -d prod
   ```

3. **Verify it's running:**
   ```bash
   docker-compose ps
   docker-compose logs -f prod
   ```

4. **Access the application:**
   ```
   http://your-server-ip:8080/radio
   ```

### Behind a Reverse Proxy (Nginx/Caddy)

#### Nginx Example

```nginx
server {
    listen 80;
    server_name radio.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Caddy Example

```
radio.example.com {
    reverse_proxy localhost:8080
}
```

## Security Considerations

1. **Change the secret key** - Never use the default secret key in production
2. **Use HTTPS** - Deploy behind a reverse proxy with SSL/TLS
3. **Firewall rules** - Restrict access to port 8080 (only reverse proxy should access it)
4. **Regular updates** - Keep base image and dependencies updated
5. **Volume permissions** - Ensure data volumes have appropriate permissions

## Advanced Configuration

### Custom Gunicorn Settings

Edit `Dockerfile` CMD to adjust workers, timeout, etc.:

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "8", "--timeout", "240", "app:app"]
```

### Resource Limits

Add to `docker-compose.yml`:

```yaml
services:
  prod:
    # ... existing config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
        reservations:
          memory: 512M
```

### Logging Configuration

```yaml
services:
  prod:
    # ... existing config ...
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Development Workflow

1. **Make code changes** - Edit files locally
2. **Changes auto-reload** - Flask dev server detects changes
3. **Test locally** - http://localhost:5000/radio
4. **Run tests** - `docker-compose exec dev pytest`
5. **Build production** - `docker-compose build prod`
6. **Deploy** - `docker-compose up -d prod`

## Support

For issues or questions, please open an issue at the project repository.
