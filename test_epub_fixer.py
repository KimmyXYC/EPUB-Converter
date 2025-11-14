#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试EPUB修复功能
"""

import os
import tempfile
from epub_fixer import EPUBFixer


def test_style_fixing():
    """测试样式修复功能"""
    fixer = EPUBFixer()
    
    # 测试竖排样式修复
    vertical_style = "writing-mode: vertical-rl; font-size: 14px; color: black;"
    fixed_style = fixer._fix_style_attribute(vertical_style)
    assert "horizontal-tb" in fixed_style
    assert "vertical" not in fixed_style
    print("✓ 竖排样式修复测试通过")
    
    # 测试text-orientation移除
    orientation_style = "text-orientation: upright; font-size: 14px;"
    fixed_style = fixer._fix_style_attribute(orientation_style)
    assert "text-orientation" not in fixed_style
    assert "font-size" in fixed_style
    print("✓ text-orientation移除测试通过")
    
    # 测试-webkit-writing-mode移除
    webkit_style = "-webkit-writing-mode: vertical-rl; margin: 10px;"
    fixed_style = fixer._fix_style_attribute(webkit_style)
    assert "-webkit-writing-mode" not in fixed_style
    assert "margin" in fixed_style
    print("✓ webkit样式移除测试通过")


def test_css_fixing():
    """测试CSS修复功能"""
    fixer = EPUBFixer()
    
    # 测试CSS中竖排样式修复
    css_content = """
body {
    writing-mode: vertical-rl;
    font-size: 16px;
}

.vertical {
    writing-mode: tb-rl;
}
"""
    fixed_css = fixer._fix_css_content(css_content.encode('utf-8')).decode('utf-8')
    assert "horizontal-tb" in fixed_css
    assert "vertical-rl" not in fixed_css
    print("✓ CSS竖排样式修复测试通过")


def test_html_fixing():
    """测试HTML修复功能"""
    fixer = EPUBFixer()
    
    # 测试HTML修复
    html_content = """
<html>
<head><title>Test</title></head>
<body style="writing-mode: vertical-rl;">
    <p style="text-orientation: upright;">测试文本</p>
</body>
</html>
"""
    fixed_html = fixer._fix_html_content(html_content.encode('utf-8')).decode('utf-8')
    assert "horizontal-tb" in fixed_html
    assert "epub-fixer-style" in fixed_html
    print("✓ HTML修复测试通过")


def test_fix_css_generation():
    """测试修复CSS生成"""
    fixer = EPUBFixer()
    css = fixer._get_fix_css()
    assert "horizontal-tb" in css
    assert "font-family" in css
    print("✓ 修复CSS生成测试通过")


def test_progress_tracking():
    """测试进度跟踪"""
    fixer = EPUBFixer()
    fixer.total_files = 10
    fixer.processed_files = 5
    fixer.current_file = "test.epub"
    
    progress = fixer.get_progress()
    assert progress[0] == 5
    assert progress[1] == 10
    assert progress[2] == "test.epub"
    print("✓ 进度跟踪测试通过")


def test_page_progression_direction():
    """测试页面翻页方向修复"""
    from ebooklib import epub
    
    fixer = EPUBFixer()
    
    # 模拟一个book对象来测试方向修复
    class MockBook:
        def __init__(self, direction):
            self.direction = direction
    
    # 测试RTL改为LTR
    book_rtl = MockBook('rtl')
    fixer._fix_page_progression_direction(book_rtl)
    assert book_rtl.direction == 'ltr'
    print("✓ RTL改为LTR测试通过")
    
    # 测试LTR保持LTR
    book_ltr = MockBook('ltr')
    fixer._fix_page_progression_direction(book_ltr)
    assert book_ltr.direction == 'ltr'
    print("✓ LTR保持不变测试通过")
    
    # 测试None改为LTR
    book_none = MockBook(None)
    fixer._fix_page_progression_direction(book_none)
    assert book_none.direction == 'ltr'
    print("✓ None改为LTR测试通过")
    
    print("✓ 页面翻页方向修复测试通过")


if __name__ == "__main__":
    print("开始测试EPUB修复功能...")
    print()
    
    try:
        test_style_fixing()
        test_css_fixing()
        test_html_fixing()
        test_fix_css_generation()
        test_progress_tracking()
        test_page_progression_direction()
        
        print()
        print("=" * 50)
        print("所有测试通过！✓")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n测试失败: {str(e)}")
        exit(1)
    except Exception as e:
        print(f"\n测试出错: {str(e)}")
        exit(1)
