# Деплой в Yandex Cloud

## Что понадобится

- Доменное имя (например, `your-domain.ru`)
- Аккаунт Yandex Cloud
- SSH-ключ для подключения к VM

---

## Шаг 1: Создать виртуальную машину

1. Зайди в **Yandex Cloud Console** → **Compute Cloud** → **Создать ВМ**
2. **Операционная система:** Ubuntu 22.04 LTS
3. **Ресурсы:** 2 vCPU, 4 GB RAM, 30 GB SSD
4. **Публичный IP адрес:** выбери **Статический** (важно!)
5. **Доступ:** укажи свой SSH-публичный ключ
6. **Security Group:** добавь правила для входящего трафика:
   - SSH (TCP 22) — твой IP
   - HTTP (TCP 80) — `0.0.0.0/0`
   - HTTPS (TCP 443) — `0.0.0.0/0`

---

## Шаг 2: Настроить DNS

У регистратора домена создай **A-запись**:

```
your-domain.ru → <публичный IP VM>
```

Подожди 5–30 минут (распространение DNS).

---

## Шаг 3: Установить Docker на сервере

Подключись по SSH:

```bash
ssh yc-user@<публичный-IP>

# Установка Docker
sudo apt update && sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
docker --version
```

---

## Шаг 4: Загрузить проект на сервер

На **локальной машине** (из папки проекта):

```bash
rsync -avz \
  --exclude='.venv' \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.db' \
  ./ yc-user@<IP>:/home/yc-user/fastapi-app/
```

---

## Шаг 5: Настроить окружение

На **сервере**:

```bash
cd ~/fastapi-app
cp .env.production .env
nano .env
```

Заполни обязательные поля:

```bash
SECRET_KEY=            # openssl rand -hex 32
DB_PASSWORD=           # сложный пароль для MSSQL
DATABASE_URL=          # поменяй пароль в URL
CORS_ORIGINS=["https://your-domain.ru"]
```

Создай папки для certbot:

```bash
mkdir -p certbot/conf certbot/www
```

---

## Шаг 6: Получить SSL-сертификат

```bash
docker run -it --rm -p 80:80 \
  -v $(pwd)/certbot/conf:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d your-domain.ru \
  --agree-tos \
  -m admin@your-domain.ru \
  -n
```

---

## Шаг 7: Запустить приложение

```bash
docker compose up -d --build
```

Подожди 2 минуты и проверь:

```bash
docker compose ps
curl https://your-domain.ru/health
```

---

## Обновление приложения

```bash
cd ~/fastapi-app
git pull          # или rsync с локальной машины
docker compose down
docker compose up -d --build
```