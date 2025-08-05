# -*- coding: utf-8 -*-
"""
加密货币API端点
版本：v1.0.0
功能：提供加密货币分析的API接口
"""

from flask import Blueprint, request, jsonify
from crypto_analyzer import CryptoAnalyzer
import logging
import threading
import time
from datetime import datetime

# 创建蓝图
crypto_api = Blueprint('crypto_api', __name__)

# 初始化分析器
crypto_analyzer = CryptoAnalyzer()

# 任务存储
crypto_tasks = {}

def generate_crypto_task_id():
    """生成任务ID"""
    return f"crypto_{int(time.time() * 1000)}"

def update_crypto_task_status(task_id, status, progress=None, result=None, error=None):
    """更新任务状态"""
    if task_id in crypto_tasks:
        crypto_tasks[task_id].update({
            'status': status,
            'progress': progress,
            'result': result,
            'error': error,
            'updated_at': datetime.now().isoformat()
        })

@crypto_api.route('/api/crypto/analyze', methods=['POST'])
def analyze_crypto():
    """分析加密货币"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'error': '请提供加密货币符号'}), 400
        
        # 创建任务
        task_id = generate_crypto_task_id()
        crypto_tasks[task_id] = {
            'task_id': task_id,
            'symbol': symbol,
            'status': 'running',
            'progress': 0,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        def run_analysis():
            try:
                update_crypto_task_status(task_id, 'running', 25)
                
                # 执行分析
                result = crypto_analyzer.analyze_crypto(symbol)
                
                update_crypto_task_status(task_id, 'running', 75)
                
                if 'error' in result:
                    update_crypto_task_status(task_id, 'failed', 100, error=result['error'])
                else:
                    update_crypto_task_status(task_id, 'completed', 100, result=result)
                    
            except Exception as e:
                update_crypto_task_status(task_id, 'failed', 100, error=str(e))
        
        # 在后台线程中运行分析
        thread = threading.Thread(target=run_analysis)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'task_id': task_id,
            'status': 'started',
            'message': f'开始分析 {symbol}'
        })
        
    except Exception as e:
        return jsonify({'error': f'启动分析失败: {str(e)}'}), 500

@crypto_api.route('/api/crypto/status/<task_id>', methods=['GET'])
def get_crypto_analysis_status(task_id):
    """获取分析状态"""
    try:
        if task_id not in crypto_tasks:
            return jsonify({'error': '任务不存在'}), 404
        
        task = crypto_tasks[task_id]
        return jsonify(task)
        
    except Exception as e:
        return jsonify({'error': f'获取状态失败: {str(e)}'}), 500

@crypto_api.route('/api/crypto/top', methods=['GET'])
def get_top_cryptos():
    """获取市值排名前N的加密货币"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        cryptos = crypto_analyzer.get_top_cryptos(limit)
        
        return jsonify({
            'cryptos': cryptos,
            'count': len(cryptos)
        })
        
    except Exception as e:
        return jsonify({'error': f'获取加密货币列表失败: {str(e)}'}), 500

@crypto_api.route('/api/crypto/search', methods=['GET'])
def search_cryptos():
    """搜索加密货币"""
    try:
        query = request.args.get('q', '').lower()
        
        if not query:
            return jsonify({'error': '请提供搜索关键词'}), 400
        
        # 获取前100个加密货币进行搜索
        all_cryptos = crypto_analyzer.get_top_cryptos(100)
        
        # 过滤匹配的加密货币
        matched_cryptos = []
        for crypto in all_cryptos:
            if (query in crypto['symbol'].lower() or 
                query in crypto['name'].lower() or
                query in crypto['id'].lower()):
                matched_cryptos.append(crypto)
        
        return jsonify({
            'cryptos': matched_cryptos,
            'count': len(matched_cryptos)
        })
        
    except Exception as e:
        return jsonify({'error': f'搜索失败: {str(e)}'}), 500

@crypto_api.route('/api/crypto/market_data', methods=['GET'])
def get_crypto_market_data():
    """获取加密货币市场数据"""
    try:
        symbol = request.args.get('symbol', '').upper()
        
        if not symbol:
            return jsonify({'error': '请提供加密货币符号'}), 400
        
        # 获取基本面数据
        fundamental_data = crypto_analyzer.get_fundamental_data(symbol)
        
        if not fundamental_data:
            return jsonify({'error': '无法获取市场数据'}), 404
        
        return jsonify({
            'symbol': symbol,
            'market_data': fundamental_data
        })
        
    except Exception as e:
        return jsonify({'error': f'获取市场数据失败: {str(e)}'}), 500

@crypto_api.route('/api/crypto/price_data', methods=['GET'])
def get_crypto_price_data():
    """获取加密货币价格数据"""
    try:
        symbol = request.args.get('symbol', '').upper()
        interval = request.args.get('interval', '1d')
        limit = request.args.get('limit', 100, type=int)
        
        if not symbol:
            return jsonify({'error': '请提供加密货币符号'}), 400
        
        # 获取价格数据
        df = crypto_analyzer.get_crypto_data(symbol, interval, limit)
        
        if df.empty:
            return jsonify({'error': '无法获取价格数据'}), 404
        
        return jsonify({
            'symbol': symbol,
            'interval': interval,
            'data': df.tail(limit).to_dict('records')
        })
        
    except Exception as e:
        return jsonify({'error': f'获取价格数据失败: {str(e)}'}), 500

@crypto_api.route('/api/crypto/compare', methods=['POST'])
def compare_cryptos():
    """比较多个加密货币"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols or len(symbols) < 2:
            return jsonify({'error': '请提供至少两个加密货币符号'}), 400
        
        if len(symbols) > 5:
            return jsonify({'error': '最多比较5个加密货币'}), 400
        
        results = []
        for symbol in symbols:
            result = crypto_analyzer.analyze_crypto(symbol)
            if 'error' not in result:
                results.append(result)
        
        return jsonify({
            'comparison': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': f'比较失败: {str(e)}'}), 500

@crypto_api.route('/api/crypto/trending', methods=['GET'])
def get_trending_cryptos():
    """获取热门加密货币"""
    try:
        # 获取前50个加密货币
        all_cryptos = crypto_analyzer.get_top_cryptos(50)
        
        # 按24小时涨跌幅排序，获取前10个
        trending = sorted(
            all_cryptos, 
            key=lambda x: x.get('price_change_24h', 0), 
            reverse=True
        )[:10]
        
        return jsonify({
            'trending': trending,
            'count': len(trending)
        })
        
    except Exception as e:
        return jsonify({'error': f'获取热门加密货币失败: {str(e)}'}), 500 