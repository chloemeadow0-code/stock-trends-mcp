import json
import urllib.request
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stock-trends")


def _fetch_trends(symbol: str) -> dict:
    """调东财原生trends2接口，不依赖AKShare"""
    url = (
        f"https://push2delay.eastmoney.com/api/qt/stock/trends2/get"
        f"?secid=0.{symbol}"
        f"&fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13"
        f"&fields2=f51,f52,f53,f54,f55,f56,f57,f58"
        f"&iscr=0&iscca=0"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _parse_trends(data: dict) -> list:
    """解析东财trends返回格式"""
    trends = data.get("data", {}).get("trends", [])
    result = []
    for t in trends:
        cols = t.split(",")
        result.append({
            "time": cols[0],
            "open": float(cols[1]),
            "close": float(cols[2]),
            "high": float(cols[3]),
            "low": float(cols[4]),
            "volume": int(cols[5]),
            "amount": float(cols[6]),
        })
    return result


@mcp.tool()
def get_trends(symbol: str = "159995") -> str:
    """获取A股/ETF当天分钟分时走势

    Args:
        symbol: 股票/ETF代码，如 159995
    Returns:
        当天每分钟的分时数据（时间、开盘、收盘、最高、最低、成交量、成交额）
    """
    try:
        raw = _fetch_trends(symbol)
        trends = _parse_trends(raw)
        return json.dumps({"data": trends, "total": len(trends)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def find_price_times(symbol: str = "159995", price_list: str = "[]") -> str:
    """按成交价在当天分时中反推时间点

    Args:
        symbol: 股票/ETF代码，如 159995
        price_list: JSON数组，如 "[2.948, 2.974, 3.001]"
    Returns:
        每个价格对应的分钟级成交时间
    """
    try:
        prices = json.loads(price_list)
        raw = _fetch_trends(symbol)
        trends = _parse_trends(raw)

        results = []
        for target in prices:
            times = [t["time"] for t in trends if abs(t["close"] - target) < 0.001]
            results.append({"price": target, "times": times})

        info = raw.get("data", {})
        return json.dumps({
            "symbol": symbol,
            "name": info.get("name", ""),
            "pre_close": info.get("preClose"),
            "data": results,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})