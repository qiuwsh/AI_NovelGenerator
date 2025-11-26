# ui/llm_settings_tab.py
# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import messagebox
from ui.config_tab import (
    build_ai_config_tab, 
    build_embeddings_config_tab, 
    build_config_choose_tab,
    build_proxy_setting_tab
)

def build_llm_settings_tab(self):
    """
    独立的大模型设置标签页
    """
    self.llm_settings_tab = self.tabview.add("大模型设置")
    self.llm_settings_tab.rowconfigure(0, weight=1)
    self.llm_settings_tab.columnconfigure(0, weight=1)
    
    # 创建配置区域
    self.llm_config_frame = ctk.CTkFrame(self.llm_settings_tab, corner_radius=10, border_width=2, border_color="gray")
    self.llm_config_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    self.llm_config_frame.columnconfigure(0, weight=1)
    
    # 构建LLM配置选项卡
    build_llm_config_tabview(self)

def build_llm_config_tabview(self):
    """
    在大模型设置标签页中创建配置选项卡
    """
    # 使用临时变量指向config_frame
    original_config_frame = getattr(self, 'config_frame', None)
    self.config_frame = self.llm_config_frame
    
    # 创建选项卡视图（复用config_tab.py的逻辑）
    from ui.config_tab import create_label_with_help
    
    self.config_tabview = ctk.CTkTabview(self.config_frame)
    self.config_tabview.grid(row=0, column=0, sticky="we", padx=5, pady=5)
    
    # 添加各个配置子标签
    self.ai_config_tab = self.config_tabview.add("大语言模型设置")
    self.embeddings_config_tab = self.config_tabview.add("向量嵌入设置") 
    self.config_choose_tab = self.config_tabview.add("配置选择")
    self.proxy_setting_tab = self.config_tabview.add("代理设置")
    
    # 构建各个子标签页的内容
    try:
        build_ai_config_tab(self)
        build_embeddings_config_tab(self)
        build_config_choose_tab(self)  # 恢复配置选择功能
        build_proxy_setting_tab(self)
    except AttributeError as e:
        print(f"构建配置选项卡时出错: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"其他错误: {e}")
        import traceback
        traceback.print_exc()
    
    # 恢复原始config_frame
    if original_config_frame is not None:
        self.config_frame = original_config_frame