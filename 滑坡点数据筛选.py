import pandas as pd

INPUT_FILE = r"C:\Crack\地质灾害应急系统\Data\基于新闻数据的中国大陆高精度滑坡事件数据集(2008-2024年)-数据实体\基于新闻数据的中国大陆高精度滑坡事件数据集(2008-2024年)-数据实体\LandslideEvents_Chinese.xlsx"
OUTPUT_FILE = r"C:\Crack\地质灾害应急系统\Data\landslide_sichuan.xlsx"
TARGET_PROVINCE = "四川省"

# 手动指定所有列名（共27列，第21列是经度，第22列是纬度）
column_names = [
    "滑坡编号", "新闻编号", "新闻标题", "新闻网址", "滑坡发生时间",
    "年", "月", "日", "时", "分", "时段", "时间精度",
    "滑坡发生地址", "省", "市", "县", "镇", "村", "地点",
    "空间精度", "地理编码", "经度", "纬度",  # 这里 U列 = 经度, V列 = 纬度
    "诱发因素", "死亡人数", "受伤人数", "失踪人数"
]

# 读取数据：跳过前两行（第一行是大类，第二行是具体字段），直接从第三行开始读
df = pd.read_excel(INPUT_FILE, skiprows=2, header=None)
df.columns = column_names

# 筛选四川省
df_sichuan = df[df["省"] == TARGET_PROVINCE].copy()

# 保留你需要的列（明确包含经度、纬度）
keep_columns = [
    "滑坡编号",
    "年", "月", "日", "时", "分",
    "省", "市", "县",
    "经度", "纬度",          # 这就是 U 列和 V 列
    "诱发因素",
    "死亡人数", "受伤人数", "失踪人数"
]
existing_keep = [col for col in keep_columns if col in df_sichuan.columns]
df_sichuan = df_sichuan[existing_keep]

# 保存
df_sichuan.to_excel(OUTPUT_FILE, index=False)

print(f"✅ 处理完成！共保留 {len(df_sichuan)} 条四川省记录。")
print(f"📁 输出文件：{OUTPUT_FILE}")