"""
Walmart 價格爬蟲 - 使用官方 API
"""
import httpx
import os
from typing import Optional, Dict, Any
from urllib.parse import urlparse

class WalmartScraper:
    """Walmart 價格爬蟲"""
    
    def __init__(self):
        self.api_key = os.getenv("WALMART_API_KEY")  # 可選
        self.api_url = "https://developer.api.walmart.com"
    
    async def fetch_price(self, url: str) -> Optional[Dict[str, Any]]:
        """
        通過 Walmart API 或爬蟲獲取價格
        
        Args:
            url: Walmart 商品 URL
            
        Returns:
            價格數據字典
        """
        # 提取 product ID (US 商品 ID)
        product_id = self._extract_product_id(url)
        
        if product_id and self.api_key:
            # 嘗試使用 API
            return await self._api_fetch(product_id)
        
        # 回退到爬蟲
        return await self._fallback_scrape(url)
    
    def _extract_product_id(self, url: str) -> Optional[str]:
        """從 Walmart URL 提取 Product ID"""
        import re
        # Walmart URL 格式: https://www.walmart.com/ip/PRODUCT_ID
        id_match = re.search(r'/ip/([^/?]+)', url)
        return id_match.group(1) if id_match else None
    
    async def _api_fetch(self, product_id: str) -> Optional[Dict[str, Any]]:
        """使用 Walmart API 獲取數據"""
        try:
            async with httpx.AsyncClient() as client:
                # Walmart Product API
                headers = {
                    'WM_SEC.KEY_VERSION': 'v2',
                    'WM_SEC.KEY_ID': self.api_key,
                    'WM_SEC.AUTHTYPE': 'HMAC.SHA256',
                    'WM_CONSUMER.KEY_ID': self.api_key,
                }
                
                response = await client.get(
                    f"{self.api_url}/product/v2/v2/items/{product_id}",
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('data'):
                    product = data['data']
                    offer_price = product.get('product', {}).get('offerPrice')
                    
                    if offer_price:
                        return {
                            'price': float(offer_price),
                            'currency': 'USD',
                            'title': product.get('product', {}).get('name', ''),
                            'is_available': product.get('product', {}).get('stock') == 'AVAILABLE',
                        }
                
                return None
                
        except Exception as e:
            print(f"Walmart API error: {e}")
            return None
    
    async def _fallback_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Walmart 通用爬蟲"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, timeout=15000)
                await page.wait_for_timeout(2000)
                
                # Walmart 價格選擇器
                selectors = [
                    '[itemprop="price"]',
                    '.prod-PriceXl',
                    '.price-characteristic',
                    '.price-group',
                ]
                
                for selector in selectors:
                    try:
                        elem = await page.query_selector(selector)
                        if elem:
                            price_text = await elem.inner_text()
                            price = self._clean_price(price_text)
                            if price:
                                return {
                                    'price': price,
                                    'currency': 'USD',
                                    'title': await page.title(),
                                    'is_available': True,
                                }
                    except:
                        continue
                
                await browser.close()
                return None
                
        except Exception as e:
            print(f"Walmart scraper failed: {e}")
            return None
    
    def _clean_price(self, text: str) -> Optional[float]:
        """清理價格字符串"""
        import re
        cleaned = re.sub(r'[^\d.,]', '', text)
        cleaned = cleaned.replace(',', '')
        try:
            return float(cleaned) if cleaned else None
        except:
            return None
