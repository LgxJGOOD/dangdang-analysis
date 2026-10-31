import requests
from bs4 import BeautifulSoup
import csv
import os
import time
import re
from datetime import datetime

headers = {
    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
}

# 分类
categories = {
    "小说": "http://category.dangdang.com/pg{page}-cp01.03.00.00.00.00.html",
    "文学": "http://category.dangdang.com/pg{page}-cp01.05.00.00.00.00.html",
    "历史": "http://category.dangdang.com/pg{page}-cp01.36.00.00.00.00.html",
    "经济管理": "http://category.dangdang.com/pg{page}-cp01.22.00.00.00.00.html",
    "计算机": "http://category.dangdang.com/pg{page}-cp01.54.00.00.00.00.html"
}

csv_file = "dangdang_books.csv"

# 创建文件
if not os.path.exists(csv_file):
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "分类",
            "书名",
            "作者",
            "出版时间",
            "出版社",
            "现价",
            "原价",
            "折扣",
            "推荐指数",
            "评论数",
            "图书链接",
            "页码",
            "采集时间"
        ])

MAX_PAGE = 20

for category_name, url_template in categories.items():

    print(f"\n开始采集【{category_name}】")

    for page in range(1, MAX_PAGE + 1):

        url = url_template.format(page=page)

        try:

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

            response.encoding = "gbk"

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            books = soup.select("ul.bigimg li")

            if not books:
                break

            rows = []

            for book in books:

                try:

                    # 书名
                    title = ""
                    title_node = book.select_one("p.name a")

                    if title_node:
                        title = (
                            title_node.get("title", "")
                            .replace("\n", "")
                            .replace("\r", "")
                            .strip()
                        )

                    # 链接
                    book_url = ""
                    if title_node:
                        book_url = title_node.get("href", "")

                    # 作者
                    author = ""
                    author_node = book.select_one(
                        ".search_book_author a"
                    )

                    if author_node:
                        author = author_node.text.strip()

                    # 出版时间、出版社
                    publish_date = ""
                    publisher = ""

                    spans = book.select(
                        ".search_book_author span"
                    )

                    if len(spans) >= 2:
                        publish_date = (
                            spans[1]
                            .get_text()
                            .replace("/", "")
                            .strip()
                        )

                    if len(spans) >= 3:

                        pub_node = spans[2].select_one("a")

                        if pub_node:
                            publisher = (
                                pub_node.text.strip()
                            )

                    # 现价
                    current_price = ""

                    node = book.select_one(
                        ".search_now_price"
                    )

                    if node:
                        current_price = node.text.strip()

                    # 原价
                    original_price = ""

                    node = book.select_one(
                        ".search_pre_price"
                    )

                    if node:
                        original_price = node.text.strip()

                    # 折扣
                    discount = ""

                    discount_nodes = book.select(
                        "span.search_discount"
                    )

                    if discount_nodes:

                        discount = (
                            discount_nodes[-1]
                            .text
                            .replace("(", "")
                            .replace(")", "")
                            .replace("\xa0", "")
                            .strip()
                        )

                    # 评论数
                    comment_count = ""

                    node = book.select_one(
                        ".search_comment_num"
                    )

                    if node:
                        comment_count = node.text.strip()

                    # 推荐指数
                    rating = ""

                    star_node = book.select_one(
                        ".search_star_black span"
                    )

                    if star_node:

                        style = star_node.get(
                            "style",
                            ""
                        )

                        m = re.search(
                            r'width:\s*([\d.]+)%',
                            style
                        )

                        if m:

                            percent = float(
                                m.group(1)
                            )

                            rating = round(
                                percent / 20,
                                1
                            )

                    rows.append([
                        category_name,
                        title,
                        author,
                        publish_date,
                        publisher,
                        current_price,
                        original_price,
                        discount,
                        rating,
                        comment_count,
                        book_url,
                        page,
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    ])

                except:
                    continue

            with open(
                csv_file,
                "a",
                newline="",
                encoding="utf-8-sig"
            ) as f:

                writer = csv.writer(f)
                writer.writerows(rows)

            print(
                f"第{page}页完成，保存{len(rows)}条"
            )

            time.sleep(1)

        except Exception as e:

            print(
                f"{category_name} 第{page}页失败：{e}"
            )

print("\n全部采集完成！")