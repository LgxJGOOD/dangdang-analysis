import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ==================== 中文解决方案 ====================
import matplotlib
matplotlib.use('Agg')

import matplotlib.font_manager as fm
import os

font_paths = [
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simhei.ttf',
]

for font_path in font_paths:
    if os.path.exists(font_path):
        try:
            fm.fontManager.addfont(font_path)
            font_prop = fm.FontProperties(fname=font_path)
            plt.rcParams['font.family'] = font_prop.get_name()
            print(f"成功加载字体: {font_path}")
            break
        except:
            continue

plt.rcParams['axes.unicode_minus'] = False

# 读取数据
df = pd.read_csv('dangdang_books_cleaned.csv', encoding='utf-8-sig')

print(f"数据加载成功！共{len(df)}条记录")
print(f"各类别数量:\n{df['分类'].value_counts()}")

# 创建图表文件夹
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

# ==================== 图表1：各类别推荐指数对比（核心图表）====================
fig, ax = plt.subplots(figsize=(12, 7))

# 计算每个类别的推荐指数统计
category_rating = df.groupby('分类')['推荐指数'].agg(['mean', 'median', 'std', 'count']).sort_values('mean', ascending=False)

# 创建分组条形图
x_pos = range(len(category_rating))
width = 0.35

bars1 = ax.bar([i - width/2 for i in x_pos], category_rating['mean'],
               width, label='平均推荐指数', color='steelblue', alpha=0.8)
bars2 = ax.bar([i + width/2 for i in x_pos], category_rating['median'],
               width, label='中位数推荐指数', color='coral', alpha=0.8)

ax.set_xticks(x_pos)
ax.set_xticklabels(category_rating.index, fontsize=11)
ax.set_ylabel('推荐指数', fontsize=12)
ax.set_title('各类别图书推荐指数对比（均值 vs 中位数）', fontsize=15, fontweight='bold')
ax.set_ylim(0, 5.5)
ax.legend(loc='upper right')
ax.axhline(y=df['推荐指数'].mean(), color='green', linestyle='--',
           label=f'总体均值: {df["推荐指数"].mean():.2f}', alpha=0.7)
ax.grid(axis='y', alpha=0.3)

