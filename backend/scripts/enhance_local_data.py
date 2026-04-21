# -*- coding: utf-8 -*-
"""颍上旅游数据增强脚本"""
import os
import re

print("="*60)
print("📊 颍上旅游数据增强")
print("="*60)

# 景区信息增强配置
ENHANCED_INFO = {
    "八里河": {
        "别名": ["八里河风景区", "八里河旅游区", "天下第一农民公园"],
        "级别": "国家5A级旅游景区",
        "特色": ["自然风光", "人文景观", "亲子游乐", "湿地生态"],
        "最佳游览时间": "春季（3-5月）和秋季（9-11月）",
        "建议游玩时长": "4-6小时",
        "交通指南": "".join([
            "1. 自驾：从阜阳出发，沿S102省道至颍上县，再沿八里河大道即可到达\n",
            "2. 公交：颍上县城有直达景区的公交车，约20分钟车程\n",
            "3. 高铁：从颍上北站下车后，可乘坐出租车或公交车前往"
        ]),
        "周边景点": ["管仲老街", "明清苑", "江心洲滨河公园"]
    },
    "管仲老街": {
        "别名": ["管仲文化街", "颍上老街"],
        "级别": "国家4A级旅游景区",
        "特色": ["历史文化", "明清建筑", "水乡风情", "民俗表演"],
        "最佳游览时间": "傍晚（17:00-22:00）",
        "建议游玩时长": "2-3小时",
        "交通指南": "".join([
            "1. 自驾：直接导航至"管仲老街"，景区有停车场\n",
            "2. 公交：颍上县城内多条公交线路可达\n",
            "3. 步行：从县城中心步行约10分钟即可到达"
        ]),
        "周边景点": ["明清苑", "江心洲滨河公园", "管鲍祠"]
    },
    "尤家花园": {
        "别名": ["淮上公园", "人民公园"],
        "级别": "国家3A级旅游景区",
        "特色": ["江南园林", "苏式建筑", "盆景艺术", "历史文化"],
        "最佳游览时间": "春季（4-5月）和秋季（10-11月）",
        "建议游玩时长": "2-3小时",
        "交通指南": "".join([
            "1. 自驾：导航至"尤家花园"，景区有停车场\n",
            "2. 公交：颍上县城有公交车直达\n",
            "3. 出租车：从县城中心打车约15分钟"
        ]),
        "周边景点": ["管仲老街", "明清苑"]
    },
    "迪沟生态园": {
        "别名": ["迪沟生态旅游风景区", "迪沟景区"],
        "级别": "国家4A级旅游景区",
        "特色": ["生态湿地", "珍稀动物", "地质奇观", "科普教育"],
        "最佳游览时间": "夏季（6-8月）和秋季（9-10月）",
        "建议游玩时长": "3-4小时",
        "交通指南": "".join([
            "1. 自驾：从颍上县城沿S102省道至迪沟镇\n",
            "2. 公交：颍上县城有前往迪沟的班车\n",
            "3. 出租车：从县城打车约30分钟"
        ]),
        "周边景点": ["小张庄公园"]
    },
    "湿地公园": {
        "别名": ["五里湖湿地公园", "五里湖生态公园"],
        "级别": "国家4A级旅游景区",
        "特色": ["湿地生态", "自然景观", "鸟类栖息地", "城市氧吧"],
        "最佳游览时间": "春季（3-5月）和秋季（10-11月）",
        "建议游玩时长": "2-3小时",
        "交通指南": "".join([
            "1. 自驾：导航至"五里湖湿地公园"\n",
            "2. 公交：颍上县城内多条公交线路可达\n",
            "3. 步行：从县城中心步行约20分钟"
        ]),
        "周边景点": ["管仲老街", "江心洲滨河公园"]
    },
    "江心洲": {
        "别名": ["江心洲滨河公园", "颍上江心洲"],
        "级别": "国家4A级旅游景区",
        "特色": ["文化公园", "滨河景观", "历史建筑", "休闲娱乐"],
        "最佳游览时间": "傍晚（18:00-20:00）",
        "建议游玩时长": "2-3小时",
        "交通指南": "".join([
            "1. 自驾：导航至"江心洲滨河公园"\n",
            "2. 公交：颍上县城内多条公交线路可达\n",
            "3. 步行：从县城中心步行约15分钟"
        ]),
        "周边景点": ["明清苑", "管仲老街", "湿地公园"]
    },
    "明清苑": {
        "别名": ["颍上明清苑", "皖北第一苑"],
        "级别": "国家4A级旅游景区",
        "特色": ["古建筑群", "南北建筑风格", "历史文化", "古风摄影"],
        "最佳游览时间": "上午（9:00-11:00）",
        "建议游玩时长": "1-2小时",
        "交通指南": "".join([
            "1. 自驾：导航至"明清苑"，位于江心洲滨河公园内\n",
            "2. 公交：颍上县城内多条公交线路可达\n",
            "3. 步行：从县城中心步行约15分钟"
        ]),
        "周边景点": ["江心洲滨河公园", "管仲老街"]
    },
    "管鲍祠": {
        "别名": ["管仲鲍叔牙祠", "管仲纪念馆"],
        "级别": "安徽省文物保护单位",
        "特色": ["历史文化", "名人纪念", "古建筑", "文化教育"],
        "最佳游览时间": "上午（9:00-11:00）",
        "建议游玩时长": "1小时",
        "交通指南": "".join([
            "1. 自驾：导航至"管鲍祠"，位于管仲公园内\n",
            "2. 公交：颍上县城内多条公交线路可达\n",
            "3. 步行：从县城中心步行约10分钟"
        ]),
        "周边景点": ["管仲老街", "明清苑"]
    },
    "小张庄": {
        "别名": ["小张庄公园", "小张庄生态旅游示范点"],
        "级别": "全国生态农业旅游示范点",
        "特色": ["生态观光", "休闲娱乐", "科普教育", "亲子活动"],
        "最佳游览时间": "春季（4-5月）和秋季（10-11月）",
        "建议游玩时长": "2-3小时",
        "交通指南": "".join([
            "1. 自驾：从颍上县城沿S102省道至谢桥镇小张庄村\n",
            "2. 公交：颍上县城有前往谢桥的班车，在小张庄下车\n",
            "3. 出租车：从县城打车约25分钟"
        ]),
        "周边景点": ["迪沟生态园"]
    }
}

