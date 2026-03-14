"""
Amazon 價格爬蟲 - 使用 Keepa API (免費套餐)
"""
import httpx
import os
from typing import Optional, Dict, Any

class AmazonScraper:
    """Amazon 價格爬蟲"""
    
    def __init__(self):
        api_key = os.getenv("KEEPA_API_KEY", "")
        self.api_key = api_key if api_key and not api_key.startswith("your-") else None
        self.api_url = "https://api.keepa.com/api"
    
    async def fetch_price(self, url: str) -> Optional[Dict[str, Any]]:
        """
        通過 Keepa API 獲取 Amazon 商品價格
        
        Args:
            url: Amazon 商品 URL
            
        Returns:
            價格數據字典
        """
        if not self.api_key:
            # 如果沒有 API key，回退到通用爬蟲
            return await self._fallback_scrape(url)
        
        # 提取 ASIN
        asin = self._extract_asin(url)
        if not asin:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                # Keepa API 請求
                params = {
                    'key': self.api_key,
                    'domain': 'com',
                    'asin': asin,
                    'live': 1,
                }
                
                response = await client.get(
                    f"{self.api_url}/product",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('product'):
                    product = data['product'][0]
                    return {
                        'price': product.get('price'),
                        'currency': 'USD',
                        'title': product.get('title'),
                        'is_available': product.get('stock') == 'available'
                    }
                
                return None
                
        except Exception as e:
            print(f"Keepa API error: {e}")
            return await self._fallback_scrape(url)
    
    def _extract_asin(self, url: str) -> Optional[str]:
        """從 URL 提取 ASIN"""
        import re
        asin_match = re.search(r'/([A-Z0-9]{10})(?:[/?]|$)', url)
        return asin_match.group(1) if asin_match else None
    
    async def _fallback_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """備用方案：使用 Playwright 爬蟲"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, timeout=15000)
                await page.wait_for_timeout(2000)  # 等待頁面加載
                
                # 嘗試多種價格選擇器
                selectors = [
                    '#priceblock_ourprice',
                    '#priceblock_dealprice',
                    '#priceblock_saleprice',
                    '.a-price-whole',
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
            print(f"Playwright fallback failed: {e}")
            return None
    
    def _clean_price(self, text: str) -> Optional[float]:
        """清理價格字符串"""
        import re
        # 移除 $, 千分位，轉為 float
        cleaned = re.sub(r'[^\d.,]', '', text)
        cleaned = cleaned.replace(',', '')
        try:
            return float(cleaned) if cleaned else None
        except:
            return None
