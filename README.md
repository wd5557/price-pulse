# PricePulse - 智能價格監控系統

## 項目概述

一個可自架的價格監控系統，支持 Amazon、eBay、Walmart 等平台。

### 核心特性

- ✅ 前端儀表板（新增監控、查看配置、手動檢查、查看歷史、刪除任務）
- ✅ 多平台支持（Amazon / eBay / Walmart / Generic）
- ✅ API + 爬蟲雙模式（有 Key 走官方 API，沒 Key 走爬蟲 fallback）
- ✅ 後端任務隊列（Celery + Redis）
- ✅ Docker Compose 一鍵啟動

---

## 首次安裝（新機器）

### 1) 安裝前置條件

- Docker Engine
- Docker Compose v2
- Git

### 2) 下載項目

```bash
git clone https://github.com/wd5557/price-pulse.git
cd price-pulse
```

### 3) 配置環境變量

```bash
cp .env.example .env
```

編輯 `.env`：

- `DATABASE_URL`、`REDIS_URL` 可用預設
- `KEEPA_API_KEY` / `EBAY_APP_ID` / `EBAY_CERT_ID` / `EBAY_DEV_ID` / `WALMART_API_KEY` 可先留空
- 留空時會自動走爬蟲 fallback（功能可用）

### 4) 啟動服務

```bash
docker compose up -d --build
```

### 5) 驗證是否成功

- 前端 UI: `http://localhost:8000/`
- API 文檔: `http://localhost:8000/docs`
- API 狀態: `http://localhost:8000/api/status`

### 6) 停止服務

```bash
docker compose down
```

---

## 已安裝後如何更新

### 方式 A：拉最新代碼並重建（推薦）

```bash
cd /root/.openclaw/workspace/price-pulse
git pull
docker compose up -d --build
```

### 方式 B：只重啟容器（無代碼變更時）

```bash
cd /root/.openclaw/workspace/price-pulse
docker compose restart
```

### 如遇異常，可用乾淨重建

```bash
cd /root/.openclaw/workspace/price-pulse
docker compose down -v
docker compose up -d --build
```

---

## API 對接入口（去哪裡申請）

### Amazon（Keepa）

- 網站: `https://keepa.com/#!api`
- 用途: Amazon 價格 API
- 環境變量: `KEEPA_API_KEY`

### eBay Developer

- 網站: `https://developer.ebay.com/`
- 用途: eBay API 憑證
- 環境變量: `EBAY_APP_ID`、`EBAY_CERT_ID`、`EBAY_DEV_ID`

### Walmart Developer

- 網站: `https://developer.walmart.com/`
- 用途: Walmart API Key
- 環境變量: `WALMART_API_KEY`

> 不對接 API 也能用：系統會自動回退到爬蟲模式。

---

## 常用運維命令

查看容器狀態：

```bash
docker compose ps
```

查看 API 日誌：

```bash
docker compose logs -f api
```

查看 Worker 日誌：

```bash
docker compose logs -f celery_worker
```

---

## 服務端點

- 前端 UI: `GET /`
- API 狀態: `GET /api/status`
- 配置資訊: `GET /api/config`
- 產品列表: `GET /api/products`
- 新增產品: `POST /api/products`
- 手動檢查: `POST /api/products/{product_id}/check`
- 歷史價格: `GET /api/products/{product_id}/history`
- 刪除產品: `DELETE /api/products/{product_id}`

---

## 技術棧

- 後端: FastAPI + SQLAlchemy
- 任務隊列: Celery + Redis
- 數據庫: PostgreSQL
- 爬蟲: Playwright
- 部署: Docker Compose

## 許可證

MIT License