# 添加数值标签
for i, (idx, row) in enumerate(category_rating.iterrows()):
    ax.text(i - width/2, row['mean'] + 0.08, f"{row['mean']:.2f}",
            ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.text(i + width/2, row['median'] + 0.08, f"{row['median']:.2f}",
            ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.savefig('visualizations/1_category_rating_comparison.png', dpi=200, bbox_inches='tight')
plt.close()
print("✓ 已生成: 1_category_rating_comparison.png (各类别推荐指数对比)")

# ==================== 图表2：高推荐指数图书分布 ====================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：推荐指数分布
df['推荐等级'] = pd.cut(df['推荐指数'],
                         bins=[0, 3, 3.5, 4, 4.5, 5],
                         labels=['较差(0-3)', '一般(3-3.5)', '良好(3.5-4)',
                                 '优秀(4-4.5)', '强烈推荐(4.5-5)'])
rating_dist = df['推荐等级'].value_counts()
colors = ['#e74c3c', '#f39c12', '#f1c40f', '#3498db', '#2ecc71']
bars = axes[0].bar(range(len(rating_dist)), rating_dist.values, color=colors, edgecolor='black')
axes[0].set_xticks(range(len(rating_dist)))
axes[0].set_xticklabels(rating_dist.index, rotation=45, ha='right')
axes[0].set_ylabel('图书数量（本）', fontsize=11)
axes[0].set_title('推荐指数分布情况', fontsize=13, fontweight='bold')
for bar, count in zip(bars, rating_dist.values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                 str(count), ha='center', va='bottom', fontsize=10)
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                 f"{count/len(df)*100:.1f}%", ha='center', va='center', fontsize=11, color='white', fontweight='bold')

# 右图：各类别高推荐指数图书占比（推荐指数≥4.5）
high_rating = df[df['推荐指数'] >= 4.5]
category_high_rating = high_rating.groupby('分类').size() / df.groupby('分类').size() * 100
category_high_rating = category_high_rating.sort_values(ascending=False)

y_pos = range(len(category_high_rating))
axes[1].barh(y_pos, category_high_rating.values, color='#2ecc71', edgecolor='black')
axes[1].set_yticks(y_pos)
axes[1].set_yticklabels(category_high_rating.index)
axes[1].set_xlabel('高推荐图书占比 (%)', fontsize=11)
axes[1].set_title('各类别中强烈推荐图书(≥4.5分)占比', fontsize=13, fontweight='bold')
for i, (idx, value) in enumerate(category_high_rating.items()):
    axes[1].text(value + 1, i, f'{value:.1f}%', va='center', fontsize=10)

plt.tight_layout()
plt.savefig('visualizations/2_high_rating_analysis.png', dpi=200, bbox_inches='tight')
plt.close()
print("✓ 已生成: 2_high_rating_analysis.png (高推荐指数分析)")

# ==================== 图表3：出版社推荐指数TOP10 ====================
fig, ax = plt.subplots(figsize=(12, 8))

# 筛选出版图书数量≥3本的出版社
publisher_stats = df.groupby('出版社')['推荐指数'].agg(['mean', 'count', 'std'])
publisher_stats = publisher_stats[publisher_stats['count'] >= 3].sort_values('mean', ascending=False).head(10)

# 添加误差线（标准差）
y_pos = range(len(publisher_stats))
bars = ax.barh(y_pos, publisher_stats['mean'].values,
               xerr=publisher_stats['std'].values,
               capsize=3, color='teal', alpha=0.7, edgecolor='black')

ax.set_yticks(y_pos)
ax.set_yticklabels(publisher_stats.index, fontsize=10)
ax.set_xlabel('平均推荐指数', fontsize=12)
ax.set_title('出版社推荐指数TOP10（出版≥3本，带误差线表示波动）', fontsize=14, fontweight='bold')
ax.axvline(x=df['推荐指数'].mean(), color='red', linestyle='--',
           label=f'总体均值: {df["推荐指数"].mean():.2f}')
ax.set_xlim(0, 5.5)

# 添加数值标签
for i, (idx, row) in enumerate(publisher_stats.iterrows()):
    ax.text(row['mean'] + 0.1, i, f"{row['mean']:.2f} (n={int(row['count'])})",
            va='center', fontsize=9)

ax.legend()
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('visualizations/3_publisher_rating_top10.png', dpi=200, bbox_inches='tight')
plt.close()
print("✓ 已生成: 3_publisher_rating_top10.png (出版社推荐指数TOP10)")

# ==================== 图表4：折扣与推荐指数的真实关系 ====================
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 左图：散点图
scatter = axes[0].scatter(df['折扣'], df['推荐指数'],
                          alpha=0.6, c=df['现价(元)'],
                          cmap='viridis', s=50, edgecolors='black', linewidth=0.5)
axes[0].set_xlabel('折扣', fontsize=11)
axes[0].set_ylabel('推荐指数', fontsize=11)
axes[0].set_title('折扣与推荐指数关系（颜色=价格）', fontsize=13, fontweight='bold')
axes[0].grid(alpha=0.3)
cbar = plt.colorbar(scatter, ax=axes[0])
cbar.set_label('现价(元)', fontsize=10)

# 添加趋势线
z = np.polyfit(df['折扣'], df['推荐指数'], 1)
p = np.poly1d(z)
axes[0].plot(df['折扣'].sort_values(), p(df['折扣'].sort_values()),
             "r--", linewidth=2, label=f'趋势线 (斜率: {z[0]:.3f})')
axes[0].legend()

# 右图：按折扣分组对比推荐指数
df['折扣分组'] = pd.cut(df['折扣'],
                         bins=[0, 0.3, 0.5, 0.7, 0.9, 2],
                         labels=['超高折扣\n(<3折)', '高折扣\n(3-5折)',
                                 '中等折扣\n(5-7折)', '较低折扣\n(7-9折)',
                                 '低折扣\n(≥9折)'])

discount_rating = df.groupby('折扣分组', observed=True)['推荐指数'].agg(['mean', 'median', 'count'])
# 计算置信区间
discount_rating['std'] = df.groupby('折扣分组', observed=True)['推荐指数'].std()

x_pos = range(len(discount_rating))
bars = axes[1].bar(x_pos, discount_rating['mean'].values,
                   yerr=discount_rating['std'].values, capsize=5,
                   color='coral', alpha=0.7, edgecolor='black')
axes[1].set_xticks(x_pos)
axes[1].set_xticklabels(discount_rating.index)
axes[1].set_ylabel('推荐指数', fontsize=11)
axes[1].set_title('不同折扣等级的平均推荐指数（带波动范围）', fontsize=13, fontweight='bold')
axes[1].set_ylim(0, 5)
axes[1].axhline(y=df['推荐指数'].mean(), color='blue', linestyle='--',
                label=f'总体均值: {df["推荐指数"].mean():.2f}')

for i, (idx, row) in enumerate(discount_rating.iterrows()):
    axes[1].text(i, row['mean'] + 0.1, f"{row['mean']:.2f}",
                 ha='center', va='bottom', fontsize=10, fontweight='bold')
    axes[1].text(i, row['mean'] - 0.25, f"n={int(row['count'])}",
                 ha='center', va='top', fontsize=9)

axes[1].legend()
plt.tight_layout()
plt.savefig('visualizations/4_discount_vs_rating.png', dpi=200, bbox_inches='tight')
plt.close()
print("✓ 已生成: 4_discount_vs_rating.png (折扣与推荐指数关系)")

# ==================== 图表5：各类别推荐指数箱线图（看分布差异）====================
fig, ax = plt.subplots(figsize=(12, 7))

# 准备箱线图数据
categories = df['分类'].unique()
data_to_plot = [df[df['分类'] == cat]['推荐指数'].values for cat in categories]

bp = ax.boxplot(data_to_plot, labels=categories, patch_artist=True, showmeans=True)

# 设置箱线图颜色
colors_box = plt.cm.Set3(np.linspace(0, 1, len(categories)))
for patch, color in zip(bp['boxes'], colors_box):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

# 添加均值点样式
for mean in bp['means']:
    mean.set(marker='D', color='red', markersize=8)

ax.set_ylabel('推荐指数', fontsize=12)
ax.set_title('各类别推荐指数分布对比（箱线图）', fontsize=15, fontweight='bold')
ax.axhline(y=df['推荐指数'].mean(), color='green', linestyle='--',
           label=f'总体均值: {df["推荐指数"].mean():.2f}')
ax.legend()
ax.grid(axis='y', alpha=0.3)

plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('visualizations/5_rating_boxplot.png', dpi=200, bbox_inches='tight')
plt.close()
print("✓ 已生成: 5_rating_boxplot.png (各类别推荐指数箱线图)")

# ==================== 生成分析报告 ====================
print("\n" + "="*60)
print("核心分析报告（基于推荐指数）")
print("="*60)

# 计算关键指标
overall_avg_rating = df['推荐指数'].mean()
high_rating_books = df[df['推荐指数'] >= 4.5]
excellent_categories = category_rating[category_rating['mean'] >= 4.0]

print(f"""
【总体评价】
- 总体平均推荐指数: {overall_avg_rating:.2f}/5.00
- 强烈推荐图书(≥4.5分): {len(high_rating_books)}本 ({len(high_rating_books)/len(df)*100:.1f}%)
- 表现优秀类别(平均≥4分): {len(excellent_categories)}个

【各类别质量排名（按推荐指数）】
""")

for i, (idx, row) in enumerate(category_rating.iterrows(), 1):
    stars = '⭐' * int(row['mean'])
    print(f"{i}. {idx}: {row['mean']:.2f} {stars} (中位数:{row['median']:.2f}, 波动:{row['std']:.2f})")

print(f"""
【折扣与质量的关系】
折扣<5折图书平均推荐指数: {df[df['折扣'] < 0.5]['推荐指数'].mean():.2f}
折扣≥7折图书平均推荐指数: {df[df['折扣'] >= 0.7]['推荐指数'].mean():.2f}
结论: {"低折扣图书质量更好" if df[df['折扣'] < 0.5]['推荐指数'].mean() > df[df['折扣'] >= 0.7]['推荐指数'].mean() else "高折扣图书质量更好"}

【TOP3高质量出版社】
""")

for i, (idx, row) in enumerate(publisher_stats.head(3).iterrows(), 1):
    print(f"{i}. {idx}: {row['mean']:.2f}分 (出版{int(row['count'])}本)")

print(f"""
【分析结论】
1. 表现最好的类别: {category_rating.index[0]} ({category_rating.iloc[0]['mean']:.2f}分)
2. 表现最差的类别: {category_rating.index[-1]} ({category_rating.iloc[-1]['mean']:.2f}分)
3. 质量差异最大的类别: {category_rating['std'].idxmax()} (标准差{category_rating['std'].max():.2f})
4. 高推荐图书占比最高的类别: {category_high_rating.index[0]} ({category_high_rating.iloc[0]:.1f}%)

生成的分析图表:
  1. 各类别推荐指数对比（核心）
  2. 高推荐指数图书分布
  3. 出版社推荐指数TOP10
  4. 折扣与推荐指数关系
  5. 各类别推荐指数箱线图
""")

# 保存报告
with open('visualizations/analysis_report.txt', 'w', encoding='utf-8') as f:
    f.write("当当网图书质量分析报告\n")
    f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"总图书数: {len(df)}\n")
    f.write(f"总体平均推荐指数: {overall_avg_rating:.2f}/5\n")
    f.write(f"强烈推荐图书: {len(high_rating_books)}本\n\n")
    f.write("各类别平均推荐指数:\n")
    for idx, row in category_rating.iterrows():
        f.write(f"  {idx}: {row['mean']:.2f}\n")

print("\n✅ 分析完成！所有图表已保存到 visualizations 文件夹")