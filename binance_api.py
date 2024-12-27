import requests
import json
import time
import hmac
import hashlib
from urllib.parse import urlencode

class BinanceAPI:
    def __init__(self, api_key=None, api_secret=None, proxy=None):
        self.base_url_spot = "https://api.binance.com"
        self.base_url = "https://fapi.binance.com"
        self.api_key = api_key
        self.api_secret = api_secret
        self.proxies = {
            'http': proxy,
            'https': proxy
        } if proxy else None

    def _generate_signature(self, params: dict) -> str:
        """生成签名"""
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def get_futures_prices(self, symbols=None):
        """获取合约价格"""
        try:
            endpoint = "/fapi/v1/ticker/price"
            response = requests.get(
                f"{self.base_url}{endpoint}",
                proxies=self.proxies,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if symbols:
                    return [item for item in data if item['symbol'] in symbols]
                return data
            return None
        except Exception as e:
            print(f"获取价格时发生错误: {str(e)}")
            return None

    def get_futures_24h_tickers(self):
        """获取24小时价格变化信息"""
        try:
            endpoint = "/fapi/v1/ticker/24hr"
            response = requests.get(
                f"{self.base_url}{endpoint}",
                proxies=self.proxies,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                # 按照涨跌幅排序
                sorted_data = sorted(data, key=lambda x: float(x['priceChangePercent']), reverse=True)
                return sorted_data
            return None
        except Exception as e:
            print(f"获取24小时数据时发生错误: {str(e)}")
            return None

    def get_spot_balance(self):
        """获取现货账户余额"""
        try:
            endpoint = "/api/v3/account"
            timestamp = int(time.time() * 1000)
            params = {
                'timestamp': timestamp
            }
            # 添加签名
            signature = self._generate_signature(params)
            params['signature'] = signature
            
            response = requests.get(
                f"{self.base_url_spot}{endpoint}",
                params=params,
                headers={'X-MBX-APIKEY': self.api_key},
                proxies=self.proxies,
                timeout=10
            )
            # print(response)
            if response.status_code == 200:
                data = response.json()
                # print(data)
                # 只返回有余额的资产
                return [asset for asset in data['balances'] if float(asset['free']) > 0 or float(asset['locked']) > 0]
            return None
        except Exception as e:
            print(f"获取现货余额时发生错误: {str(e)}")
            return None

    def get_futures_balance(self):
        """获取合约账户余额"""
        try:
            endpoint = "/fapi/v2/balance"
            timestamp = int(time.time() * 1000)
            params = {
                'timestamp': timestamp
            }
            signature = self._generate_signature(params)
            params['signature'] = signature
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers={'X-MBX-APIKEY': self.api_key},
                proxies=self.proxies,
                timeout=10
            )
            # print(response.json())
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"获取合约余额时发生错误: {str(e)}")
            return None

    def get_futures_positions(self):
        """获取合约持仓信息"""
        try:
            endpoint = "/fapi/v2/positionRisk"
            timestamp = int(time.time() * 1000)
            params = {
                'timestamp': timestamp
            }
            signature = self._generate_signature(params)
            params['signature'] = signature
            
            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers={'X-MBX-APIKEY': self.api_key},
                proxies=self.proxies,
                timeout=10
            )
            if response.status_code == 200:
                # 只返回有持仓的数据
                return [pos for pos in response.json() if float(pos['positionAmt']) != 0]
            return None
        except Exception as e:
            print(f"获取持仓信息时发生错误: {str(e)}")
            return None

a = BinanceAPI(
        api_key='UkHQCpU57DzH4FwYC2XK7rF2DEcgxXpPafbXZKiZJhq8eqUutHsLLZ27ButSjPsw',
        api_secret='eb1QsLNX5akAymWx9LtJ5oclLaIB5vv7go0Eu27GmeEtdlfruXRLQZqHJZlDxFcx',
        proxy="http://127.0.0.1:7890"  # 代理设置
    )
# a.get_spot_balance()
# a.get_futures_balance()