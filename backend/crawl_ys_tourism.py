# -*- coding: utf-8 -*-
"""颍上旅游网站爬虫"""
import requests
from bs4 import BeautifulSoup
import os
import time

print("="*60)
print("🌍 颍上旅游网站爬虫")
print("="*60)

# 颍上旅游相关网站
YS_TOURISM_URLS = {
    "颍上县文化旅游体育局": "http://www.ys.gov.cn/zwgk/public/column/116820432?type=4&action=list",
    "颍上旅游官方": "http://www.yslyj.com/",
    "阜阳旅游": "https://lyj.fy.gov.cn/"
}

# 景区关键词
SCENIC_SPOTS = [
    "八里河", "管仲老街", "尤家花园", "迪沟生态园", "湿地公园", "江心洲", "明清苑", "管鲍祠", "小张庄"
]

def fetch_page(url):
    """获取网页内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        print(f"❌ 访问 {url} 失败: {str(e)}")
        return None

def extract_content(html, spot_name):
    """提取与景区相关的内容"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 提取所有文本内容
    text = soup.get_text(separator='\n', strip=True)
    
    # 筛选包含景区名称的段落
    relevant_content = []
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if spot_name in line:
            # 提取前后5行作为上下文
            start = max(0, i-5)
            end = min(len(lines), i+6)
            context = '\n'.join(lines[start:end])
            relevant_content.append(context)
    
    return relevant_content

def save_crawled_data(data, filename):
    """保存爬取的数据"""
    os.makedirs("crawled_data", exist_ok=True)
    filepath = os.path.join("crawled_data", filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# 颍上旅游爬虫数据\n\n")
        f.write(f"爬取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(data)
    
    print(f"✅ 数据已保存至: {filepath}")

def main():
    """主函数"""
    all_data = []
    
    for site_name, url in YS_TOURISM_URLS.items():
        print(f"\n🔍 爬取 {site_name}: {url}")
        html = fetch_page(url)
        
        if html:
            for spot in SCENIC_SPOTS:
                content = extract_content(html, spot)
                if content:
                    all_data.append(f"\n{'='*40}")
                    all_data.append(f"【{site_name}】{spot}")
                    all_data.append('='*40)
                    all_data.extend(content)
                    all_data.append('\n')
        
        # 避免请求过快
        time.sleep(2)
    
    # 保存结果
    if all_data:
        data_str = '\n'.join(all_data)
        save_crawled_data(data_str, "颍上旅游爬虫数据.txt")
        print(f"\n✨ 爬取完成！共获取 {len(all_data)} 条相关信息")
    else:
        print("\n⚠️  未获取到任何数据")

if __name__ == "__main__":
    main()
