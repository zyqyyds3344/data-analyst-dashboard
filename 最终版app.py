import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import warnings
import os
from collections import Counter
import base64
from datetime import datetime

warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="数据分析师实习市场洞察看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
def inject_custom_css():
    st.markdown("""
    <style>
        /* 隐藏Streamlit默认元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 主背景色 */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* 侧边栏样式 - 极淡灰蓝背景 */
        .css-1d391kg, .css-1lcbmhc {
            background-color: #f0f4f8 !important;
        }
        
        .stSidebar {
            background-color: #f0f4f8;
        }
        
        /* 侧边栏标题样式 */
        .sidebar-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        /* 筛选器组样式 */
        .filter-group {
            background: white;
            padding: 1.2rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border-left: 4px solid #667eea;
        }
        
        .filter-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 0.8rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        /* 数据量反馈样式 */
        .data-feedback {
            background: #e8f4fd;
            padding: 0.8rem;
            border-radius: 8px;
            margin: 0.8rem 0;
            border-left: 3px solid #3498db;
            font-size: 0.9rem;
            color: #2c3e50;
        }
        
        /* 主标题区域 */
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .hero-title {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 1rem;
        }
        
        .hero-description {
            font-size: 1rem;
            opacity: 0.8;
            max-width: 600px;
        }
        
        /* 自定义指标卡片 */
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 4px solid #3498db;
            text-align: center;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #7f8c8d;
            font-weight: 500;
        }
        
        /* 图表容器 */
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 1.5rem;
        }
        
        /* 标签页样式 */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: transparent;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #f8f9fa;
            border-radius: 10px 10px 0px 0px;
            gap: 1rem;
            padding: 0px 20px;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #667eea;
            color: white;
        }
        
        /* 空状态样式 */
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #7f8c8d;
        }
        
        .empty-state-emoji {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        /* 数据新鲜度样式 */
        .data-freshness {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin-top: 2rem;
        }
        
        .freshness-value {
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .section-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #2c3e50;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #3498db;
        }
    </style>
    """, unsafe_allow_html=True)

# 自定义指标卡片组件
def metric_card(label, value, subtitle=None):
    card_html = f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {f'<div style="font-size: 0.8rem; color: #95a5a6; margin-top: 0.5rem;">{subtitle}</div>' if subtitle else ''}
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# 数据清洗函数
def clean_salary(salary_str):
    """清洗薪资字段，处理各种格式"""
    try:
        if pd.isna(salary_str) or salary_str in ['', 'None', 'nan']:
            return None
        
        salary_str = str(salary_str).strip()
        
        # 处理薪资面议
        if any(keyword in salary_str for keyword in ['面议', '薪资面议']):
            return None
        
        # 提取数字
        numbers = re.findall(r'\d+', salary_str)
        
        if not numbers:
            return None
        
        numbers = [int(num) for num in numbers]
        
        if len(numbers) == 1:
            return numbers[0]
        elif len(numbers) >= 2:
            return (numbers[0] + numbers[1]) / 2
        else:
            return None
            
    except Exception:
        return None

# 城市名称标准化函数
def standardize_city_name(city_name):
    """标准化城市名称，去除末尾的'市'字"""
    if pd.isna(city_name):
        return '未知'
    
    city_str = str(city_name).strip()
    
    # 去除末尾的"市"字
    if city_str.endswith('市'):
        city_str = city_str[:-1]
    
    # 特殊处理
    special_cases = {
        '朝阳': '北京',  # 假设朝阳指的是北京朝阳区
        '海淀': '北京',  # 假设海淀指的是北京海淀区
        '浦东': '上海',  # 假设浦东指的是上海浦东区
        '福田': '深圳',  # 假设福田指的是深圳福田区
    }
    
    return special_cases.get(city_str, city_str)

