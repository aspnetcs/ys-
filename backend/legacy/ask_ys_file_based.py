# -*- coding: utf-8 -*-
"""颍上智能问答（基于文件搜索）"""
import os
import re

print("🌾 正在唤醒颍小智...")

# 加载所有景区文件
def load_scenic_files():
    """加载所有景区文件"""
    files = []
    for filename in os.listdir("processed_chunks"):
        if filename.endswith(".txt") and "processed_chunk" in filename:
            filepath = os.path.join("processed_chunks", filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                # 提取景区名称
                match = re.search(r"【📍\s*景区】\s*([^\n]+)", content)
                if match:
                    scenic = match.group(1).strip()
                else:
                    # 从文件名中提取
                    scenic = filename.replace("processed_chunk.", "").replace(".txt", "")
                files.append({
                    "scenic": scenic,
                    "content": content,
                    "filename": filename
                })
            except Exception as e:
                print(f"⚠️  读取 {filename} 失败: {str(e)}")
    return files

# 智能搜索
def search_content(question, files):
    """搜索相关内容"""
    # 同义词映射
    synonyms = {
        '老街': '管仲老街',
        '八里河': '八里河景区',
        '迪沟': '迪沟生态园',
        '尤家花园': '尤家花园',
        '湿地公园': '湿地公园',
        '江心洲': '江心洲公园',
        '明清苑': '明清苑',
        '管鲍祠': '管鲍祠',
        '小张庄': '小张庄公园',
        '五里湖': '湿地公园',
        '管仲': '管仲老街',
        '生态园': '迪沟生态园',
        '花园': '尤家花园',
        '公园': '江心洲公园'
    }
    
    # 景区名称映射
    scenic_names = {
        '管仲老街': '管仲老街',
        '八里河景区': '八里河景区',
        '迪沟生态园': '迪沟生态园',
        '尤家花园': '尤家花园',
        '湿地公园': '湿地公园',
        '江心洲公园': '江心洲公园',
        '明清苑': '明清苑',
        '管鲍祠': '管鲍祠',
        '小张庄公园': '小张庄公园'
    }
    
    # 处理查询
    processed_question = question
    target_scenic = None
    
    # 检查是否包含景区名称
    for key, value in scenic_names.items():
        if key in question:
            target_scenic = value
            break
    
    # 检查是否包含同义词
    if not target_scenic:
        for key, value in synonyms.items():
            if key in question:
                target_scenic = value
                break
    
    # 搜索相关文件
    results = []
    
    # 如果找到了目标景区，只返回该景区的内容
    if target_scenic:
        for file in files:
            if target_scenic in file['scenic']:
                file['relevance'] = 100  # 最高相关性
                results.append(file)
    else:
        # 分析查询意图
        query_terms = processed_question.split()
        intent_keywords = ['时间', '门票', '地址', '特色', '历史', '美食', '交通', '开放', '价格', '位置']
        
        # 搜索相关文件并计算相关性
        for file in files:
            relevance_score = 0
            
            # 检查内容是否包含查询词
            for term in query_terms:
                if term in file['content']:
                    relevance_score += 5
            
            # 检查是否包含意图关键词
            for keyword in intent_keywords:
                if keyword in processed_question and keyword in file['content']:
                    relevance_score += 10
            
            # 只有当相关性分数大于10时才添加
            if relevance_score > 10:
                file['relevance'] = relevance_score
                results.append(file)
    
    # 按相关性排序
    results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
    
    # 限制返回结果数量
    return results[:2]

# 格式化结果
def format_results(results, question):
    """格式化搜索结果"""
    if not results:
        return None
    
    formatted = []
    for idx, result in enumerate(results[:3]):  # 最多返回3个结果
        # 提取内容（移除标记）
        content = result['content']
        content = re.sub(r"【📍\s*景区】[^\n]*\n?", "", content)
        content = re.sub(r"【📌\s*简介】", "", content)
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = content.strip()
        
        # 根据查询意图提取相关部分
        query_lower = question.lower()
        if '时间' in query_lower or '开放' in query_lower:
            # 提取开放时间相关内容
            time_pattern = re.compile(r'(开放时间|营业时间).*?(\n|$)', re.DOTALL)
            time_match = time_pattern.search(content)
            if time_match:
                content = time_match.group(0)
        elif '门票' in query_lower or '价格' in query_lower:
            # 提取门票相关内容
            ticket_pattern = re.compile(r'(门票|价格).*?(\n|$)', re.DOTALL)
            ticket_match = ticket_pattern.search(content)
            if ticket_match:
                content = ticket_match.group(0)
        elif '地址' in query_lower or '位置' in query_lower:
            # 提取地址相关内容
            address_pattern = re.compile(r'(地址|位置).*?(\n|$)', re.DOTALL)
            address_match = address_pattern.search(content)
            if address_match:
                content = address_match.group(0)
        elif '特色' in query_lower:
            # 提取特色相关内容
            feature_pattern = re.compile(r'(特色|特点).*?(\n\n|$)', re.DOTALL)
            feature_match = feature_pattern.search(content)
            if feature_match:
                content = feature_match.group(0)
        elif '历史' in query_lower:
            # 提取历史相关内容
            history_pattern = re.compile(r'(历史|由来).*?(\n\n|$)', re.DOTALL)
            history_match = history_pattern.search(content)
            if history_match:
                content = history_match.group(0)
        elif '美食' in query_lower:
            # 提取美食相关内容
            food_pattern = re.compile(r'(美食|小吃).*?(\n\n|$)', re.DOTALL)
            food_match = food_pattern.search(content)
            if food_match:
                content = food_match.group(0)
        
        if content:
            # 限制内容长度
            if len(content) > 500:
                content = content[:500] + "..."
            formatted.append(f"【{idx+1}】{content}")
    
    return formatted

# 主函数
def main():
    """主函数"""
    print("✅ 颍小智已上线！俺是咱颍上的旅游小管家~\n")
    
    # 加载文件
    files = load_scenic_files()
    print(f"📚 加载了 {len(files)} 个景区文件")
    for file in files:
        print(f"   ✓ {file['scenic']}")
    print()
    
    # 问答循环
    while True:
        try:
            question = input("👉 您想问啥？（输入q退出）: ").strip()
            if question.lower() in ['q', 'quit', '退出']:
                print("\n🌾 颍小智：慢走啊！有空常来颍上耍~")
                break
            if not question:
                print("🌾 颍小智：俺等着哩！您说说想了解啥？\n")
                continue
            
            # 搜索内容
            results = search_content(question, files)
            formatted_results = format_results(results, question)
            
            # 生成回答
            if formatted_results:
                context = "\n\n".join(formatted_results)
                scenic_set = {result['scenic'] for result in results}
                scenic_list = "、".join(sorted(scenic_set)) if scenic_set else "颍上核心景区"
                
                print("\n" + "="*50)
                print("🌾 颍小智：")
                print(f"（眼睛一亮）关于「{question}」，俺给您说道说道：\n")
                print(context)
                print(f"\n💡 小提示：以上内容来自 {scenic_list}")
                print("📍 想了解更细？直接问：'管仲老街几点关门？''迪沟观鸟最佳时间？'")
                print("="*50 + "\n")
            else:
                print("\n" + "="*50)
                print("🌾 颍小智：")
                print(f"哎呀！俺在资料库里没找到「{question}」的详细信息~\n")
                print("💡 建议您：")
                print("1️⃣ 换个问法（比如'管仲老街特色？'）")
                print("2️⃣ 问具体景区：八里河/管仲老街/迪沟/尤家花园/五里湖")
                print("3️⃣ 联系颍上文旅局：0558-XXXXXXX（资料库持续更新！）")
                print("\n❤️ 感谢您关注咱颍上！有空常来耍~")
                print("="*50 + "\n")
                
        except KeyboardInterrupt:
            print("\n\n🌾 颍小智：俺先歇会儿~ 随时喊俺！")
            break
        except Exception as e:
            print(f"\n❌ 遇到小问题：{str(e)}\n💡 请重试或联系技术支持\n")

if __name__ == "__main__":
    main()
