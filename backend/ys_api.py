# -*- coding: utf-8 -*-
"""颍上文旅信息API服务"""
from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import time
import ssl
import os

app = Flask(__name__)

# 禁用SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

# 颍上文旅相关网站
TOURISM_URLS = {
    "颍上县文化旅游体育局": "http://www.ys.gov.cn/zwgk/public/column/116820432?type=4&action=list",
    "颍上旅游官方": "http://www.yslyj.com/",
}

# 景区关键词
SCENIC_KEYWORDS = [
    "八里河", "管仲老街", "尤家花园", "迪沟", "湿地", "江心洲", "明清苑", "管鲍祠", "小张庄"
]

# 缓存数据
cache = {
    "data": None,
    "timestamp": 0
}

def fetch_page(url):
    """获取网页内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(f"获取页面失败: {url}, 错误: {str(e)}")
        return None

def extract_news(html):
    """提取新闻信息"""
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'html.parser')
    news_list = []
    
    # 尝试提取新闻列表
    articles = soup.find_all('li') or soup.find_all('a') or soup.find_all('article')
    
    for article in articles[:10]:  # 只取前10条
        text = article.get_text(strip=True)
        if any(keyword in text for keyword in SCENIC_KEYWORDS) and len(text) > 20:
            news_list.append(text[:200])  # 限制长度
    
    return news_list

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>颍上文旅信息API</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #667eea; }
            .btn { background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
            pre { background: #f5f5f5; padding: 20px; border-radius: 5px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>🌾 颍上文旅信息API</h1>
        <p>颍上小智后端服务正在运行...</p>
        <h2>API接口：</h2>
        <ul>
            <li><a href="/api/news">/api/news</a> - 获取最新文旅资讯</li>
            <li><a href="/api/refresh">/api/refresh</a> - 刷新缓存数据</li>
        </ul>
    </body>
    </html>
    '''

@app.route('/api/news')
def get_news():
    """获取文旅资讯API"""
    global cache
    
    # 检查缓存（1小时内有效）
    if cache["data"] and (time.time() - cache["timestamp"]) < 3600:
        return jsonify({
            "success": True,
            "source": "cache",
            "data": cache["data"]
        })
    
    # 尝试获取新数据
    all_news = []
    
    for site_name, url in TOURISM_URLS.items():
        html = fetch_page(url)
        if html:
            news = extract_news(html)
            all_news.extend(news)
    
    # 更新缓存
    if all_news:
        cache["data"] = all_news
        cache["timestamp"] = time.time()
        
        return jsonify({
            "success": True,
            "source": "web",
            "count": len(all_news),
            "data": all_news
        })
    else:
        # 返回本地备用数据
        return jsonify({
            "success": False,
            "message": "无法获取最新数据，请检查网络连接",
            "fallback": "可使用本地数据"
        })

@app.route('/api/refresh')
def refresh_cache():
    """强制刷新缓存"""
    global cache
    cache["data"] = None
    cache["timestamp"] = 0
    return jsonify({"message": "缓存已清除，请访问 /api/news 获取新数据"})

if __name__ == '__main__':
    print("=" * 50)
    print("🌾 颍上文旅信息API服务")
    print("=" * 50)
    print("服务地址: http://localhost:5000")
    print("API接口: http://localhost:5000/api/news")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