# 福利标签提取
def extract_benefits(df):
    """从职位描述中提取福利标签"""
    benefit_keywords = {
        '转正机会': ['转正', '留用', '全职机会'],
        '弹性工作': ['弹性工作', '不打卡', '灵活工时'],
        '下午茶': ['下午茶', '茶歇', '零食'],
        '免费三餐': ['包吃', '三餐', '免费餐'],
        '房补': ['房补', '住房补贴', '租房补贴'],
        '交通补贴': ['交通补贴', '车补', '通勤补贴'],
        '健身房': ['健身房', '健身', '运动设施'],
        '年度旅游': ['旅游', '团建', 'outing'],
        '五险一金': ['五险一金', '社保', '公积金']
    }
    
    benefits_data = []
    
    if '职位描述' not in df.columns:
        return benefits_data
    
    for idx, desc in df['职位描述'].dropna().items():
        desc_str = str(desc)
        for benefit, keywords in benefit_keywords.items():
            if any(keyword in desc_str for keyword in keywords):
                benefits_data.append({
                    'index': idx,
                    '福利标签': benefit
                })
    
    return pd.DataFrame(benefits_data)

# 行业分类提取
def extract_industry(company_name):
    """根据公司名称推断行业"""
    industry_mapping = {
        '互联网': ['字节', '阿里', '腾讯', '百度', '美团', '京东', '拼多多', '网易', '快手', '滴滴'],
        '金融': ['银行', '证券', '保险', '基金', '信托', '平安', '招商', '中信'],
        '科技': ['华为', '小米', 'oppo', 'vivo', '联想', '中兴'],
        '电商': ['淘宝', '天猫', '京东', '拼多多', '唯品会'],
        '游戏': ['网易游戏', '腾讯游戏', '完美世界', '盛大', '游族'],
        '教育': ['学而思', '好未来', '新东方', '猿辅导', '作业帮']
    }
    
    if pd.isna(company_name):
        return '其他'
    
    company_str = str(company_name)
    for industry, keywords in industry_mapping.items():
        if any(keyword in company_str for keyword in keywords):
            return industry
    return '其他'

# 幸福感指数计算器
def calculate_happiness_index(city_salary_data):
    """计算各城市的实习幸福感指数"""
    # 扩展的房租估算字典（单位：元/月）
    rent_estimates = {
        # 一线城市
        '北京': 3800, '上海': 3500, '深圳': 3000, '广州': 2500,
        # 新一线城市
        '杭州': 2800, '南京': 2200, '成都': 1800, '武汉': 1800,
        '西安': 1700, '重庆': 1600, '天津': 2000, '苏州': 2000,
        '长沙': 1600, '郑州': 1500, '东莞': 1200, '青岛': 1700,
        '合肥': 1600, '佛山': 1200, '宁波': 1800, '无锡': 1600,
        # 其他热门城市
        '厦门': 2000, '福州': 1500, '济南': 1500, '大连': 1600,
        '哈尔滨': 1300, '沈阳': 1400, '石家庄': 1300, '长春': 1300,
        '昆明': 1400, '南宁': 1300, '贵阳': 1300, '兰州': 1200,
        '太原': 1300, '乌鲁木齐': 1400, '呼和浩特': 1200, '银川': 1200,
        '西宁': 1100, '海口': 1500, '珠海': 1800, '中山': 1200
    }
    
    happiness_data = []
    
    for city, data in city_salary_data.items():
        avg_salary = data['avg_salary']
        avg_days = data['avg_days']
        position_count = data['position_count']
        
        # 获取该城市房租，如果不在字典中则使用默认值
        rent = rent_estimates.get(city, 1500)
        
        # 计算月收入（日薪 × 每周天数 × 4周）
        monthly_income = avg_salary * avg_days * 4
        
        # 幸福感指数 = 月收入 / 房租 × 100（标准化到0-100范围）
        if rent > 0:
            happiness_index = min((monthly_income / rent) * 100, 150)
        else:
            happiness_index = 0
            
        happiness_data.append({
            '城市': city,
            '幸福感指数': round(happiness_index, 1),
            '平均日薪': round(avg_salary, 1),
            '预估房租': rent,
            '预估月收入': round(monthly_income, 1),
            '岗位数量': position_count
        })
    
    return pd.DataFrame(happiness_data)

