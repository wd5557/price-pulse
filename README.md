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

```bash
# 複製項目
git clone <repo-url>
cd price-pulse

# 啟動開發環境
docker-compose up -d

# 訪置環境變量
cp .env.example .env
# 編輯 .env 文件

# 運行數據庫遷移
docker-compose exec api alembic upgrade head

# 啟動服務
docker-compose up
```

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
