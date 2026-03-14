"""Celery tasks for periodic price checks."""
import asyncio
import logging
import os
import time
from datetime import datetime

from celery import Celery
from celery.schedules import crontab

from database import SessionLocal
from models import PriceHistory, Product
from scrapers.amazon_scraper import AmazonScraper
from scrapers.ebay_scraper import EbayScraper
from scrapers.walmart_scraper import WalmartScraper

redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
result_backend = redis_url.rsplit("/", 1)[0] + "/1"

celery_app = Celery(
    "pricepulse",
    broker=redis_url,
    backend=result_backend,
)
celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scrapers = {
    "amazon": AmazonScraper(),
    "ebay": EbayScraper(),
    "walmart": WalmartScraper(),
}


@celery_app.task
def check_product_price(product_id: int) -> None:
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            logger.warning("Product %s not found", product_id)
            return

        scraper = scrapers.get(product.platform)
        if not scraper:
            logger.warning("No scraper found for platform: %s", product.platform)
            return

        try:
            price_data = asyncio.run(scraper.fetch_price(product.product_url))
            if not price_data or "price" not in price_data:
                logger.warning("Failed to fetch price for product %s", product_id)
                return

            new_price = float(price_data["price"])
            old_price = float(product.current_price) if product.current_price is not None else None

            product.current_price = new_price
            product.last_checked_at = datetime.utcnow()
            if product.lowest_price is None or new_price < float(product.lowest_price):
                product.lowest_price = new_price
            if product.highest_price is None or new_price > float(product.highest_price):
                product.highest_price = new_price
            db.commit()

            db.add(
                PriceHistory(
                    product_id=product_id,
                    price=new_price,
                    currency=price_data.get("currency", "USD"),
                    is_available=price_data.get("is_available", True),
                    timestamp=datetime.utcnow(),
                )
            )
            db.commit()

            logger.info("Checked %s product %s: %s -> %s", product.platform, product_id, old_price, new_price)

            if _should_alert(product):
                logger.info("Alert triggered for product %s", product_id)

        except Exception as error:
            logger.error("Error checking price for product %s: %s", product_id, error)
    finally:
        db.close()


@celery_app.task
def check_all_products() -> None:
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.is_active.is_(True)).all()
        logger.info("Checking %s products...", len(products))

        for product in products:
            check_product_price.delay(product.id)
            time.sleep(2)

        logger.info("All products checked")
    except Exception as error:
        logger.error("Error in check_all_products: %s", error)
    finally:
        db.close()


def _should_alert(product: Product) -> bool:
    if product.target_price is None or product.current_price is None:
        return False
    return float(product.current_price) <= float(product.target_price)


celery_app.conf.beat_schedule = {
    "check-all-products": {
        "task": "celery_tasks.check_all_products",
        "schedule": crontab(minute="*/10"),
    },
}
