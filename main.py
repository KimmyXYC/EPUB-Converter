#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB格式修复工具
主入口文件
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import main

if __name__ == "__main__":
    main()
