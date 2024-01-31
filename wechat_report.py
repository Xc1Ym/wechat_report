import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import os
import matplotlib.pyplot as plt
import jieba
from wordcloud import WordCloud

# 感谢OpenAI的大力支持，本文件由ChatGPT 4编写，由Xc1Ym进行整理

'''
读取数据
'''

# 获取不包含目录的文件名
# 获取文件的名称
def process_csv(csv_path):
    file_name_with_extension = os.path.basename(csv_path)

    # 分离文件名和扩展名
    file_name, file_extension = os.path.splitext(file_name_with_extension)

    # 移除特定的后缀
    file_name1 = file_name.replace('_utf8', '')


    '''
    数据处理
    '''



    # 获取当前群聊的废话前十

    # print("正在读取数据")

    # 读取CSV文件
    df = pd.read_csv(csv_path)

    # 获取数据总量

    number_of_rows = len(df)
    # print("共读取到" + str(number_of_rows) + "条数据")

    # print("正在处理数据，获取当前群聊废话前十名")

    # 分组统计Sender和NickName对应的数量
    grouped_counts = df.groupby(['Sender', 'NickName']).size().reset_index(name='Counts')
    unique_senders_count = df['Sender'].nunique()
    # print(unique_senders_count)

    # 排序并取前十条记录
    top_senders = grouped_counts.sort_values(by='Counts', ascending=False).head(10)

    # time.sleep(5)

    # 获取赵总发言次数
    # print("已获取当前群聊的废话前十名")

    # 计算包含'<msg><emoji'的行数
    emoji_count = df['StrContent'].str.contains('<msg><emoji', na=False).sum()

    # 计算包含'<img aeskey'的行数
    img_aeskey_count = df['StrContent'].str.contains('<img aeskey', na=False).sum()

    emoji_all = emoji_count + img_aeskey_count

    # 获取所有聊天日期

    # 将StrTime列转换为datetime对象，并且只保留日期部分
    df['Date'] = pd.to_datetime(df['StrTime']).dt.date
    df['StrTime'] = pd.to_datetime(df['StrTime'])

    # 对每个日期进行计数并排序
    date_counts = df['Date'].value_counts().sort_values(ascending=False)
    # print(date_counts)

    # 找到最早和最晚的日期
    earliest_date = df['StrTime'].min()
    latest_date = df['StrTime'].max()

    # 计算差值
    date_difference = latest_date - earliest_date
    # 获取差值的整数天数
    difference_in_days = date_difference.days

    # 输出结果
    # print(f"最早的一天是：{earliest_date}")
    # print(f"最晚的一天是：{latest_date}")
    # print(f"他们的差值是：{date_difference}")

    # 找到数量最多的一天
    most_common_date = date_counts.idxmax()
    most_common_count = date_counts.max()

    # 找到数量最少的一天
    least_common_date = date_counts.idxmin()
    least_common_count = date_counts.min()

    # 输出结果
    # print(f"数量最多的一天是 {most_common_date}，有 {most_common_count} 条记录。")
    # print(f"数量最少的一天是 {least_common_date}，有 {least_common_count} 条记录。")

    # 选择数量前十的日期
    top_dates = date_counts.head(10)

    # 将其余日期的总和计入"Other"
    other_count = date_counts[10:].sum()
    top_dates['Other'] = other_count

    # 绘制饼图
    plt.figure(figsize=(10, 10))
    plt.pie(top_dates, labels=top_dates.index, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')  # 确保饼图是圆形的

    # 保存饼图为图片
    image_path = 'pie_chart.png'
    plt.savefig(image_path)
    plt.close()

    # 排除包含特定字符串的行
    df = df[~df['StrContent'].str.contains(r'<\?xml version="1.0"\?>|<msg><emoji', regex=True, na=False)]

    # 假设您已经有了一个停用词列表文件'stopwords.txt'，每个停用词占一行
    with open('stopwords.txt', 'r', encoding='utf-8') as f:
        stopwords = set([line.strip() for line in f.readlines()])

    # 定义一个函数来分词并过滤停用词
    def tokenize_and_remove_stopwords(text):
        # 首先检查是否为float（即NaN值）
        if isinstance(text, float):
            return []
        words = jieba.cut_for_search(text)
        filtered_words = [word for word in words if word not in stopwords and word.strip() != '']
        return filtered_words

    # 应用到StrContent列
    df['StrContent_tokenized'] = df['StrContent'].astype(str).apply(tokenize_and_remove_stopwords)

    # 将所有分词结果合并为一个长字符串
    all_words = ' '.join([' '.join(tokens) for tokens in df['StrContent_tokenized'] if tokens])

    # 创建词云对象
    wordcloud = WordCloud(width=800, height=400, background_color='white', font_path='C:\\Windows\\Fonts\\simsun.ttc').generate(all_words)

    # 显示词云
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')  # 关闭坐标轴
    # 将词云保存为PNG文件
    plt.savefig('wordcloud.png', format='png')
    plt.close()
    # 查看结果
    # print(df['StrContent_tokenized'].head())

    '''
    输出为PDF
    '''

    # 设置PDF文件名
    filename = file_name1 + '2023年度总结.pdf'
    title = file_name1 + "2023年度总结"
    pdf_path = ".\\report\\" + filename

    # 注册中文字体
    pdfmetrics.registerFont(TTFont('SimSun', 'C:\\Windows\\Fonts\\simsun.ttc'))

    # 创建PDF画布
    c = canvas.Canvas(pdf_path, pagesize=letter)
    c.setTitle(title)

    # 添加大标题
    c.setFont('SimSun', 20)
    c.drawString(20, 750, str(title))

    # 添加数据来源

    c.setFont('SimSun', 12)
    output = "本次数据来自群聊" + str(earliest_date) + "至" + str(latest_date) + "全量聊天记录"
    c.drawString(20, 720, output)
    c.drawString(20, 700, "（包括文本、图片、视频、表情包）。")
    c.drawString(20, 680, "基于上述数据，群内一年内共产生了" + str(number_of_rows) + "条消息，其中表情包" + str(emoji_all) + "条，共有" + str(unique_senders_count) + "名群友在群内发言，")
    c.drawString(20, 660, "本年度前十废话群友分别为：")

    # 添加表头
    c.setFont('SimSun', 12)
    c.drawString(20, 640, '昵称')
    c.drawString(250, 640, '计数')

    # 添加表格数据
    line_height = 620
    for index, row in top_senders.iterrows():
        c.setFont('SimSun', 12)
        c.drawString(20, line_height, str(row['NickName']))
        c.drawString(250, line_height, str(row['Counts']))
        line_height -= 20

    # 统计时间

    c.drawString(300, 640, "本年度群聊共有" + str(difference_in_days + 1) + "天活跃")
    c.drawString(300, 620, "其中最活跃的一天是" + str(most_common_date) + "，有" + str(most_common_count) + "条消息。")
    c.drawString(300, 600, "最不活跃的一天是" + str(least_common_date) + "，有" + str(least_common_count) + "条消息。")

    # 插入聊天时间饼图
    width = 300
    height = 300
    c.drawImage("pie_chart.png", 300, 290, width, height)
    os.remove("pie_chart.png")

    # 插入词云

    c.drawString(20, 260, "通过对群友的聊天记录进行统计、分词，剔除标点、语气词等停用词后，绘制词云如下:")
    c.drawImage("wordcloud.png", 20, 50, 400, 200)
    os.remove("wordcloud.png")

    # 保存PDF文件
    c.save()


# 这个函数递归地遍历所有文件夹，找到所有的.csv文件
def find_csv_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.csv'):
                process_csv(os.path.join(root, file))

# 用你想要搜索的文件夹的路径替换YOUR_FOLDER_PATH
folder_path = '.\data\聊天记录'
find_csv_files(folder_path)
