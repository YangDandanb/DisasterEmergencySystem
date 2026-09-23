import requests
import csv
import time
from typing import List, Dict

# ==================== 配置 ====================
KEY = "4e3007a054740dd65a65afeaea1b1503"  # 你的高德Key
OUTPUT_DIR = "./poi_data/"                # 输出文件夹
# 四川省所有地级市（含自治州）名称
CITIES = [
    "成都市", "自贡市", "攀枝花市", "泸州市", "德阳市", "绵阳市",
    "广元市", "遂宁市", "内江市", "乐山市", "南充市", "眉山市",
    "宜宾市", "广安市", "达州市", "雅安市", "巴中市", "资阳市",
    "阿坝藏族羌族自治州", "甘孜藏族自治州", "凉山彝族自治州"
]

# POI分类与搜索关键词映射
POI_TYPES = {
    "hospital": {"keyword": "医院", "output_file": "hospitals.csv"},
    "fire_station": {"keyword": "消防站", "output_file": "fire_stations.csv"},
    "shelter": {"keyword": "避难所", "output_file": "shelters.csv"}   # 若数量少可改用“应急避难场所”
}
# ==============================================

def fetch_pois(city: str, keyword: str, max_pages: int = 20) -> List[Dict]:
    """
    获取指定城市和关键词的POI数据（分页）
    :param city: 城市名称（如"成都市"）
    :param keyword: 搜索关键词（如"医院"）
    :param max_pages: 最大页数（防止死循环）
    :return: POI列表（每个POI为字典）
    """
    all_pois = []
    page = 1
    while page <= max_pages:
        url = "https://restapi.amap.com/v5/place/text"
        params = {
            "keywords": keyword,
            "region": city,
            "city_limit": True,        # 仅返回指定城市数据
            "output": "json",
            "page_size": 50,
            "page_num": page,
            "key": KEY
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.encoding = "utf-8"
            data = resp.json()
        except Exception as e:
            print(f"请求失败: {city} - {keyword} 第{page}页，错误: {e}")
            break

        # 检查状态
        if data.get("status") != "1":
            print(f"API错误: {city} - {keyword}，信息: {data.get('info')}")
            break

        pois = data.get("pois", [])
        if not pois:
            break  # 无数据，结束分页

        all_pois.extend(pois)
        total_count = int(data.get("count", 0))
        # 判断是否还有下一页（如果当前页数据不足50条，说明是最后一页）
        if len(pois) < 50:
            break
        # 或者已经获取到总数量
        if len(all_pois) >= total_count:
            break

        page += 1
        time.sleep(0.2)  # 控制请求频率，避免QPS超限

    print(f"  ✓ {city} 获取 {keyword} 共 {len(all_pois)} 条")
    return all_pois

def parse_poi(poi: Dict) -> Dict:
    """
    提取需要的字段
    """
    location = poi.get("location", "").split(",")  # "经度,纬度"
    lon = location[0] if len(location) > 0 else ""
    lat = location[1] if len(location) > 1 else ""
    return {
        "名称": poi.get("name", ""),
        "地址": poi.get("address", ""),
        "经度": lon,
        "纬度": lat,
        "电话": poi.get("tel", ""),
        "类型": poi.get("type", ""),
        "typecode": poi.get("typecode", ""),
        "城市": poi.get("cityname", ""),
        "adcode": poi.get("adcode", "")
    }

def save_to_csv(pois: List[Dict], filename: str):
    """保存POI列表到CSV文件（UTF-8 with BOM）"""
    if not pois:
        print(f"  ⚠️ 无数据，跳过保存 {filename}")
        return
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    fieldnames = ["名称", "地址", "经度", "纬度", "电话", "类型", "typecode", "城市", "adcode"]
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in pois:
            writer.writerow(p)
    print(f"  ✅ 保存 {len(pois)} 条到 {filepath}")

def main():
    print("=== 高德POI爬虫启动 ===")
    print(f"Key: {KEY[:5]}****{KEY[-5:]}")
    print(f"目标城市: {len(CITIES)} 个")
    print(f"POI类别: {list(POI_TYPES.keys())}")

    # 分别爬取三类POI
    for poi_type, config in POI_TYPES.items():
        keyword = config["keyword"]
        out_file = config["output_file"]
        print(f"\n--- 开始爬取 [{keyword}] ---")
        all_results = []
        for city in CITIES:
            pois = fetch_pois(city, keyword)
            # 解析并收集
            for p in pois:
                all_results.append(parse_poi(p))
        # 去重（基于经纬度+名称简单去重）
        seen = set()
        unique = []
        for item in all_results:
            key = (item["经度"], item["纬度"], item["名称"])
            if key not in seen:
                seen.add(key)
                unique.append(item)
        print(f"  总计获取 {len(all_results)} 条，去重后 {len(unique)} 条")
        save_to_csv(unique, out_file)

    print("\n=== 所有数据爬取完成 ===")

if __name__ == "__main__":
    main()