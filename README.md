# PricePulse - 智能價格監控系統

## 項目概述

一個**完全免費**的價格監控系統，支持 Amazon、eBay、Walmart 等平台。

### 核心特性

- ✅ **零成本運行** - 使用免費 API 和開源工具
- ✅ **多平台支持** - Amazon + eBay + Walmart + 自定義平台
- ✅ **智能爬蟲** - 自動識別平台和價格
- ✅ **實時通知** - Telegram + Email
- ✅ **價格歷史** - 追蹤價格趨勢

## 快速開始

### 1. 克隆項目（需要權限）

```bash
# SSH 方式（推薦）
git clone git@github.com:wd5557/price-pulse.git
cd price-pulse

# 或 HTTPS 方式
git clone https://github.com/wd5557/price-pulse.git
cd price-pulse
```

### 2. 配置環境變量

```bash
cp .env.example .env
# 編輯 .env 文件（API Keys 可選，系統支持無 API Key 爬蟲模式）
```

### 3. 啟動服務

```bash
docker compose up -d
```

### 4. 訪問服務

- API 文檔: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- Redis: localhost:6379

---

**注意**: 這是私人倉庫，克隆需要認證：
- **SSH**: 配置好 SSH key（已有權限的 GitHub 帳號）
- **HTTPS**: 使用 GitHub token 或已登入的 gh CLI

## 技術棧

- **後端**: FastAPI + Python 3.11+
- **數據庫**: PostgreSQL + Redis
- **爬蟲**: Playwright
- **任務隊列**: Celery
- **前端**: React + TypeScript
- **部署**: Docker Compose

## 免費 API 組合

| 平台 | API | 服務 | 月費 |
|------|-----|------|------|
| Amazon | Keepa API (免費套餐) | 100 請求/月 | $0 |
| eBay | Official API | 無限制 | $0 |
| Walmart | Official API | 無限制 | $0 |

## 開發狀態

- [x] 項目規劃
- [ ] 項目初始化
- [ ] API 開發
- [ ] 爬蟲開發
- [ ] 前端開發
- [ ] 測試

## 許可證

MIT License
