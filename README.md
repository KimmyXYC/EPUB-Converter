# EPUB格式修复工具

一个用于修复机翻后EPUB文件格式问题的Python工具，特别针对日文等语言翻译成中文后出现的文字排版方向和字体问题。

## 功能特性

- ✅ 自动修复EPUB文件中的文字排版方向问题（竖排改为横排）
- ✅ 修复字体显示问题，确保中文字体正确显示
- ✅ 支持单文件处理
- ✅ 支持批量文件处理
- ✅ 提供友好的图形用户界面（GUI）
- ✅ 可选择覆盖原文件或保存到新位置

## 安装

### 前置要求

- Python 3.7 或更高版本

### 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 图形界面模式（推荐）

1. 运行主程序：

```bash
python main.py
```

或者直接运行GUI：

```bash
python gui.py
```

2. 在图形界面中：
   - 点击"选择单个文件"按钮选择一个EPUB文件，或点击"选择多个文件"选择多个文件
   - 选择是否覆盖原文件，或选择输出目录
   - 点击"开始处理"按钮开始修复
   - 等待处理完成，查看结果

### 命令行模式

如果需要在命令行中使用，可以编写脚本调用`epub_fixer.py`模块：

```python
from epub_fixer import EPUBFixer

fixer = EPUBFixer()

# 修复单个文件
fixer.fix_epub('input.epub', 'output.epub')

# 批量修复
fixer.batch_fix(['file1.epub', 'file2.epub'], output_dir='./fixed/')
```

## 修复内容

本工具会自动进行以下修复：

1. **文字排版方向修复**
   - 将竖排文字（vertical-rl, vertical-lr）改为横排（horizontal-tb）
   - 移除或修复CSS中的writing-mode属性
   - 修复HTML中的style属性

2. **字体问题修复**
   - 添加适合中文显示的字体族
   - 确保文字正确显示

3. **样式优化**
   - 注入修复样式到每个HTML文档
   - 修复CSS样式表
   - 保持原有的其他样式不变

## 项目结构

```
EPUB-Converter/
├── main.py           # 主入口文件
├── gui.py            # GUI界面
├── epub_fixer.py     # 核心修复逻辑
├── requirements.txt  # Python依赖
├── README.md         # 说明文档
└── LICENSE          # MIT许可证
```

## 技术栈

- **Python 3.12** - 主要编程语言
- **tkinter** - GUI界面
- **ebooklib** - EPUB文件处理
- **BeautifulSoup4** - HTML解析和修改
- **lxml** - XML/HTML解析引擎

## 常见问题

### Q: 处理后的EPUB文件无法打开？
A: 请确保输入的文件是有效的EPUB文件。如果问题仍然存在，请尝试使用专业的EPUB验证工具检查原文件。

### Q: 修复后字体显示还是有问题？
A: 某些阅读器可能有自己的字体设置。请在阅读器中检查字体设置，或尝试不同的EPUB阅读器。

### Q: 可以处理加密的EPUB文件吗？
A: 不可以。本工具只能处理未加密的标准EPUB文件。

### Q: 批量处理时某些文件失败？
A: 工具会跳过处理失败的文件并继续处理其他文件。完成后会显示失败的文件列表。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交问题报告和拉取请求！

## 作者

KimmyXYC

## 更新日志

### v1.0.0 (2025-11-14)
- 初始版本发布
- 实现基本的EPUB格式修复功能
- 提供GUI界面
- 支持单文件和批量处理
