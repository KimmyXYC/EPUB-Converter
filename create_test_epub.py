#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用的EPUB文件（包含竖排文字问题）
"""

from ebooklib import epub


def create_test_epub():
    """创建一个包含竖排文字问题的测试EPUB文件"""
    
    book = epub.EpubBook()
    
    # 设置元数据
    book.set_identifier('test-vertical-text-001')
    book.set_title('测试EPUB - 竖排文字')
    book.set_language('zh')
    book.add_author('测试作者')
    
    # 创建CSS样式（包含竖排问题）
    vertical_css = '''
body {
    writing-mode: vertical-rl;
    -webkit-writing-mode: vertical-rl;
    -epub-writing-mode: vertical-rl;
    text-orientation: upright;
}

p {
    font-size: 16px;
    line-height: 1.8;
}

.vertical-text {
    writing-mode: tb-rl;
}
'''
    
    css = epub.EpubItem(
        uid="style",
        file_name="style/style.css",
        media_type="text/css",
        content=vertical_css
    )
    book.add_item(css)
    
    # 创建章节内容（包含竖排样式）
    chapter1_content = '''
<html>
<head>
    <title>第一章</title>
    <link href="../style/style.css" rel="stylesheet" type="text/css"/>
</head>
<body style="writing-mode: vertical-rl;">
    <h1>第一章：问题演示</h1>
    <p style="text-orientation: upright;">这是一段测试文字。在机翻日文EPUB后，经常会出现文字竖排的问题。</p>
    <p class="vertical-text">这段文字使用了竖排样式类。</p>
    <p>本工具可以自动将这些竖排文字修正为横排，以便正常阅读。</p>
</body>
</html>
'''
    
    chapter1 = epub.EpubHtml(
        title='第一章',
        file_name='chapter1.xhtml',
        lang='zh',
        content=chapter1_content,
        uid='chapter1'
    )
    book.add_item(chapter1)
    
    # 创建第二章
    chapter2_content = '''
<html>
<head>
    <title>第二章</title>
    <link href="../style/style.css" rel="stylesheet" type="text/css"/>
</head>
<body>
    <h1>第二章：更多示例</h1>
    <p style="writing-mode: tb-rl; -webkit-writing-mode: vertical-rl;">
        这段文字混合了多种竖排样式属性。
    </p>
    <p>修复工具会自动识别并修正这些问题，确保文字以正确的横排方式显示。</p>
</body>
</html>
'''
    
    chapter2 = epub.EpubHtml(
        title='第二章',
        file_name='chapter2.xhtml',
        lang='zh',
        content=chapter2_content,
        uid='chapter2'
    )
    book.add_item(chapter2)
    
    # 定义目录
    book.toc = (
        chapter1,
        chapter2
    )
    
    # 添加导航文件
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # 定义spine
    book.spine = ['nav', chapter1, chapter2]
    
    # 保存EPUB
    output_path = '/tmp/test_vertical_text.epub'
    epub.write_epub(output_path, book)
    print(f"测试EPUB文件已创建: {output_path}")
    
    return output_path


if __name__ == "__main__":
    create_test_epub()