def read_existing_data():
    """读取现有数据"""
    existing_data = {}
    
    # 读取颍上景区介绍.txt
    if os.path.exists("颍上景区介绍.txt"):
        with open("颍上景区介绍.txt", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 分割各个景区的内容
        sections = re.split(r'\n\n(?=[^\n]+：)', content)
        
        for section in sections:
            if section.strip():
                # 提取景区名称
                match = re.search(r'^([^：]+)：', section)
                if match:
                    spot_name = match.group(1)
                    existing_data[spot_name] = section
                else:
                    # 处理没有冒号的情况
                    lines = section.split('\n')
                    if lines:
                        spot_name = lines[0].strip()
                        existing_data[spot_name] = section
    
    return existing_data

def enhance_data(existing_data):
    """增强数据"""
    enhanced_data = []
    
    for spot_name, content in existing_data.items():
        # 找到对应的增强信息
        for key, info in ENHANCED_INFO.items():
            if key in spot_name:
                # 构建增强后的内容
                enhanced_content = []
                enhanced_content.append(f"{spot_name}景区")
                enhanced_content.append("=" * 40)
                
                # 保留原有内容
                enhanced_content.append("\n【原有信息】")
                enhanced_content.append(content)
                
                # 添加增强信息
                enhanced_content.append("\n【增强信息】")
                
                if "别名" in info:
                    enhanced_content.append(f"别名：{', '.join(info['别名'])}")
                
                if "级别" in info:
                    enhanced_content.append(f"景区级别：{info['级别']}")
                
                if "特色" in info:
                    enhanced_content.append(f"景区特色：{', '.join(info['特色'])}")
                
                if "最佳游览时间" in info:
                    enhanced_content.append(f"最佳游览时间：{info['最佳游览时间']}")
                
                if "建议游玩时长" in info:
                    enhanced_content.append(f"建议游玩时长：{info['建议游玩时长']}")
                
                if "交通指南" in info:
                    enhanced_content.append("交通指南：")
                    enhanced_content.append(info['交通指南'])
                
                if "周边景点" in info:
                    enhanced_content.append(f"周边景点：{', '.join(info['周边景点'])}")
                
                enhanced_data.append('\n'.join(enhanced_content))
                break
        else:
            # 如果没有找到对应的增强信息，保留原有内容
            enhanced_data.append(content)
    
    return enhanced_data

def main():
    """主函数"""
    print("🔍 读取现有数据...")
    existing_data = read_existing_data()
    
    if not existing_data:
        print("❌ 未找到现有数据！")
        return
    
    print(f"✅ 找到 {len(existing_data)} 个景区的数据")
    
    print("\n🚀 增强数据...")
    enhanced_data = enhance_data(existing_data)
    
    # 保存增强后的数据
    output_file = "颍上景区介绍_增强版.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('\n\n'.join(enhanced_data))
    
    print(f"\n✅ 数据增强完成！")
    print(f"📁 保存至: {output_file}")
    print(f"📝 增强后数据长度: {os.path.getsize(output_file)} 字节")
    
    print("\n💡 后续步骤：")
    print("   1. 查看增强后的数据文件")
    print("   2. 运行 prepare_data.py 预处理数据")
    print("   3. 运行 build_vector_db.py 更新向量库")

if __name__ == "__main__":
    main()
