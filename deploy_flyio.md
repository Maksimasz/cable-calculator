# 🪰 Развертывание на Fly.io

## Преимущества:
- ✅ **Бесплатный тариф** (3 приложения)
- ✅ **Глобальная CDN**
- ✅ **Docker поддержка**
- ✅ **Высокая производительность**

## Шаги:

### 1. Установите flyctl
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

### 2. Войдите в аккаунт
```bash
fly auth login
```

### 3. Создайте fly.toml
```toml
app = "cable-calculator"
primary_region = "fra"

[build]

[env]
  PORT = "8501"

[http_service]
  internal_port = 8501
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

### 4. Разверните
```bash
fly deploy
```

## Результат:
`https://cable-calculator.fly.dev`