# 技能需求分析
def analyze_skills(df):
    """分析职位描述中的技能需求"""
    skill_keywords = {
        'SQL': r'\bSQL\b',
        'Python': r'\bPython\b',
        'Excel': r'\bExcel\b',
        'Tableau': r'\bTableau\b',
        'Power BI': r'\bPower\s*BI\b',
        'R语言': r'\bR语言\b|\bR\s*语言\b',
        'SPSS': r'\bSPSS\b',
        'SAS': r'\bSAS\b',
        'Hive': r'\bHive\b',
        'Spark': r'\bSpark\b',
        '机器学习': r'机器学习',
        '数据挖掘': r'数据挖掘',
        '统计分析': r'统计分析',
        '数据可视化': r'数据可视化'
    }
    
    skill_counts = {skill: 0 for skill in skill_keywords.keys()}
    total_positions = len(df)
    
    if '职位描述' not in df.columns:
        return pd.DataFrame(), 0
    
    for desc in df['职位描述'].dropna():
        desc_str = str(desc)
        for skill, pattern in skill_keywords.items():
            if re.search(pattern, desc_str, re.IGNORECASE):
                skill_counts[skill] += 1
    
    skill_data = []
    for skill, count in skill_counts.items():
        if total_positions > 0:
            mention_rate = (count / total_positions) * 100
        else:
            mention_rate = 0
        skill_data.append({
            '技能': skill,
            '提及次数': count,
            '提及率': round(mention_rate, 1)
        })
    
    return pd.DataFrame(skill_data), total_positions

# 空状态组件
def empty_state(emoji="😔", message="暂无数据"):
    st.markdown(f"""
    <div class="empty-state">
        <div class="empty-state-emoji">{emoji}</div>
        <h3>{message}</h3>
        <p>请尝试调整筛选条件</p>
    </div>
    """, unsafe_allow_html=True)

