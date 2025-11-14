# EPUB格式修复工具 - 使用示例

本文档提供了EPUB格式修复工具的详细使用示例。

## 目录
- [GUI图形界面使用](#gui图形界面使用)
- [命令行界面使用](#命令行界面使用)
- [Python脚本调用](#python脚本调用)
- [常见场景](#常见场景)

## GUI图形界面使用

### 启动GUI

```bash
python main.py
# 或
python gui.py
```

### 操作步骤

1. **选择文件**
   - 单文件: 点击"选择单个文件"按钮
   - 多文件: 点击"选择多个文件"按钮

2. **配置输出选项**
   - 勾选"覆盖原文件"可以直接修改原文件
   - 或者选择输出目录保存修复后的文件

3. **开始处理**
   - 点击"开始处理"按钮
   - 等待进度条完成
   - 查看处理结果

## 命令行界面使用

### 基本命令

```bash
# 查看帮助
python cli.py --help

# 查看版本
python cli.py --version  # (如果实现了的话)
```

### 单文件处理

```bash
# 保存到新文件
python cli.py input.epub -o output.epub

# 覆盖原文件
python cli.py input.epub --overwrite

# 显示详细信息
python cli.py input.epub -o output.epub -v
```

### 批量处理

```bash
# 处理多个文件，保存到指定目录
python cli.py file1.epub file2.epub file3.epub -d ./fixed/

# 使用通配符批量处理
python cli.py *.epub -d ./output/

# 批量覆盖原文件
python cli.py *.epub --overwrite

# 批量处理并显示详细信息
python cli.py book*.epub -d ./fixed/ -v
```

## Python脚本调用

### 基本用法

```python
from epub_fixer import EPUBFixer

# 创建修复器实例
fixer = EPUBFixer()

# 修复单个文件
success = fixer.fix_epub('input.epub', 'output.epub')
if success:
    print("修复成功！")
else:
    print("修复失败！")
```

### 批量处理

```python
from epub_fixer import EPUBFixer
import os

fixer = EPUBFixer()

# 准备文件列表
files = ['book1.epub', 'book2.epub', 'book3.epub']

# 批量处理
result = fixer.batch_fix(files, output_dir='./fixed/')

# 查看结果
print(f"总计: {result['total']}")
print(f"成功: {result['success']}")
print(f"失败: {result['failed']}")

if result['failed_files']:
    print("失败的文件:")
    for f in result['failed_files']:
        print(f"  - {f}")
```

### 监控进度

```python
from epub_fixer import EPUBFixer
import time

fixer = EPUBFixer()

# 在后台线程中处理
import threading

def process_files():
    files = ['book1.epub', 'book2.epub', 'book3.epub']
    fixer.batch_fix(files, output_dir='./fixed/')

thread = threading.Thread(target=process_files)
thread.start()

# 监控进度
while thread.is_alive():
    processed, total, current = fixer.get_progress()
    print(f"进度: {processed}/{total} - 当前: {current}")
    time.sleep(1)

thread.join()
print("处理完成！")
```

## 常见场景

### 场景1: 修复单个机翻EPUB

机翻后的日文小说，文字变成了竖排：

```bash
# 命令行
python cli.py japanese_novel.epub -o fixed_novel.epub -v

# 或使用GUI
python main.py
# 然后选择文件，点击处理
```

### 场景2: 批量修复整个文件夹

下载了一堆机翻EPUB，需要全部修复：

```bash
# 方法1: 使用通配符
python cli.py /path/to/books/*.epub -d /path/to/fixed_books/

# 方法2: 使用Python脚本
python << EOF
from epub_fixer import EPUBFixer
import glob

fixer = EPUBFixer()
files = glob.glob('/path/to/books/*.epub')
result = fixer.batch_fix(files, output_dir='/path/to/fixed_books/')
print(f"处理完成: {result['success']}/{result['total']}")
EOF
```

### 场景3: 仅测试，不覆盖原文件

先修复一个文件测试效果：

```bash
python cli.py test.epub -o test_fixed.epub
# 检查test_fixed.epub，如果满意再批量处理
```

### 场景4: 备份原文件后修复

```bash
# 先备份
mkdir backup
cp *.epub backup/

# 然后修复
python cli.py *.epub --overwrite
```

### 场景5: 在服务器上自动处理

创建一个自动处理脚本 `auto_fix.sh`:

```bash
#!/bin/bash
# auto_fix.sh - 自动监控和修复EPUB文件

WATCH_DIR="/path/to/incoming"
OUTPUT_DIR="/path/to/fixed"

# 使用inotifywait监控新文件（需要安装inotify-tools）
inotifywait -m -e create -e moved_to --format '%f' "$WATCH_DIR" | while read filename
do
    if [[ $filename == *.epub ]]; then
        echo "检测到新文件: $filename"
        python3 cli.py "$WATCH_DIR/$filename" -d "$OUTPUT_DIR" -v
        echo "处理完成: $filename"
    fi
done
```

## 修复效果说明

### 修复前
- 文字竖排显示（从上到下，从右到左）
- 可能使用了错误的字体
- CSS包含 `writing-mode: vertical-rl` 等属性

### 修复后
- 文字横排显示（从左到右，从上到下）
- 使用中文友好的字体
- CSS使用 `writing-mode: horizontal-tb`
- 注入了修复样式确保正确显示

## 技术细节

### 修复的CSS属性

工具会修复以下CSS属性：

- `writing-mode: vertical-rl` → `horizontal-tb`
- `writing-mode: vertical-lr` → `horizontal-tb`
- `writing-mode: tb-rl` → `horizontal-tb`
- `-webkit-writing-mode: vertical-*` (移除)
- `-epub-writing-mode: vertical-*` (移除)
- `text-orientation: upright` (移除)

### 注入的修复样式

```css
body {
    writing-mode: horizontal-tb !important;
    -webkit-writing-mode: horizontal-tb !important;
    -epub-writing-mode: horizontal-tb !important;
    direction: ltr;
}

* {
    text-orientation: mixed !important;
}

body, p, div, span {
    font-family: "Microsoft YaHei", "SimSun", 
                 "PingFang SC", "Noto Sans CJK SC", sans-serif;
}
```

## 故障排除

### 问题: GUI无法启动

**原因**: 缺少tkinter

**解决方案**:
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# 或使用CLI
python cli.py input.epub -o output.epub
```

### 问题: 修复后文件无法打开

**原因**: 原EPUB文件可能已损坏

**解决方案**:
1. 使用EPUB验证工具检查原文件
2. 尝试用不同的EPUB阅读器打开

### 问题: 文字还是竖排

**原因**: EPUB阅读器可能有自己的样式覆盖

**解决方案**:
1. 尝试不同的EPUB阅读器
2. 检查阅读器的设置，禁用"强制使用原始样式"

## 更多帮助

如有问题或建议，请访问项目GitHub页面提交Issue。
