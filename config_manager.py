# config_manager.py
# -*- coding: utf-8 -*-
import json
import os
import threading
from llm_adapters import create_llm_adapter
from embedding_adapters import create_embedding_adapter


def load_config(config_file: str) -> dict:
    """从指定的 config_file 加载配置，若不存在则创建一个默认配置文件。"""
    
    if not os.path.exists(config_file):
        return create_config(config_file)

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            # 验证配置文件的完整性
            if not isinstance(config, dict):
                raise ValueError("配置文件格式错误")
            return config
    except json.JSONDecodeError as e:
        print(f"配置文件JSON格式错误: {e}")
        return create_config(config_file)
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return {}


# PenBo 增加了创建默认配置文件函数
def create_config(config_file: str) -> dict:
    """创建一个创建默认配置文件。"""
    config = {
    "last_interface_format": "Ollama",
    "last_embedding_interface_format": "Ollama",
    "llm_configs": {
        "本地 Ollama": {
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1",
            "model_name": "gpt-oss:120b",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600,
            "interface_format": "OpenAI"
        },
        "DeepSeek V3": {
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "temperature": 0.7,
            "max_tokens": 8192,
            "timeout": 600,
            "interface_format": "OpenAI"
        }
    },
    "embedding_configs": {
        "Ollama": {
            "api_key": "ollama",
            "base_url": "http://localhost:11434/v1",
            "model_name": "nomic-embed-text:137m-v1.5-fp16",
            "retrieval_k": 4,
            "interface_format": "OpenAI"
        },
        "DeepSeek": {
            "api_key": "",
            "base_url": "https://api.deepseek.com/v1",
            "model_name": "deepseek-chat",
            "retrieval_k": 4,
            "interface_format": "OpenAI"
        }
    },
    "other_params": {
        "topic": "",
        "genre": "",
        "num_chapters": 0,
        "word_number": 0,
        "filepath": "",
        "chapter_num": "120",
        "user_guidance": "",
        "characters_involved": "",
        "key_items": "",
        "scene_location": "",
        "time_constraint": ""
    },
    "choose_configs": {
        "prompt_draft_llm": "本地 Ollama",
        "chapter_outline_llm": "本地 Ollama",
        "architecture_llm": "本地 Ollama",
        "final_chapter_llm": "本地 Ollama",
        "consistency_review_llm": "本地 Ollama"
    },
    "proxy_setting": {
        "proxy_url": "127.0.0.1",
        "proxy_port": "",
        "enabled": False
    },
    "webdav_config": {
        "webdav_url": "",
        "webdav_username": "",
        "webdav_password": ""
    }
}
    save_config(config, config_file)
    return config



def save_config(config_data: dict, config_file: str) -> bool:
    """将 config_data 保存到 config_file 中，返回 True/False 表示是否成功。"""
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        return True
    except:
        return False

def test_llm_config(interface_format, api_key, base_url, model_name, temperature, max_tokens, timeout, log_func, handle_exception_func):
    """测试当前的LLM配置是否可用"""
    def task():
        try:
            log_func("开始测试LLM配置...")
            llm_adapter = create_llm_adapter(
                interface_format=interface_format,
                base_url=base_url,
                model_name=model_name,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            test_prompt = "Please reply 'OK'"
            response = llm_adapter.invoke(test_prompt)
            if response:
                log_func("✅ LLM配置测试成功！")
                log_func(f"测试回复: {response}")
            else:
                log_func("❌ LLM配置测试失败：未获取到响应")
        except Exception as e:
            log_func(f"❌ LLM配置测试出错: {str(e)}")
            handle_exception_func("测试LLM配置时出错")

    threading.Thread(target=task, daemon=True).start()

def test_embedding_config(api_key, base_url, interface_format, model_name, log_func, handle_exception_func):
    """测试当前的Embedding配置是否可用"""
    def task():
        try:
            log_func("开始测试Embedding配置...")
            embedding_adapter = create_embedding_adapter(
                interface_format=interface_format,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name
            )

            test_text = "测试文本"
            embeddings = embedding_adapter.embed_query(test_text)
            if embeddings and len(embeddings) > 0:
                log_func("✅ Embedding配置测试成功！")
                log_func(f"生成的向量维度: {len(embeddings)}")
            else:
                log_func("❌ Embedding配置测试失败：未获取到向量")
        except Exception as e:
            log_func(f"❌ Embedding配置测试出错: {str(e)}")
            handle_exception_func("测试Embedding配置时出错")

    threading.Thread(target=task, daemon=True).start()