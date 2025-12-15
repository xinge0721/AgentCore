"""
API密钥配置管理后端服务
提供Web界面用于管理各种AI模型的API密钥
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 配置文件路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SECRET_KEY_PATH = os.path.join(BASE_DIR, "..", "role", "secret_key.Json")
CONFIG_PATH = os.path.join(BASE_DIR, "..", "role", "config.json")
CHAR_PATH = os.path.join(BASE_DIR, "..", "role", "Char.JSON")

logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"SECRET_KEY_PATH: {SECRET_KEY_PATH}")
logger.info(f"CONFIG_PATH: {CONFIG_PATH}")
logger.info(f"CHAR_PATH: {CHAR_PATH}")
logger.info(f"SECRET_KEY文件是否存在: {os.path.exists(SECRET_KEY_PATH)}")
logger.info(f"CONFIG文件是否存在: {os.path.exists(CONFIG_PATH)}")
logger.info(f"CHAR文件是否存在: {os.path.exists(CHAR_PATH)}")


def load_json_file(file_path):
    """加载JSON配置文件"""
    try:
        logger.info(f"尝试读取文件: {file_path}")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"成功读取文件，数据: {data}")
                return data
        else:
            logger.warning(f"文件不存在: {file_path}")
            return {}
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        return {}


def save_json_file(file_path, data):
    """保存JSON配置文件"""
    try:
        logger.info(f"尝试保存文件: {file_path}")
        logger.info(f"保存数据: {data}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"成功保存文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存文件失败 {file_path}: {e}")
        return False


@app.route('/')
def index():
    """主页"""
    logger.info("访问主页")
    return render_template('index.html')


@app.before_request
def log_request():
    """记录所有请求"""
    logger.info(f"收到请求: {request.method} {request.path}")
    if request.data:
        logger.info(f"请求数据: {request.data.decode('utf-8')}")


@app.route('/api/get_config', methods=['GET'])
def get_config():
    """获取所有配置"""
    logger.info("获取配置请求")
    secret_key_data = load_json_file(SECRET_KEY_PATH)
    
    # 所有配置都从 secret_key.Json 读取
    result = {
        'success': True,
        'data': {
            'secret_key': secret_key_data,
            'config': {}  # 不再使用单独的config文件
        }
    }
    logger.info(f"返回配置数据: {result}")
    return jsonify(result)


@app.route('/api/update_deepseek', methods=['POST'])
def update_deepseek():
    """更新DeepSeek配置"""
    logger.info("收到DeepSeek更新请求")
    data = request.json
    logger.info(f"接收到的数据: {data}")
    
    config = load_json_file(SECRET_KEY_PATH)
    
    config['deepseek'] = {
        'api_key': data.get('api_key', ''),
        'base_url': data.get('base_url', 'https://api.deepseek.com'),
        'model': data.get('model', 'deepseek-chat')
    }
    
    if save_json_file(SECRET_KEY_PATH, config):
        logger.info("DeepSeek配置更新成功")
        return jsonify({'success': True, 'message': 'DeepSeek配置更新成功'})
    logger.error("DeepSeek配置保存失败")
    return jsonify({'success': False, 'message': '保存失败'})


@app.route('/api/update_qwen', methods=['POST'])
def update_qwen():
    """更新Qwen配置"""
    logger.info("收到Qwen更新请求")
    data = request.json
    logger.info(f"接收到的数据: {data}")
    
    config = load_json_file(SECRET_KEY_PATH)
    
    config['qwen'] = {
        'api_key': data.get('api_key', ''),
        'base_url': data.get('base_url', 'https://dashscope.aliyuncs.com/compatible-mode/v1'),
        'model': data.get('model', 'qwen-turbo')
    }
    
    if save_json_file(SECRET_KEY_PATH, config):
        logger.info("Qwen配置更新成功")
        return jsonify({'success': True, 'message': 'Qwen配置更新成功'})
    logger.error("Qwen配置保存失败")
    return jsonify({'success': False, 'message': '保存失败'})


@app.route('/api/update_kimi', methods=['POST'])
def update_kimi():
    """更新Kimi配置"""
    logger.info("收到Kimi更新请求")
    data = request.json
    logger.info(f"接收到的数据: {data}")
    
    config = load_json_file(SECRET_KEY_PATH)
    
    config['kimi'] = {
        'api_key': data.get('api_key', ''),
        'base_url': data.get('base_url', 'https://api.moonshot.cn/v1'),
        'model': data.get('model', 'moonshot-v1-8k'),
        'tier': data.get('tier', 'Free')
    }
    
    if save_json_file(SECRET_KEY_PATH, config):
        logger.info("Kimi配置更新成功")
        return jsonify({'success': True, 'message': 'Kimi配置更新成功'})
    logger.error("Kimi配置保存失败")
    return jsonify({'success': False, 'message': '保存失败'})


@app.route('/api/update_doubao', methods=['POST'])
def update_doubao():
    """更新豆包配置"""
    logger.info("收到豆包更新请求")
    data = request.json
    logger.info(f"接收到的数据: {data}")
    
    config = load_json_file(SECRET_KEY_PATH)
    
    config['doubao'] = {
        'api_key': data.get('api_key', ''),
        'base_url': data.get('base_url', 'https://ark.cn-beijing.volces.com/api/v3'),
        'model': data.get('model', 'ep-xxxxxxxxxxxxxx')
    }
    
    if save_json_file(SECRET_KEY_PATH, config):
        logger.info("豆包配置更新成功")
        return jsonify({'success': True, 'message': '豆包配置更新成功'})
    logger.error("豆包配置保存失败")
    return jsonify({'success': False, 'message': '保存失败'})


@app.route('/api/update_xinhuo', methods=['POST'])
def update_xinhuo():
    """更新讯飞星火配置"""
    logger.info("收到讯飞星火更新请求")
    data = request.json
    logger.info(f"接收到的数据: {data}")
    
    # 讯飞星火配置也写到 secret_key.Json
    config = load_json_file(SECRET_KEY_PATH)
    
    config['xinhuo'] = {
        'appid': data.get('appid', ''),
        'api_secret': data.get('api_secret', ''),
        'api_key': data.get('api_key', ''),
        'domain': data.get('domain', '4.0Ultra'),
        'Spark_url': data.get('Spark_url', 'wss://spark-api.xf-yun.com/v4.0/chat')
    }
    
    if save_json_file(SECRET_KEY_PATH, config):
        logger.info("讯飞星火配置更新成功")
        return jsonify({'success': True, 'message': '讯飞星火配置更新成功'})
    logger.error("讯飞星火配置保存失败")
    return jsonify({'success': False, 'message': '保存失败'})


@app.route('/api/get_prompt', methods=['GET'])
def get_prompt():
    """获取提示词配置"""
    logger.info("获取提示词请求")
    char_data = load_json_file(CHAR_PATH)
    
    result = {
        'success': True,
        'data': char_data
    }
    logger.info(f"返回提示词数据")
    return jsonify(result)


@app.route('/api/update_prompt', methods=['POST'])
def update_prompt():
    """更新提示词配置"""
    logger.info("收到提示词更新请求")
    data = request.json
    logger.info(f"接收到的数据长度: {len(data.get('content', ''))}")
    
    char_config = {
        'role': 'system',
        'content': data.get('content', '')
    }
    
    if save_json_file(CHAR_PATH, char_config):
        logger.info("提示词配置更新成功")
        return jsonify({'success': True, 'message': '提示词配置更新成功'})
    logger.error("提示词配置保存失败")
    return jsonify({'success': False, 'message': '保存失败'})


if __name__ == '__main__':
    # 创建templates目录
    templates_dir = os.path.join(BASE_DIR, 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
        logger.info(f"创建templates目录: {templates_dir}")
    
    logger.info("=" * 60)
    logger.info("API密钥配置管理系统启动")
    logger.info("访问地址: http://localhost:5000")
    logger.info("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

