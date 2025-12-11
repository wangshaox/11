import requests
from bs4 import BeautifulSoup   
import re
from sqlUtil import MySQLDBUtil

url = "https://avhole.store/zh/censored"  # Replace with your target URL
url_en = "https://avhole.store/censored"
www = "https://avhole.store"
requests.headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
a_href_list = []  
def fetch_list(url):
    response = requests.get(url,headers=requests.headers)
    response.raise_for_status()  # Raise an error for bad responses
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    parent_elements = soup.select('div.v-container div.grid div.v-card')
    print(f"\n匹配到的父容器数量：{len(parent_elements)}")
    # 5. 遍历父容器，提取内部的h5标签文本（核心新增逻辑）
    for idx, parent in enumerate(parent_elements):
        obj = {}
        tags = parent.select("span.v-btn__content")
        if tags:
            yanyuan = []
            for tag in tags:
                yanyuan.append(tag.get_text(strip=True))
            yanyuan_str = ",".join(yanyuan)
            obj["author"] = yanyuan_str
        else:
            obj["author"] = ""
        a_tag = parent.find('a')
        if a_tag:  
            a_href = a_tag.get('href') # 或者 a_href = a_tag['href']
            # a_href = a_tag.get_text(strip=True)  
            obj["href"] = www + a_href
        obj["category"] = "有码"
        obj["category_en"] = "censored"
        a_href_list.append(obj)
    # 6. 返回解析对象和h5文本列表（方便后续复用）
    return a_href_list
#英文版
def fetch_list_en(url):
    response = requests.get(url,headers=requests.headers)
    response.raise_for_status()  # Raise an error for bad responses
    content = response.text
    soup = BeautifulSoup(content, 'lxml')
    parent_elements = soup.select('div.v-container div.grid div.v-card')
    # 5. 遍历父容器，提取内部的h5标签文本（核心新增逻辑）
    for idx, parent in enumerate(parent_elements):
        tags = parent.select("span.v-btn__content")
        if tags:
            yanyuan = []
            for tag in tags:
                yanyuan.append(tag.get_text(strip=True))
            yanyuan_str = ",".join(yanyuan)
            a_href_list[idx]["author_en"] = yanyuan_str
        else:
            a_href_list[idx]["author_en"] = ""
        a_tag = parent.find('a')
        if a_tag:  
            a_href = a_tag.get('href') # 或者 a_href = a_tag['href']
            # a_href = a_tag.get_text(strip=True)  
            a_href_list[idx]["href"] = www + a_href
    # 6. 返回解析对象和h5文本列表（方便后续复用）
    return a_href_list

def fetch_page(urlList):
    for idx,url in enumerate(urlList):
        response = requests.get(url['href'],headers=requests.headers)
        response.raise_for_status()  # Raise an error for bad responses
        content = response.text
        soup = BeautifulSoup(content, 'lxml')
        # 假设 content 变量包含了您的 HTML 字符串
        # soup = BeautifulSoup(content, 'lxml')
        jpg_url = soup.find('meta', property='og:image')['content']
        a_href_list[idx]["thumbnail"] = jpg_url
        title = soup.find('meta', property='og:title')['content']
        a_href_list[idx]["title"] = title
        code = title.split()
        a_href_list[idx]["code"] = code[0]
        # 使用 find() 方法和属性字典来定位特定的 script 标签
        nuxt_data_script = soup.find('script', attrs={
            'id': '__NUXT_DATA__',
            'type': 'application/json',
            'data-nuxt-data': 'nuxt-app'
        })
        # 检查是否找到了标签并且有内容
        if nuxt_data_script and nuxt_data_script.string:
            # 提取标签内的文本内容，并去除首尾空白
            script_content = nuxt_data_script.string.strip()
            # 因为内容是 JSON 格式，您也可以将其解析为 Python 字典或列表
            import json
            data = json.loads(script_content)
            m3u8_pattern = re.compile(r'(https?:\/\/[^\s\n\r]*?\.m3u8)')
            m3u8_list = []
            for data_item in enumerate(data):
                data_str = str(data_item)
                matches = m3u8_pattern.findall(data_str)
                if matches:
                    for match in matches:
                        m3u8_list.append(match)
                        print(match)
            a_href_list[idx]["video_url"] = m3u8_list[0]


def fetch_page_en(urlList):
    for idx,url in enumerate(urlList):
        response = requests.get(url['href'],headers=requests.headers)
        response.raise_for_status()  # Raise an error for bad responses
        content = response.text
        soup = BeautifulSoup(content, 'lxml')
        title = soup.find('meta', property='og:title')['content']
        a_href_list[idx]["title_en"] = title



import datetime

# 数据库配置（请替换为您的实际配置）
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'qazplm123',
    'db': 'video_db',
    'port': 3306
}

# 确保 SQL 语句中 VALUES 后面有 8 个 %s 占位符
insert_sql = """
    INSERT INTO videos        (title,title_en,code, thumbnail, video_url, category, category_en, author,author_en, created_at, updated_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
"""

insert_sql_ignore = """
    INSERT IGNORE INTO videos (title, title_en, code, thumbnail, video_url, category, category_en, author, author_en, created_at, updated_at) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
"""

for i in range(154,2000):
    a_href_list = []  
    print(f"--- 正在处理第 {i} 页 ---")
    if i==1:
        url = "https://avhole.store/zh/censored"
        url_en = "https://avhole.store/censored"
    else:
        url = f"https://avhole.store/zh/censored?page={i}"
        url_en = f"https://avhole.store/censored?page={i}"
    a_href_list =fetch_list(url)
    fetch_page(a_href_list)
    a_href_list =fetch_list_en(url_en)
    fetch_page_en(a_href_list)
    print(a_href_list)
    # 准备批量插入的参数列表 (保持 8 个参数不变)
    params_for_batch = [
        (
            data['title'], 
            data['title_en'], 
            data['code'],
            data['thumbnail'], 
            data['video_url'], 
            data['category'], 
            data['category_en'], 
            data['author'], 
            data['author_en'],
            datetime.datetime.now(), 
            datetime.datetime.now()
        )
        for data in a_href_list
    ]
    # 在您的代码中将 insert_sql 替换为 insert_sql_ignore 即可：
    try:
        with MySQLDBUtil(**DB_CONFIG) as db:
            rows_affected = db.execute_insert_many(insert_sql_ignore, params_for_batch)
            print(f"✅ 批量数据插入成功，总共尝试插入 {len(params_for_batch)} 条，实际影响行数: {rows_affected}")
    # ...
            
            print(f"✅ 批量数据插入成功，总共影响行数: {rows_affected}")

    except Exception as e:
        print(f"❌ 批量操作失败并已回滚: {e}")