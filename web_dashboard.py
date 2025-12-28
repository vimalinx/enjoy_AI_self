#!/usr/bin/env python3
"""
轮回系统 Web 面板
提供可视化管理界面
"""

from flask import Flask, render_template, jsonify, request
from pathlib import Path
import json
import os
from datetime import datetime

# 导入轮回管理器和AI提供商
from reincarnation_manager import ReincarnationManager
from ai_providers import AIProviderFactory, APIKeyManager

app = Flask(__name__)
app.jinja_env.globals['now'] = datetime.now

# 获取工作目录
WORK_DIR = Path(__file__).parent
manager = ReincarnationManager(work_dir=WORK_DIR)
ai_manager = APIKeyManager(work_dir=WORK_DIR)


@app.route('/')
def index():
    """主页"""
    return render_template('dashboard.html')


@app.route('/api/lives')
def api_lives():
    """获取所有生命"""
    lives = manager.list_lives()
    return jsonify({
        'success': True,
        'data': lives
    })


@app.route('/api/lives/<life_name>')
def api_life_detail(life_name):
    """获取生命详情"""
    stats = manager.get_life_stats(life_name)
    if not stats:
        return jsonify({
            'success': False,
            'error': f'生命 {life_name} 不存在'
        }), 404

    return jsonify({
        'success': True,
        'data': stats
    })


@app.route('/api/lives/<life_name>/diary')
def api_life_diary(life_name):
    """获取生命日记"""
    limit = request.args.get('limit', type=int)
    phase = request.args.get('phase')  # 可选：过滤特定阶段

    entries = manager.read_life_diary(life_name, limit=limit)

    # 如果指定了阶段，过滤
    if phase:
        entries = [e for e in entries if e.get('phase') == phase]

    return jsonify({
        'success': True,
        'data': entries,
        'count': len(entries)
    })


@app.route('/api/lives/<life_name>/state')
def api_life_state(life_name):
    """获取生命状态文件"""
    life_path = WORK_DIR / "lives" / life_name
    state_file = life_path / "state.json"

    if not state_file.exists():
        return jsonify({
            'success': False,
            'error': '状态文件不存在'
        }), 404

    try:
        state = json.loads(state_file.read_text(encoding='utf-8'))
        return jsonify({
            'success': True,
            'data': state
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats')
def api_stats():
    """获取轮回统计"""
    stats = manager.get_reincarnation_stats()
    return jsonify({
        'success': True,
        'data': stats
    })


@app.route('/api/compare', methods=['POST'])
def api_compare():
    """对比生命"""
    data = request.get_json()
    lives = data.get('lives', [])

    if not lives or len(lives) < 2:
        return jsonify({
            'success': False,
            'error': '请至少选择两个生命进行对比'
        }), 400

    comparison = manager.compare_lives(lives)
    return jsonify({
        'success': True,
        'data': comparison
    })


@app.route('/api/lives/create', methods=['POST'])
def api_create_life():
    """创建新生命"""
    data = request.get_json()
    name = data.get('name')

    try:
        metadata = manager.create_life(name=name)
        return jsonify({
            'success': True,
            'data': metadata
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/lives/<life_name>/switch', methods=['POST'])
def api_switch_life(life_name):
    """切换生命"""
    try:
        manager.switch_to_life(life_name)
        return jsonify({
            'success': True,
            'message': f'已切换到生命 {life_name}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/lives/<life_name>/metadata')
def api_life_metadata(life_name):
    """获取生命元数据"""
    life_path = WORK_DIR / "lives" / life_name
    metadata_file = life_path / "metadata.json"

    if not metadata_file.exists():
        return jsonify({
            'success': False,
            'error': '元数据文件不存在'
        }), 404

    try:
        metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
        return jsonify({
            'success': True,
            'data': metadata
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/diary/entry')
def api_diary_entry():
    """获取单条日记详情（通过时间戳定位）"""
    life_name = request.args.get('life')
    timestamp = request.args.get('timestamp')

    if not life_name:
        return jsonify({
            'success': False,
            'error': '缺少生命名称'
        }), 400

    entries = manager.read_life_diary(life_name)

    # 查找匹配的条目
    for entry in entries:
        if entry.get('timestamp') == timestamp:
            return jsonify({
                'success': True,
                'data': entry
            })

    return jsonify({
        'success': False,
        'error': '未找到该日记条目'
    }), 404


# AI 配置相关 API
@app.route('/api/ai/providers')
def api_ai_providers():
    """获取所有 AI 提供商"""
    providers = AIProviderFactory.list_providers()
    config = ai_manager.load_config()

    provider_list = []
    for key, name in providers.items():
        provider_config = config.get('providers', {}).get(key, {})
        provider_list.append({
            'key': key,
            'name': name,
            'enabled': provider_config.get('enabled', key == 'claude'),
            'available': _check_provider_available(key, provider_config)
        })

    return jsonify({
        'success': True,
        'data': provider_list
    })


@app.route('/api/ai/config')
def api_ai_config():
    """获取 AI 配置"""
    config = ai_manager.load_config()
    return jsonify({
        'success': True,
        'data': config
    })


@app.route('/api/ai/config', methods=['POST'])
def api_update_ai_config():
    """更新 AI 配置"""
    data = request.get_json()

    try:
        ai_manager.save_config(data)
        return jsonify({
            'success': True,
            'message': '配置已更新'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/ai/provider/<provider_type>/config', methods=['POST'])
def api_update_provider_config(provider_type):
    """更新特定提供商的配置"""
    data = request.get_json()

    try:
        ai_manager.update_provider_config(provider_type, data)
        return jsonify({
            'success': True,
            'message': f'{provider_type} 配置已更新'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/ai/default', methods=['POST'])
def api_set_default_provider():
    """设置默认提供商"""
    data = request.get_json()
    provider_type = data.get('provider')

    if not provider_type:
        return jsonify({
            'success': False,
            'error': '缺少提供商类型'
        }), 400

    try:
        ai_manager.set_default_provider(provider_type)
        return jsonify({
            'success': True,
            'message': f'已设置 {provider_type} 为默认提供商'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/ai/test', methods=['POST'])
def api_test_provider():
    """测试提供商"""
    data = request.get_json()
    provider_type = data.get('provider')

    if not provider_type:
        return jsonify({
            'success': False,
            'error': '缺少提供商类型'
        }), 400

    try:
        provider_config = ai_manager.get_provider_config(provider_type)
        provider = AIProviderFactory.get_provider(
            provider_type,
            api_key=provider_config.get('api_key'),
            config=provider_config
        )

        available = provider.is_available()
        return jsonify({
            'success': True,
            'data': {
                'provider': provider_type,
                'name': provider.get_name(),
                'description': provider.get_description(),
                'available': available
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


def _check_provider_available(provider_type, config):
    """检查提供商是否可用"""
    try:
        provider = AIProviderFactory.get_provider(
            provider_type,
            api_key=config.get('api_key'),
            config=config
        )
        return provider.is_available()
    except:
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="轮回系统 Web 面板")
    parser.add_argument("--host", "-H", default="127.0.0.1", help="监听地址")
    parser.add_argument("--port", "-p", type=int, default=5000, help="监听端口")
    parser.add_argument("--debug", "-d", action="store_true", help="调试模式")

    args = parser.parse_args()

    print("=" * 60)
    print("🌐 轮回系统 Web 面板")
    print("=" * 60)
    print(f"工作目录: {WORK_DIR}")
    print(f"监听地址: http://{args.host}:{args.port}")
    print("=" * 60)
    print()

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
