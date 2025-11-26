# main.py
# -*- coding: utf-8 -*-
import sys
import logging
import traceback
import customtkinter as ctk
from ui import NovelGeneratorGUI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    try:
        # 设置应用外观
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        app = ctk.CTk()
        app.title("AI小说生成器 v2.0")
        app.geometry("1350x840")
        app.minsize(1200, 800)
        
        # 创建GUI
        gui = NovelGeneratorGUI(app)
        
        # 运行主循环
        app.mainloop()
        
    except ImportError as e:
        logging.error(f"导入模块失败: {e}")
        logging.error("请检查是否安装了所有必需的依赖包")
        sys.exit(1)
    except Exception as e:
        logging.error(f"程序启动失败: {e}")
        logging.error(f"详细错误信息: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
