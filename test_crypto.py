# -*- coding: utf-8 -*-
"""
加密货币分析测试脚本
"""

from crypto_analyzer import CryptoAnalyzer
import json

def test_crypto_analyzer():
    """测试加密货币分析器"""
    print("开始测试加密货币分析器...")
    
    # 初始化分析器
    analyzer = CryptoAnalyzer()
    
    # 测试获取热门币种
    print("\n1. 测试获取热门币种...")
    try:
        cryptos = analyzer.get_top_cryptos(5)
        print(f"成功获取 {len(cryptos)} 个热门币种:")
        for crypto in cryptos:
            print(f"  {crypto['symbol']} - {crypto['name']} - ${crypto['current_price']}")
    except Exception as e:
        print(f"获取热门币种失败: {e}")
    
    # 测试分析BTC
    print("\n2. 测试分析BTC...")
    try:
        result = analyzer.analyze_crypto('BTC')
        if 'error' in result:
            print(f"分析失败: {result['error']}")
        else:
            print("分析结果:")
            print(f"  当前价格: ${result['current_price']}")
            print(f"  24h涨跌: {result['price_change_24h']}%")
            print(f"  市值排名: #{result['market_cap_rank']}")
            print(f"  技术评分: {result['technical_score']}")
            print(f"  基本面评分: {result['fundamental_score']}")
            print(f"  综合评分: {result['total_score']}")
            print(f"  投资建议: {result['investment_advice']}")
    except Exception as e:
        print(f"分析BTC失败: {e}")
    
    # 测试分析ETH
    print("\n3. 测试分析ETH...")
    try:
        result = analyzer.analyze_crypto('ETH')
        if 'error' in result:
            print(f"分析失败: {result['error']}")
        else:
            print("分析结果:")
            print(f"  当前价格: ${result['current_price']}")
            print(f"  24h涨跌: {result['price_change_24h']}%")
            print(f"  市值排名: #{result['market_cap_rank']}")
            print(f"  技术评分: {result['technical_score']}")
            print(f"  基本面评分: {result['fundamental_score']}")
            print(f"  综合评分: {result['total_score']}")
            print(f"  投资建议: {result['investment_advice']}")
    except Exception as e:
        print(f"分析ETH失败: {e}")
    
    print("\n测试完成!")

if __name__ == "__main__":
    test_crypto_analyzer() 