# 加载数据
@st.cache_data
def load_data():
    """加载和预处理数据"""
    try:
        if not os.path.exists('数据分析师岗位数据.csv'):
            # 创建更丰富的示例数据
            sample_data = {
                '职位标题': ['数据分析师实习生', '商业数据分析师', '数据运营实习生', '数据分析师', '数据产品实习生'] * 40,
                '薪资范围': ['150-200/天', '200/天', '180-250/天', '120-180/天', '250/天'] * 40,
                '公司名称': ['字节跳动', '阿里巴巴', '腾讯', '百度', '美团', '京东', '拼多多', '网易', '快手', '滴滴'] * 20,
                '工作地点': ['北京', '上海市', '深圳', '北京市', '上海', '广州市', '成都', '武汉市', '南京', '西安市'] * 20,
                '学历要求': ['本科', '硕士', '本科', '本科', '硕士', '博士', '本科', '硕士', '本科', '硕士'] * 20,
                '每周天数': ['5天/周', '5天/周', '4天/周', '5天/周', '5天/周', '3天/周', '4天/周', '5天/周', '4天/周', '5天/周'] * 20,
                '实习时长': ['3个月', '6个月', '3个月', '4个月', '6个月', '2个月', '3个月', '6个月', '4个月', '5个月'] * 20,
                '职位描述': [
                    '需要熟练掌握SQL和Python，有数据可视化经验者优先，Tableau和Excel是必备技能，提供转正机会和下午茶',
                    '要求掌握Python数据分析，熟悉机器学习算法，有SQL使用经验，弹性工作制，交通补贴',
                    '熟练使用Excel和SQL，了解SPSS统计分析工具，提供房补和年度旅游',
                    '需要Python编程能力，掌握数据挖掘技术，熟悉Hive和Spark，免费三餐',
                    '要求Tableau数据可视化技能，熟悉Power BI，有SQL基础，健身房福利',
                    '数据分析实习生，SQL和Python必备，提供转正机会',
                    '商业分析岗位，需要Excel和统计分析能力，弹性工作',
                    '数据运营，Tableau可视化，下午茶福利',
                    '数据产品实习，Python机器学习，房补提供',
                    '数据分析师，SQL查询优化，五险一金'
                ] * 20
            }
            df = pd.DataFrame(sample_data)
        else:
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv('数据分析师岗位数据.csv', encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    continue
            
            if df is None:
                st.error("❌ 无法读取数据文件")
                return None
                
    except Exception as e:
        st.error(f"❌ 加载数据出错: {str(e)}")
        return None
    
    try:
        # 数据清洗
        if '薪资范围' in df.columns:
            df['薪资数值'] = df['薪资范围'].apply(clean_salary)
        else:
            df['薪资数值'] = None
        
        # 城市清洗 - 关键修复：标准化城市名称
        if '工作地点' in df.columns:
            df['城市'] = df['工作地点'].apply(standardize_city_name)
        else:
            df['城市'] = '未知'
        
        if '学历要求' in df.columns:
            df['学历要求'] = df['学历要求'].fillna('不限')
        else:
            df['学历要求'] = '不限'
        
        if '每周天数' in df.columns:
            df['每周天数数值'] = df['每周天数'].apply(
                lambda x: int(re.findall(r'\d+', str(x))[0]) if re.findall(r'\d+', str(x)) else 5
            )
        else:
            df['每周天数数值'] = 5
        
        # 提取行业信息
        if '公司名称' in df.columns:
            df['行业'] = df['公司名称'].apply(extract_industry)
        else:
            df['行业'] = '其他'
        
        # 提取福利标签
        benefits_df = extract_benefits(df)
        if not benefits_df.empty:
            df = df.merge(benefits_df, left_index=True, right_on='index', how='left')
            df['福利标签'] = df['福利标签'].fillna('无特殊福利')
        else:
            df['福利标签'] = '无特殊福利'
        
        return df
        
    except Exception as e:
        st.error(f"❌ 数据清洗出错: {str(e)}")
        return None

# 主程序
def main():
    # 注入自定义CSS
    inject_custom_css()
    
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">📊 数据分析师实习市场洞察</div>
        <div class="hero-subtitle">基于实习僧平台的深度岗位分析</div>
        <div class="hero-description">
            专业的数据分析师实习市场分析平台，提供薪资洞察、技能需求、城市性价比等多维度分析，
            助力你的实习决策
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 加载数据
    df = load_data()
    
    if df is None:
        st.error("无法加载数据，请检查数据文件")
        return
    
    # 侧边栏 - 控制中心
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><h3>🎛️ 数据控制中心</h3></div>', unsafe_allow_html=True)
        
        # 实时数据反馈
        total_positions = len(df)
        st.markdown(f"""
        <div class="data-feedback">
            <strong>📈 数据概览</strong><br>
            共 <strong>{total_positions}</strong> 个实习岗位
        </div>
        """, unsafe_allow_html=True)
        
        # 城市筛选
        st.markdown('<div class="filter-group">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">📍 城市选择</div>', unsafe_allow_html=True)
        
        cities = sorted([city for city in df['城市'].unique() if city and str(city) != 'nan'])
        city_counts = df['城市'].value_counts()
        
        selected_cities = st.multiselect(
            "选择城市（显示岗位数量）",
            options=cities,
            default=cities[:3],
            format_func=lambda x: f"{x} ({city_counts.get(x, 0)}个岗位)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 学历筛选
        st.markdown('<div class="filter-group">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">🎓 学历要求</div>', unsafe_allow_html=True)
        
        education_options = sorted(df['学历要求'].unique())
        edu_counts = df['学历要求'].value_counts()
        
        selected_education = st.multiselect(
            "学历要求",
            options=education_options,
            default=education_options,
            format_func=lambda x: f"{x} ({edu_counts.get(x, 0)}个岗位)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 行业筛选
        st.markdown('<div class="filter-group">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">🏢 行业领域</div>', unsafe_allow_html=True)
        
        industry_options = sorted(df['行业'].unique())
        industry_counts = df['行业'].value_counts()
        
        selected_industry = st.multiselect(
            "所属行业",
            options=industry_options,
            default=industry_options,
            format_func=lambda x: f"{x} ({industry_counts.get(x, 0)}个岗位)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 薪资筛选
        st.markdown('<div class="filter-group">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">💰 薪资范围</div>', unsafe_allow_html=True)
        
        valid_salaries = [s for s in df['薪资数值'] if s is not None]
        if valid_salaries:
            min_salary = int(min(valid_salaries))
            max_salary = int(max(valid_salaries))
            salary_range = st.slider(
                "日薪范围 (元/天)",
                min_value=min_salary,
                max_value=max_salary,
                value=(min_salary, max_salary)
            )
        else:
            salary_range = (0, 300)
            st.info("使用默认薪资范围")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 福利筛选
        st.markdown('<div class="filter-group">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">🎁 福利待遇</div>', unsafe_allow_html=True)
        
        benefit_options = sorted([b for b in df['福利标签'].unique() if b != '无特殊福利'])
        selected_benefits = st.multiselect(
            "福利标签",
            options=benefit_options,
            default=[]
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 每周天数筛选
        st.markdown('<div class="filter-group">', unsafe_allow_html=True)
        st.markdown('<div class="filter-title">📅 每周天数</div>', unsafe_allow_html=True)
        
        days_options = sorted([day for day in df['每周天数数值'].unique() if day is not None])
        days_counts = df['每周天数数值'].value_counts()
        
        selected_days = st.multiselect(
            "每周工作天数",
            options=days_options,
            default=days_options,
            format_func=lambda x: f"{x}天 ({days_counts.get(x, 0)}个岗位)"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 数据新鲜度
        st.markdown("""
        <div class="data-freshness">
            <div class="freshness-value">🕐 数据新鲜度</div>
            <div>最后更新: {}</div>
            <div style="margin-top: 0.5rem;">
                <div style="background: rgba(255,255,255,0.2); border-radius: 10px; height: 6px;">
                    <div style="background: white; width: 95%; height: 100%; border-radius: 10px;"></div>
                </div>
            </div>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)
    
    # 应用筛选
    filtered_df = df.copy()
    
    if selected_cities:
        filtered_df = filtered_df[filtered_df['城市'].isin(selected_cities)]
    
    if selected_education:
        filtered_df = filtered_df[filtered_df['学历要求'].isin(selected_education)]
    
    if selected_industry:
        filtered_df = filtered_df[filtered_df['行业'].isin(selected_industry)]
    
    if selected_days:
        filtered_df = filtered_df[filtered_df['每周天数数值'].isin(selected_days)]
    
    if selected_benefits:
        filtered_df = filtered_df[filtered_df['福利标签'].isin(selected_benefits)]
    
    if valid_salaries:
        filtered_df = filtered_df[
            (filtered_df['薪资数值'] >= salary_range[0]) & 
            (filtered_df['薪资数值'] <= salary_range[1])
        ]
    
    # 标签页布局
    tab1, tab2, tab3 = st.tabs(["🏙️ 市场全景", "💰 薪资与回报", "🛠️ 技能风向标"])
    
    with tab1:
        # 核心指标
        st.markdown('<div class="section-title">📈 核心指标</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_positions_filtered = len(filtered_df)
            metric_card("岗位总数", f"{total_positions_filtered}", "筛选后的岗位数量")
        
        with col2:
            avg_salary = filtered_df['薪资数值'].mean()
            metric_card("平均日薪", f"¥{avg_salary:.1f}" if not pd.isna(avg_salary) else "暂无", "元/天")
        
        with col3:
            unique_companies = filtered_df['公司名称'].nunique() if '公司名称' in filtered_df.columns else 0
            metric_card("公司数量", f"{unique_companies}", "招聘企业数量")
        
        with col4:
            if not filtered_df.empty and '公司名称' in filtered_df.columns:
                company_counts = filtered_df['公司名称'].value_counts()
                if not company_counts.empty:
                    top_company = company_counts.index[0]
                    metric_card("热门公司", top_company, "招聘岗位最多")
                else:
                    metric_card("热门公司", "暂无", "无数据")
            else:
                metric_card("热门公司", "暂无", "无数据")
        
        # 树状图展示城市-行业分布
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🌳 城市-行业分布树状图")
        
        if not filtered_df.empty:
            city_industry_counts = filtered_df.groupby(['城市', '行业']).size().reset_index(name='岗位数量')
            
            fig_treemap = px.treemap(
                city_industry_counts,
                path=['城市', '行业'],
                values='岗位数量',
                color='岗位数量',
                color_continuous_scale='Purples',
                title=""
            )
            fig_treemap.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_treemap, use_container_width=True)
        else:
            empty_state("🌳", "暂无分布数据")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 热门城市和行业分布
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🏙️ 热门城市分布")
            
            if not filtered_df.empty:
                city_counts = filtered_df['城市'].value_counts().head(10)
                fig_city = px.bar(
                    x=city_counts.values,
                    y=city_counts.index,
                    orientation='h',
                    title="",
                    labels={'x': '岗位数量', 'y': '城市'},
                    color=city_counts.values,
                    color_continuous_scale='Blues'
                )
                fig_city.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_city, use_container_width=True)
            else:
                empty_state("🏙️", "暂无城市数据")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🏢 行业分布")
            
            if not filtered_df.empty:
                industry_counts = filtered_df['行业'].value_counts()
                fig_industry = px.pie(
                    values=industry_counts.values,
                    names=industry_counts.index,
                    title="",
                    color_discrete_sequence=px.colors.sequential.Purples
                )
                st.plotly_chart(fig_industry, use_container_width=True)
            else:
                empty_state("🏢", "暂无行业数据")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # 幸福感指数分析
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("😊 实习幸福感指数排行榜")
        st.markdown("**算法说明**: 幸福感指数 = (平均日薪 × 每周天数 × 4周) / 当地预估房租 × 100")
        
        if not filtered_df.empty:
            # 计算各城市平均薪资和天数
            city_stats = {}
            for city in filtered_df['城市'].unique():
                city_data = filtered_df[filtered_df['城市'] == city]
                valid_salaries = city_data['薪资数值'].dropna()
                valid_days = city_data['每周天数数值'].dropna()
                
                if len(valid_salaries) > 0 and len(valid_days) > 0:
                    city_stats[city] = {
                        'avg_salary': valid_salaries.mean(),
                        'avg_days': valid_days.mean(),
                        'position_count': len(city_data)
                    }
            
            if city_stats:
                happiness_df = calculate_happiness_index(city_stats)
                # 修复：默认展示岗位数量最多的Top 10城市
                happiness_df = happiness_df.nlargest(10, '岗位数量').sort_values('幸福感指数', ascending=False)
                
                fig_happiness = px.bar(
                    happiness_df,
                    x='幸福感指数',
                    y='城市',
                    orientation='h',
                    title="",
                    labels={'幸福感指数': '幸福感指数', '城市': '城市'},
                    color='幸福感指数',
                    color_continuous_scale='RdYlGn',
                    hover_data=['平均日薪', '预估月收入', '预估房租', '岗位数量']
                )
                fig_happiness.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_happiness, use_container_width=True)
                
                # 显示详细数据
                with st.expander("📊 查看详细数据"):
                    display_df = happiness_df[['城市', '幸福感指数', '平均日薪', '预估月收入', '预估房租', '岗位数量']]
                    st.dataframe(display_df, use_container_width=True)
            else:
                empty_state("📊", "暂无足够数据计算幸福感指数")
        else:
            empty_state("😔", "暂无数据")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 薪资分析
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("💰 薪资分布分析")
            
            salary_data = filtered_df[filtered_df['薪资数值'].notna()]
            if not salary_data.empty:
                fig_salary = px.histogram(
                    salary_data, 
                    x='薪资数值',
                    nbins=15,
                    title="",
                    labels={'薪资数值': '日薪 (元/天)'},
                    color_discrete_sequence=['#667eea']
                )
                fig_salary.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_salary, use_container_width=True)
            else:
                empty_state("💰", "暂无薪资数据")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.subheader("🎓 学历与薪资关系")
            
            salary_edu_data = filtered_df[filtered_df['薪资数值'].notna()]
            if not salary_edu_data.empty and '学历要求' in salary_edu_data.columns:
                fig_box = px.box(
                    salary_edu_data,
                    x='学历要求',
                    y='薪资数值',
                    title="",
                    labels={'薪资数值': '日薪 (元/天)', '学历要求': '学历'},
                    color='学历要求',
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_box.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                )
                st.plotly_chart(fig_box, use_container_width=True)
            else:
                empty_state("🎓", "暂无学历薪资数据")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        # 技能需求分析
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🛠️ 技能需求热度图")
        
        skill_df, total_positions = analyze_skills(filtered_df)
        
        if not skill_df.empty and total_positions > 0:
            # 筛选出提及率大于0的技能
            skill_df = skill_df[skill_df['提及率'] > 0].sort_values('提及率', ascending=True)
            
            fig_skills = px.bar(
                skill_df,
                x='提及率',
                y='技能',
                orientation='h',
                title="",
                labels={'提及率': '提及率 (%)', '技能': '技能'},
                color='提及率',
                color_continuous_scale='Purples'
            )
            fig_skills.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
            )
            st.plotly_chart(fig_skills, use_container_width=True)
            
            # 技能统计指标
            col1, col2, col3 = st.columns(3)
            with col1:
                top_skill = skill_df.iloc[-1] if len(skill_df) > 0 else None
                if top_skill is not None:
                    st.metric("🔥 最热门技能", top_skill['技能'], f"{top_skill['提及率']}%")
            
            with col2:
                avg_mention_rate = skill_df['提及率'].mean() if len(skill_df) > 0 else 0
                st.metric("📊 平均提及率", f"{avg_mention_rate:.1f}%")
            
            with col3:
                total_mentions = skill_df['提及次数'].sum()
                st.metric("💬 总提及次数", f"{total_mentions}")
                
        else:
            empty_state("🛠️", "暂无技能分析数据")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 技能词云模拟（使用条形图模拟）
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("☁️ 技能词云分布")
        
        if not skill_df.empty:
            # 使用条形图模拟词云效果
            fig_wordcloud = px.bar(
                skill_df.nlargest(10, '提及率'),
                x='提及率',
                y='技能',
                orientation='h',
                title="",
                labels={'提及率': '热度', '技能': '技能'},
                color='提及率',
                color_continuous_scale='Viridis'
            )
            fig_wordcloud.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            st.plotly_chart(fig_wordcloud, use_container_width=True)
        else:
            empty_state("☁️", "暂无技能数据")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 超级表格 - 岗位明细
    st.markdown('<div class="section-title">📋 岗位明细表</div>', unsafe_allow_html=True)
    
    if not filtered_df.empty:
        display_cols = ['职位标题', '公司名称', '城市', '行业', '薪资范围', '学历要求', '每周天数', '实习时长', '福利标签']
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        
        if available_cols:
            display_df = filtered_df[available_cols].copy()
            display_df.reset_index(drop=True, inplace=True)
            display_df.index = display_df.index + 1
            
            # 配置列显示
            column_config = {
                '职位标题': st.column_config.TextColumn(
                    '职位名称',
                    width='large'
                ),
                '公司名称': st.column_config.TextColumn(
                    '公司',
                    width='medium'
                ),
                '城市': st.column_config.TextColumn(
                    '城市',
                    width='small'
                ),
                '行业': st.column_config.TextColumn(
                    '行业',
                    width='small'
                ),
                '薪资范围': st.column_config.ProgressColumn(
                    '薪资',
                    width='medium',
                    min_value=0,
                    max_value=300,
                    format="%f元/天"
                ),
                '学历要求': st.column_config.TextColumn(
                    '学历',
                    width='small'
                ),
                '每周天数': st.column_config.TextColumn(
                    '天数',
                    width='small'
                ),
                '实习时长': st.column_config.TextColumn(
                    '时长',
                    width='small'
                ),
                '福利标签': st.column_config.TextColumn(
                    '福利',
                    width='medium'
                )
            }
            
            st.dataframe(
                display_df,
                use_container_width=True,
                height=400,
                column_config=column_config
            )
        else:
            empty_state("📋", "没有可显示的列")
    else:
        empty_state("📋", "暂无岗位数据")
    
    # 页脚
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #7f8c8d; font-size: 0.9rem;'>"
        "数据分析师实习市场洞察看板 | 基于实习数据 | 史诗级重构版 | 设计于2024"
        "</div>", 
        unsafe_allow_html=True
    )

# 运行程序
if __name__ == "__main__":
    main()
