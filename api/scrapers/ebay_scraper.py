"""
eBay 價格爬蟲 - 使用官方 Finding API
"""
import httpx
import os
from typing import Optional, Dict, Any

class EbayScraper:
    """eBay 價格爬蟲"""
    
    def __init__(self):
        self.app_id = os.getenv("EBAY_APP_ID")
        self.cert_id = os.getenv("EBAY_CERT_ID")
        self.dev_id = os.getenv("EBAY_DEV_ID")
        self.api_url = "https://open.api.ebay.com/shopping"
    
    async def fetch_price(self, url: str) -> Optional[Dict[str, Any]]:
        """
        通過 eBay Finding API 獲取價格
        
        Args:
            url: eBay 商品 URL
            
        Returns:
            價格數據字典
        """
        # 提取 item ID
        item_id = self._extract_item_id(url)
        if not item_id:
            return await self._fallback_scrape(url)
        
        # 如果沒有 API 憑證，使用備用方案
        if not all([self.app_id, self.cert_id, self.dev_id]):
            return await self._fallback_scrape(url)
        
        try:
            async with httpx.AsyncClient() as client:
                # eBay Finding API 请求
                params = {
                    'OPERATION-NAME': 'getSingleItem',
                    'SERVICE-NAME': 'FindingService',
                    'SERVICE-VERSION': '1.0.0',
                    'SECURITY-APPNAME': self.app_id,
                    'RESPONSE-DATA-FORMAT': 'JSON',
                    'REST-PAYLOAD': '',
                    'keywords': '',
                    'productId': item_id,
                    'affiliateUserId': '',
                    'affiliateCustomId': '',
                    'trackingId': '',
                    'trackingPartnerCode': ''
                }
                
                headers = {
                    'X-EBAY-C-MARKETPLACE-ID': 'EBAY-US'
                }
                
                response = await client.get(
                    f"{self.api_url}",
                    params=params,
                    headers=headers,
                    timeout=10.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get('getSingleItemResponse')[0].get('Item'):
                    item = data['getSingleItemResponse'][0]['Item']
                    return {
                        'price': self._extract_price(item),
                        'currency': item.get('Currency', 'USD'),
                        'title': item.get('Title'),
                        'is_available': True,
                    }
                
                return None
                
        except Exception as e:
            print(f"eBay API error: {e}")
            return await self._fallback_scrape(url)
    
    def _extract_item_id(self, url: str) -> Optional[str]:
        """從 eBay URL 提取 Item ID"""
        import re
        id_match = re.search(r'/item/([^/?]+)(?:\\?|)', url)
        return id_match.group(1) if id_match else None
    
    def _extract_price(self, item: dict) -> Optional[float]:
        """從 eBay API 回應提取價格"""
        try:
            price = item.get('CurrentPrice')
            if price:
                return float(price['Value'])
            
            # 嘗試其他價格字段
            price = item.get('ConvertedCurrentPrice')
            if price:
                return float(price['Value'])
            
            price = item.get('StartPrice')
            if price:
                return float(price['Value'])
            
            return None
        except:
            return None
    
    async def _fallback_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """eBay 通用爬蟲（不推薦）"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                await page.goto(url, timeout=15000)
                await page.wait_for_timeout(2000)
                
                # eBay 價格選擇器
                selectors = [
                    '.x-price-primary',
                    '.x-price-amount',
                    '.display-price',
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
            print(f"eBay scraper failed: {e}")
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
