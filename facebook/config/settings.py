import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Apify配置
APIFY_API_TOKEN = os.getenv('APIFY_API_TOKEN', '')

# Facebook群组配置
FACEBOOK_GROUP_URL = os.getenv('FACEBOOK_GROUP_URL', 'https://www.facebook.com/groups/2091834914421201/')
FACEBOOK_GROUP_ID = os.getenv('FACEBOOK_GROUP_ID', '2091834914421201')

# 项目配置
PROJECT_NAME = os.getenv('PROJECT_NAME', 'Smart Home Facebook Scraper')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data')

# 目录配置
RAW_DATA_DIR = os.path.join(DATA_PATH, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_PATH, 'processed')
EXPORTS_DIR = os.path.join(DATA_PATH, 'exports')

# 确保目录存在
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Apify Actor配置
FACEBOOK_GROUPS_SCRAPER_ACTOR_ID = 'apify/facebook-groups-scraper'

# 数据处理配置
MAX_POSTS_PER_FILE = 1000
EXPORT_FORMATS = ['json', 'csv', 'xlsx'] 