"""
通用價格爬蟲 - 支持任意電商網站
"""
from typing import Optional, Dict, Any
import re
from playwright.async_api import async_playwright

class GenericScraper:
    """通用價格爬蟲 - 適用於任何平台"""
    
    # 通用價格選擇器（覆蓋 80% 的網站）
    PRICE_SELECTORS = [
        '[class*="price"]',
        '[id*="price"]',
        '.product-price',
        '.sale-price',
        '.current-price',
        '.price-amount',
        '[itemprop="price"]',
        '.price',
    ]
    
    async def fetch_price(self, url: str) -> Optional[Dict[str, Any]]:
        """
        從任意 URL 提取價格
        
        Args:
            url: 商品 URL
            
        Returns:
            價格數據字典
        """
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, timeout=15000)
                await page.wait_for_timeout(2000)
                
                # 嘗試所有價格選擇器
                for selector in self.PRICE_SELECTORS:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            price_text = await elem.inner_text()
                            price = self.clean_price(price_text)
                            if price and price > 0:
                                return {
                                    'price': price,
                                    'currency': await self._detect_currency(page),
                                    'title': await page.title(),
                                    'is_available': True,
                                }
                    except:
                        continue
                
                await browser.close()
                return None
                
        except Exception as e:
            print(f"Generic scraper failed for {url}: {e}")
            return None
    
    def clean_price(self, text: str) -> Optional[float]:
        """
        清理價格字符串並提取數字
        """
        if not text:
            return None
        
        # 移除貨幣符號和特殊字符
        cleaned = re.sub(r'[^\d.,]', '', text)
        
        # 處理歐洲格式 (1.234,56) vs 美國格式 (1,234.56)
        if ',' in cleaned and '.' in cleaned:
            if cleaned.rfind(',') > cleaned.rfind('.'):
                # 歐洲格式: 1.234,56 -> 1234.56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # 美國格式: 1,234.56 -> 1234.56
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            cleaned = cleaned.replace(',', '.')
        
        try:
            return float(cleaned) if cleaned else None
        except:
            return None
    
    async def _detect_currency(self, page) -> str:
        """檢測貨幣"""
        try:
            content = await page.content()
            if '$' in content or 'USD' in content:
                return 'USD'
            if '€' in content or 'EUR' in content:
                return 'EUR'
            if '£' in content or 'GBP' in content:
                return 'GBP'
            if '¥' in content or 'CNY' in content:
                return 'CNY'
            return 'USD'
        except Exception:
            return 'USD'
