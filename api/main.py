"""PricePulse API."""
from decimal import Decimal
from typing import List

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine, get_db
from models import PriceHistory, Product, User
from schemas import PriceCheckResponse, ProductCreate, ProductResponse
from scrapers.amazon_scraper import AmazonScraper
from scrapers.ebay_scraper import EbayScraper
from scrapers.platform_detector import PlatformDetector
from scrapers.walmart_scraper import WalmartScraper
from scrapers.generic_scraper import GenericScraper
from celery_tasks import check_product_price

app = FastAPI(
    title="PricePulse API",
    description="智能價格監控系統 - 免費組合版",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

platform_detector = PlatformDetector()
scrapers = {
    "amazon": AmazonScraper(),
    "ebay": EbayScraper(),
    "walmart": WalmartScraper(),
    "generic": GenericScraper(),
}

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == 1).first()
        if not user:
            db.add(
                User(
                    id=1,
                    email="demo@pricepulse.local",
                    password_hash="not-used",
                    name="Demo User",
                    is_active=True,
                )
            )
            db.commit()
    finally:
        db.close()


@app.get("/")
async def root() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/api/status")
async def api_status() -> dict:
    return {
        "app": "PricePulse API",
        "version": "1.0.0",
        "status": "running",
        "supported_platforms": ["amazon", "ebay", "walmart"],
    }


@app.get("/api/config")
async def api_config() -> dict:
    return {
        "features": {
            "platform_detector": True,
            "manual_check": True,
            "scheduler": True,
            "history": True,
        },
        "supported_platforms": ["amazon", "ebay", "walmart", "generic"],
        "defaults": {
            "currency": "USD",
            "check_interval": 3600,
        },
        "api_routes": [
            "GET /api/status",
            "GET /api/config",
            "GET /api/products",
            "POST /api/products",
            "POST /api/products/{product_id}/check",
            "GET /api/products/{product_id}/history",
            "DELETE /api/products/{product_id}",
        ],
    }


@app.get("/health")
async def health_check() -> dict:
    return {"status": "healthy"}


@app.post("/api/products", response_model=ProductResponse)
async def create_product(product: ProductCreate, db: Session = Depends(get_db)) -> ProductResponse:
    platform = product.platform.value if product.platform else platform_detector.detect(product.url)

    current_price = None
    currency = "USD"

    scraper = scrapers.get(platform)
    if scraper:
        try:
            price_data = await scraper.fetch_price(product.url)
            if price_data and "price" in price_data:
                current_price = Decimal(str(price_data["price"]))
                currency = price_data.get("currency", "USD")
        except Exception:
            pass

    db_product = Product(
        user_id=1,
        platform=platform,
        product_url=product.url,
        product_name=product.product_name or product.url,
        target_price=Decimal(str(product.target_price)),
        current_price=current_price,
        currency=currency,
        is_active=True,
        check_interval=product.check_interval or 3600,
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    check_product_price.delay(db_product.id)

    return ProductResponse(
        id=db_product.id,
        platform=db_product.platform,
        product_url=db_product.product_url,
        product_name=db_product.product_name or "",
        target_price=float(db_product.target_price) if db_product.target_price is not None else None,
        current_price=float(db_product.current_price) if db_product.current_price is not None else None,
        currency=db_product.currency,
        is_active=db_product.is_active,
        created_at=db_product.created_at.isoformat(),
        updated_at=db_product.updated_at.isoformat() if db_product.updated_at else db_product.created_at.isoformat(),
    )


@app.get("/api/products", response_model=List[ProductResponse])
async def list_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> List[ProductResponse]:
    products = db.query(Product).offset(skip).limit(limit).all()
    return [
        ProductResponse(
            id=p.id,
            platform=p.platform,
            product_url=p.product_url,
            product_name=p.product_name or "",
            target_price=float(p.target_price) if p.target_price is not None else None,
            current_price=float(p.current_price) if p.current_price is not None else None,
            currency=p.currency,
            is_active=p.is_active,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat() if p.updated_at else p.created_at.isoformat(),
        )
        for p in products
    ]


@app.post("/api/products/{product_id}/check", response_model=PriceCheckResponse)
async def check_price(product_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)) -> PriceCheckResponse:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    background_tasks.add_task(check_product_price.delay, product_id)
    return PriceCheckResponse(product_id=product_id, status="scheduled", message="價格檢查已排程")


@app.get("/api/products/{product_id}/history")
async def get_price_history(product_id: int, limit: int = 100, db: Session = Depends(get_db)) -> list[dict]:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    history = (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": h.id,
            "price": float(h.price),
            "timestamp": h.timestamp.isoformat(),
            "is_available": h.is_available,
        }
        for h in history
    ]


@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int, db: Session = Depends(get_db)) -> dict:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
