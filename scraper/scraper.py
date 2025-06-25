import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import os

# 定义文件路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_PATH = os.path.join(BASE_DIR, 'scraper', 'mock_data.html')
CSV_PATH = os.path.join(BASE_DIR, 'data', 'housing_data.csv')

def scrape_and_update_data():
    """爬取模拟数据并更新CSV文件"""
    # 1. 读取模拟网页内容
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 2. 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 3. 提取数据
    scraped_data = []
    today_str = datetime.now().strftime('%Y-%m-%d')

    city_divs = soup.find_all('div', class_='city-data')
    for city_div in city_divs:
        city_name = city_div.find('h2').text
        table = city_div.find('table')
        rows = table.find('tbody').find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            area = cols[0].text.strip()
            price = int(cols[1].text.strip())
            scraped_data.append({
                'city': city_name,
                'area': area,
                'price': price,
                'date': today_str
            })

    if not scraped_data:
        print("没有抓取到新数据。")
        return

    # 4. 将新数据转换为DataFrame
    new_df = pd.DataFrame(scraped_data)
    print("抓取到的新数据：")
    print(new_df)

    # 5. 追加到现有的CSV文件中
    # a. 读取旧数据
    try:
        existing_df = pd.read_csv(CSV_PATH)
    except FileNotFoundError:
        existing_df = pd.DataFrame()

    # b. 合并新旧数据
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)

    # c. 去重，保留最新的记录
    # 统一日期格式，避免解析错误。
    # 使用 format='mixed' 可以让 pandas 自动处理混合的日期格式 (如 '2025-05' 和 '2025-06-25')
    combined_df['date'] = pd.to_datetime(combined_df['date'], format='mixed')

    # 为了按月更新，我们将所有日期归一化到月份的开头
    combined_df['year_month'] = combined_df['date'].dt.to_period('M')

    # 排序，确保每个月的最新数据排在前面
    combined_df.sort_values('date', ascending=False, inplace=True)

    # 按 city, area, 和 year_month 去重，保留最新的一个
    final_df = combined_df.drop_duplicates(subset=['city', 'area', 'year_month'], keep='first')

    # 将日期格式化为 'YYYY-MM-DD' 保存，统一格式
    final_df['date'] = final_df['date'].dt.strftime('%Y-%m-%d')

    # 清理辅助列并排序
    final_df = final_df.drop(columns=['year_month'])
    final_df.sort_values(['date', 'city', 'area'], inplace=True)

    # d. 保存回CSV
    final_df.to_csv(CSV_PATH, index=False)
    print(f"数据已成功更新到 {CSV_PATH}")

if __name__ == "__main__":
    scrape_and_update_data()
