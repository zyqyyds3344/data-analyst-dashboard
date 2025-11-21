import streamlit as st
import pandas as pd
import plotly.express as px
import re
import warnings
import os
warnings.filterwarnings('ignore')

# 设置页面配置
st.set_page_config(
    page_title="数据分析师实习市场洞察看板",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 应用标题
st.title("📊 数据分析师实习市场洞察看板")
st.markdown("基于实习僧平台的实习岗位数据分析")
st.markdown("---")

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

# 加载数据
@st.cache_data
def load_data():
    """加载和预处理数据"""
    try:
        # 先检查文件是否存在
        if not os.path.exists('数据分析师岗位数据.csv'):
            st.error("❌ 未找到数据文件 '数据分析师岗位数据.csv'")
            st.info("当前目录文件: " + str(os.listdir('.')))
            return None
            
        # 尝试不同编码读取文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv('数据分析师岗位数据.csv', encoding=encoding)
                st.success(f"✅ 数据加载成功 (编码: {encoding})")
                break
            except UnicodeDecodeError:
                continue
            except Exception as e:
                st.error(f"❌ 读取文件出错 ({encoding}): {str(e)}")
                continue
        
        if df is None:
            st.error("❌ 无法用任何编码读取文件")
            return None
            
        # 显示数据基本信息
        st.info(f"数据形状: {df.shape}, 列名: {list(df.columns)}")
        
    except Exception as e:
        st.error(f"❌ 加载数据出错: {str(e)}")
        return None
    
    try:
        # 数据清洗
        # 检查必要的列是否存在
        required_columns = ['薪资范围', '工作地点', '学历要求', '每周天数']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.warning(f"⚠️ 缺少以下列: {missing_columns}")
            st.info(f"可用列: {list(df.columns)}")
        
        # 薪资清洗
        if '薪资范围' in df.columns:
            df['薪资数值'] = df['薪资范围'].apply(clean_salary)
        else:
            df['薪资数值'] = None
            st.warning("⚠️ 无薪资范围列，薪资分析将不可用")
        
        # 城市清洗
        if '工作地点' in df.columns:
            df['城市'] = df['工作地点'].apply(
                lambda x: str(x).split('/')[0] if '/' in str(x) else str(x)
            )
        else:
            df['城市'] = '未知'
            st.warning("⚠️ 无工作地点列，城市分析将受限")
        
        # 学历要求
        if '学历要求' in df.columns:
            df['学历要求'] = df['学历要求'].fillna('不限')
        else:
            df['学历要求'] = '不限'
            st.warning("⚠️ 无学历要求列")
        
        # 每周天数
        if '每周天数' in df.columns:
            df['每周天数数值'] = df['每周天数'].apply(
                lambda x: int(re.findall(r'\d+', str(x))[0]) if re.findall(r'\d+', str(x)) else 5
            )
        else:
            df['每周天数数值'] = 5
            st.warning("⚠️ 无每周天数列")
        
        st.success("✅ 数据清洗完成")
        return df
        
    except Exception as e:
        st.error(f"❌ 数据清洗出错: {str(e)}")
        return None

# 创建示例数据（如果文件不存在或读取失败）
def create_sample_data():
    """创建示例数据用于演示"""
    sample_data = {
        '职位标题': ['数据分析师实习生', '商业数据分析师', '数据运营实习生', '数据分析师', '数据产品实习生'],
        '薪资范围': ['150-200/天', '200/天', '180-250/天', '120-180/天', '250/天'],
        '公司名称': ['字节跳动', '阿里巴巴', '腾讯', '百度', '美团'],
        '工作地点': ['北京', '杭州', '深圳', '北京', '北京'],
        '学历要求': ['本科', '硕士', '本科', '本科', '硕士'],
        '每周天数': ['5天/周', '5天/周', '4天/周', '5天/周', '5天/周'],
        '实习时长': ['3个月', '6个月', '3个月', '4个月', '6个月'],
        '福利待遇': ['免费三餐', '周末双休', '弹性工作', '地铁周边', '免费班车']
    }
    return pd.DataFrame(sample_data)

# 主程序
def main():
    # 加载数据
    df = load_data()
    
    if df is None or df.empty:
        st.warning("⚠️ 使用示例数据进行演示")
        df = create_sample_data()
        df['薪资数值'] = df['薪资范围'].apply(clean_salary)
        df['城市'] = df['工作地点']
        df['每周天数数值'] = df['每周天数'].apply(
            lambda x: int(re.findall(r'\d+', str(x))[0]) if re.findall(r'\d+', str(x)) else 5
        )
    
    # 侧边栏筛选器
    st.sidebar.header("🔍 筛选条件")
    
    # 城市筛选
    cities = sorted([city for city in df['城市'].unique() if city and str(city) != 'nan'])
    selected_cities = st.sidebar.multiselect(
        "选择城市",
        options=cities,
        default=cities[:3] if len(cities) > 3 else cities  # 默认选择前3个城市
    )
    
    # 学历筛选
    education_options = sorted(df['学历要求'].unique())
    selected_education = st.sidebar.multiselect(
        "学历要求",
        options=education_options,
        default=education_options
    )
    
    # 每周天数筛选
    days_options = sorted([day for day in df['每周天数数值'].unique() if day is not None])
    selected_days = st.sidebar.multiselect(
        "每周天数",
        options=days_options,
        default=days_options
    )
    
    # 薪资范围筛选
    valid_salaries = [s for s in df['薪资数值'] if s is not None]
    if valid_salaries:
        min_salary = int(min(valid_salaries))
        max_salary = int(max(valid_salaries))
        salary_range = st.sidebar.slider(
            "日薪范围 (元/天)",
            min_value=min_salary,
            max_value=max_salary,
            value=(min_salary, max_salary)
        )
    else:
        salary_range = (0, 300)
        st.sidebar.info("⚠️ 使用默认薪资范围")
    
    # 应用筛选
    filtered_df = df.copy()
    
    if selected_cities:
        filtered_df = filtered_df[filtered_df['城市'].isin(selected_cities)]
    
    if selected_education:
        filtered_df = filtered_df[filtered_df['学历要求'].isin(selected_education)]
    
    if selected_days:
        filtered_df = filtered_df[filtered_df['每周天数数值'].isin(selected_days)]
    
    # 薪资筛选（仅当有薪资数据时）
    if valid_salaries:
        filtered_df = filtered_df[
            (filtered_df['薪资数值'] >= salary_range[0]) & 
            (filtered_df['薪资数值'] <= salary_range[1])
        ]
    
    # 核心指标
    st.header("📈 核心指标")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_positions = len(filtered_df)
        st.metric("岗位总数", f"{total_positions} 个")
    
    with col2:
        avg_salary = filtered_df['薪资数值'].mean()
        st.metric("平均日薪", f"¥{avg_salary:.1f}" if not pd.isna(avg_salary) else "暂无")
    
    with col3:
        unique_companies = filtered_df['公司名称'].nunique() if '公司名称' in filtered_df.columns else 0
        st.metric("公司数量", f"{unique_companies} 家")
    
    with col4:
        if not filtered_df.empty and '公司名称' in filtered_df.columns:
            company_counts = filtered_df['公司名称'].value_counts()
            if not company_counts.empty:
                top_company = company_counts.index[0]
                st.metric("热门公司", top_company)
            else:
                st.metric("热门公司", "暂无")
        else:
            st.metric("热门公司", "暂无")
    
    st.markdown("---")
    
    # 可视化图表
    if not filtered_df.empty:
        st.header("📊 数据可视化")
        
        # 第一行图表
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 薪资分布")
            salary_data = filtered_df[filtered_df['薪资数值'].notna()]
            if not salary_data.empty:
                fig_salary = px.histogram(
                    salary_data, 
                    x='薪资数值',
                    nbins=15,
                    title="实习日薪分布",
                    labels={'薪资数值': '日薪 (元/天)'}
                )
                st.plotly_chart(fig_salary, use_container_width=True)
            else:
                st.info("暂无薪资数据")
        
        with col2:
            st.subheader("🏙️ 热门城市")
            city_counts = filtered_df['城市'].value_counts().head(10)
            if not city_counts.empty:
                fig_city = px.bar(
                    x=city_counts.values,
                    y=city_counts.index,
                    orientation='h',
                    title="岗位数量TOP10城市",
                    labels={'x': '岗位数量', 'y': '城市'}
                )
                st.plotly_chart(fig_city, use_container_width=True)
            else:
                st.info("暂无城市数据")
        
        # 第二行图表
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("🎓 学历分布")
            edu_counts = filtered_df['学历要求'].value_counts()
            if not edu_counts.empty:
                fig_edu = px.pie(
                    values=edu_counts.values,
                    names=edu_counts.index,
                    title="学历要求分布"
                )
                st.plotly_chart(fig_edu, use_container_width=True)
            else:
                st.info("暂无学历数据")
        
        with col4:
            st.subheader("📅 实习时长")
            if '实习时长' in filtered_df.columns:
                duration_counts = filtered_df['实习时长'].value_counts().head(8)
                if not duration_counts.empty:
                    fig_duration = px.bar(
                        x=duration_counts.index,
                        y=duration_counts.values,
                        title="实习时长分布",
                        labels={'x': '实习时长', 'y': '岗位数量'}
                    )
                    st.plotly_chart(fig_duration, use_container_width=True)
                else:
                    st.info("暂无实习时长数据")
            else:
                st.info("无实习时长字段")
        
        # 数据表格
        st.header("📋 岗位详情")
        display_cols = ['职位标题', '公司名称', '城市', '薪资范围', '学历要求', '每周天数', '实习时长']
        available_cols = [col for col in display_cols if col in filtered_df.columns]
        
        if available_cols:
            display_df = filtered_df[available_cols].copy()
            display_df.reset_index(drop=True, inplace=True)
            display_df.index = display_df.index + 1
            
            st.dataframe(display_df, use_container_width=True, height=400)
        else:
            st.warning("没有可显示的列")
        
    else:
        st.warning("没有找到符合筛选条件的岗位")

# 运行程序
if __name__ == "__main__":
    main()
    
    st.markdown("---")
    st.markdown("数据分析师实习市场洞察看板 | 基于实习数据")