# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
import os


class HousingSpiderPipeline:
    def process_item(self, item, spider):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(base_dir, 'data', 'housing_data.csv')
        # 读取旧数据
        try:
            existing_df = pd.read_csv(csv_path)
        except FileNotFoundError:
            existing_df = pd.DataFrame()
        # 新数据
        new_df = pd.DataFrame([dict(item)])
        # 合并
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        # 统一日期格式
        combined_df['date'] = pd.to_datetime(combined_df['date'], format='mixed')
        combined_df['year_month'] = combined_df['date'].dt.to_period('M')
        combined_df.sort_values('date', ascending=False, inplace=True)
        final_df = combined_df.drop_duplicates(subset=['city', 'area', 'year_month'], keep='first')
        final_df['date'] = final_df['date'].dt.strftime('%Y-%m-%d')
        final_df = final_df.drop(columns=['year_month'])
        final_df.sort_values(['date', 'city', 'area'], inplace=True)
        final_df.to_csv(csv_path, index=False)
        return item
