import pandas as pd
import numpy as np
import re
from datetime import datetime

# 读取数据
df = pd.read_csv('dangdang_books.csv', encoding='utf-8-sig')

print("原始数据信息：")
print(f"数据形状: {df.shape}")
print(f"\n缺失值统计:\n{df.isnull().sum()}")
print(f"\n数据类型:\n{df.dtypes}")
print(f"\n前5行数据预览:\n{df.head()}")

# ==================== 数据清洗与预处理 ====================

# 1. 处理缺失值
print("\n" + "=" * 50)
print("开始数据清洗...")
print("=" * 50)

# 1.1 书名缺失的处理（删除，因为书名是关键字段）
df = df.dropna(subset=['书名'])
print(f"删除书名为空的记录后，剩余 {len(df)} 条")

# 1.2 过滤异常记录（作者为"加入购物车"等无效值）
invalid_authors = ['加入购物车', '']
df = df[~df['作者'].isin(invalid_authors)]
print(f"删除作者异常的记录后，剩余 {len(df)} 条")

# 1.3 填充其他缺失值
df['作者'] = df['作者'].fillna('未知作者')
df['出版社'] = df['出版社'].fillna('未知出版社')
df['出版时间'] = df['出版时间'].fillna('未知')
df['现价'] = df['现价'].fillna('0')
df['原价'] = df['原价'].fillna('0')
df['折扣'] = df['折扣'].fillna('0')
df['评论数'] = df['评论数'].fillna('0')
df['推荐指数'] = df['推荐指数'].fillna(0)


# 2. 价格数据清洗和转换
def clean_price(price_str):
    """清洗价格字符串，转换为浮点数"""
    if pd.isna(price_str) or price_str == '':
        return 0.0

    # 如果是字符串类型
    if isinstance(price_str, str):
        # 去除¥符号、空格、文字等
        price_str = re.sub(r'[¥￥\s元]', '', price_str)
        # 提取数字和小数点
        match = re.search(r'(\d+\.?\d*)', price_str)
        if match:
            return float(match.group(1))
    return 0.0


# 应用价格清洗
df['现价_clean'] = df['现价'].apply(clean_price)
df['原价_clean'] = df['原价'].apply(clean_price)


# 3. 折扣转换（从百分比字符串转换为数值）
def clean_discount(discount_str):
    """清洗折扣，转换为小数"""
    if pd.isna(discount_str) or discount_str == '':
        return 0.0

    if isinstance(discount_str, str):
        # 去除括号、空格等
        discount_str = re.sub(r'[()（）\s]', '', discount_str)
        # 提取数字
        match = re.search(r'(\d+\.?\d*)', discount_str)
        if match:
            discount = float(match.group(1))
            # 如果大于10，可能是百分比，转换为小数
            if discount > 10:
                discount = discount / 10
            return round(discount, 1)
    return 0.0


df['折扣_clean'] = df['折扣'].apply(clean_discount)


# 4. 评论数清洗（转换为整数）
def clean_comment_count(comment_str):
    """清洗评论数字符串，转换为整数"""
    if pd.isna(comment_str) or comment_str == '':
        return 0

    if isinstance(comment_str, str):
        # 去除逗号、空格等
        comment_str = re.sub(r'[,，\s]', '', comment_str)
        # 提取数字
        match = re.search(r'(\d+)', comment_str)
        if match:
            return int(match.group(1))
    return 0


df['评论数_clean'] = df['评论数'].apply(clean_comment_count)


# 5. 出版时间清洗（提取年份）
def extract_year(date_str):
    """从出版时间中提取年份"""
    if pd.isna(date_str) or date_str == '未知':
        return None

    if isinstance(date_str, str):
        # 匹配4位数字的年份
        match = re.search(r'(\d{4})', date_str)
        if match:
            year = int(match.group(1))
            # 合理性检查：年份应该在1900-2026之间
            if 1900 <= year <= 2026:
                return year
    return None


df['出版年份'] = df['出版时间'].apply(extract_year)


# 6. 推荐指数清洗（确保在0-5范围内）
def clean_rating(rating):
    """清洗推荐指数，确保在0-5范围内"""
    try:
        rating_float = float(rating)
        # 限制范围
        rating_float = max(0, min(5, rating_float))
        return round(rating_float, 1)
    except (ValueError, TypeError):
        return 0.0


df['推荐指数_clean'] = df['推荐指数'].apply(clean_rating)

# 7. 检测数据异常
print("\n" + "=" * 50)
print("数据异常检测:")
print("=" * 50)

# 7.1 价格异常检测（现价 > 原价）
price_anomaly = df[df['现价_clean'] > df['原价_clean']]
print(f"现价高于原价的异常记录数: {len(price_anomaly)}")
if len(price_anomaly) > 0:
    print(f"  示例: {price_anomaly[['书名', '现价_clean', '原价_clean']].head(3).to_dict('records')}")

# 7.2 折扣异常检测
discount_anomaly = df[(df['折扣_clean'] > 1) | (df['折扣_clean'] < 0)]
print(f"折扣范围异常的记录数: {len(discount_anomaly)}")

# 7.3 评论数为0但其他数据正常
zero_comments = df[df['评论数_clean'] == 0]
print(f"评论数为0的记录数: {len(zero_comments)} ({len(zero_comments) / len(df) * 100:.1f}%)")

# 7.4 重复值检测
duplicates = df[df.duplicated(subset=['书名', '分类'], keep=False)]
print(f"可能存在重复图书的记录数: {len(duplicates)}")

# 8. 创建衍生特征
print("\n" + "=" * 50)
print("创建衍生特征:")
print("=" * 50)

# 8.1 价格差（原价 - 现价）
df['价格差额'] = df['原价_clean'] - df['现价_clean']


# 8.2 折扣力度等级
def discount_level(discount):
    if discount >= 0.9:
        return '折扣低(9-10折)'
    elif discount >= 0.7:
        return '中等折扣(7-9折)'
    elif discount >= 0.5:
        return '较高折扣(5-7折)'
    elif discount >= 0.3:
        return '高折扣(3-5折)'
    else:
        return '超高折扣(<3折)'


df['折扣等级'] = df['折扣_clean'].apply(discount_level)


# 8.3 图书热度等级（基于评论数）
def popularity_level(comment_count):
    if comment_count >= 100000:
        return '爆款(>10w评论)'
    elif comment_count >= 50000:
        return '热门(5-10w评论)'
    elif comment_count >= 10000:
        return '较热(1-5w评论)'
    elif comment_count >= 1000:
        return '一般(1000-1w评论)'
    else:
        return '冷门(<1000评论)'


df['热度等级'] = df['评论数_clean'].apply(popularity_level)


# 8.4 推荐等级
def rating_level(rating):
    if rating >= 4.5:
        return '强烈推荐'
    elif rating >= 4.0:
        return '推荐'
    elif rating >= 3.0:
        return '一般'
    else:
        return '不推荐'


df['推荐等级'] = df['推荐指数_clean'].apply(rating_level)

# 9. 保存清洗后的数据
print("\n" + "=" * 50)
print("保存清洗后的数据:")
print("=" * 50)

# 选择需要保存的列
columns_to_save = [
    '分类', '书名', '作者', '出版社', '出版年份', '出版时间',
    '现价_clean', '原价_clean', '折扣_clean', '折扣等级',
    '推荐指数_clean', '推荐等级', '评论数_clean', '热度等级',
    '价格差额', '图书链接', '页码', '采集时间'
]

# 重命名列为更友好的名称
df_clean = df[columns_to_save].copy()
df_clean.columns = [
    '分类', '书名', '作者', '出版社', '出版年份', '原始出版时间',
    '现价(元)', '原价(元)', '折扣', '折扣等级',
    '推荐指数', '推荐等级', '评论数', '热度等级',
    '价格差额(元)', '图书链接', '页码', '采集时间'
]

# 保存清洗后的数据
df_clean.to_csv('dangdang_books_cleaned.csv', index=False, encoding='utf-8-sig')
print(f"清洗后的数据已保存: dangdang_books_cleaned.csv")
print(f"数据形状: {df_clean.shape}")

# 10. 数据统计分析
print("\n" + "=" * 50)
print("数据统计分析:")
print("=" * 50)

print(f"\n总体统计:")
print(f"图书总数: {len(df_clean)}")
print(f"图书分类数: {df_clean['分类'].nunique()}")
print(f"出版社数量: {df_clean['出版社'].nunique()}")
print(f"平均价格: 现价{df_clean['现价(元)'].mean():.2f}元, 原价{df_clean['原价(元)'].mean():.2f}元")
print(f"平均折扣: {df_clean['折扣'].mean():.2f}")
print(f"平均推荐指数: {df_clean['推荐指数'].mean():.2f}")
print(f"总评论数: {df_clean['评论数'].sum():,}")

print(f"\n各分类图书数量:")
category_stats = df_clean['分类'].value_counts()
for cat, count in category_stats.items():
    print(f"  {cat}: {count}本 ({count / len(df_clean) * 100:.1f}%)")

print(f"\n折扣等级分布:")
discount_dist = df_clean['折扣等级'].value_counts()
for level, count in discount_dist.items():
    print(f"  {level}: {count}本 ({count / len(df_clean) * 100:.1f}%)")

print(f"\n热度等级分布:")
hot_dist = df_clean['热度等级'].value_counts()
for level, count in hot_dist.items():
    print(f"  {level}: {count}本 ({count / len(df_clean) * 100:.1f}%)")

# 11. 生成数据清洗报告
print("\n" + "=" * 50)
print("生成数据清洗报告:")
print("=" * 50)

report = f"""
数据清洗报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
原始数据文件: dangdang_books.csv
清洗后文件: dangdang_books_cleaned.csv

清洗操作记录:
1. 删除书名为空的记录
2. 填充缺失值: 作者、出版社、出版时间、价格、评论数等
3. 价格数据清洗: 提取数字并转换为浮点数
4. 折扣数据清洗: 转换为小数格式(0-1之间)
5. 评论数清洗: 转换为整数格式
6. 出版时间清洗: 提取年份信息
7. 推荐指数清洗: 确保在0-5范围内
8. 创建衍生特征: 价格差、折扣等级、热度等级、推荐等级

数据质量指标:
- 总记录数: {len(df_clean)}
- 价格异常(现价>原价): {len(price_anomaly)}条
- 重复记录: {len(duplicates)}条
- 评论数为0: {len(zero_comments)}条 ({len(zero_comments) / len(df) * 100:.1f}%)

建议后续分析方向:
1. 不同分类的图书价格分布分析
2. 折扣与销量(评论数)的相关性分析
3. 出版社的图书质量和受欢迎程度分析
4. 出版年份与图书热度的趋势分析
5. 推荐指数与实际销量的一致性分析
"""

# 保存清洗报告
with open('data_cleaning_report.txt', 'w', encoding='utf-8') as f:
    f.write(report)

print(report)
print("\n数据预处理完成！")
print("生成文件:")
print("  - dangdang_books_cleaned.csv (清洗后的数据)")
print("  - data_cleaning_report.txt (清洗报告)")