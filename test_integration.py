#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试：测试完整的EPUB修复流程
"""

import os
import sys
from create_test_epub import create_test_epub
from epub_fixer import EPUBFixer
from ebooklib import epub
from bs4 import BeautifulSoup


def test_full_workflow():
    """测试完整的EPUB修复工作流程"""
    print("=" * 60)
    print("开始集成测试：完整EPUB修复流程")
    print("=" * 60)
    print()
    
    # 步骤1：创建测试EPUB文件
    print("步骤1: 创建包含竖排问题的测试EPUB文件...")
    input_path = create_test_epub()
    print(f"✓ 测试文件已创建: {input_path}")
    print()
    
    # 步骤2：检查原始文件内容
    print("步骤2: 检查原始文件内容...")
    book_original = epub.read_epub(input_path)
    
    has_vertical = False
    for item in book_original.get_items():
        if item.get_type() == 9:  # HTML文档
            content = item.get_content().decode('utf-8')
            if 'vertical' in content.lower():
                has_vertical = True
                print(f"✓ 在 {item.get_name()} 中发现竖排样式")
    
    if not has_vertical:
        print("✗ 错误：测试文件中没有找到竖排样式")
        return False
    print()
    
    # 步骤3：使用修复工具修复EPUB
    print("步骤3: 使用修复工具修复EPUB...")
    output_path = '/tmp/test_vertical_text_fixed.epub'
    fixer = EPUBFixer()
    success = fixer.fix_epub(input_path, output_path)
    
    if not success:
        print("✗ 修复失败")
        return False
    print(f"✓ 修复完成，输出文件: {output_path}")
    print()
    
    # 步骤4：验证修复后的文件
    print("步骤4: 验证修复后的文件...")
    
    # 直接从ZIP文件读取以获取实际修复后的内容
    import zipfile
    
    still_has_vertical = False
    has_horizontal = False
    has_fix_style = False
    
    with zipfile.ZipFile(output_path, 'r') as zip_file:
        # 检查HTML文件
        for name in zip_file.namelist():
            if name.endswith('.xhtml') or name.endswith('.html'):
                with zip_file.open(name) as f:
                    content = f.read().decode('utf-8')
                    
                    # 检查是否还有竖排样式（在非注释中）
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # 检查body的style
                    body = soup.find('body')
                    if body and body.get('style'):
                        style = body.get('style', '')
                        if 'vertical' in style.lower() and 'horizontal' not in style.lower():
                            still_has_vertical = True
                            print(f"✗ {name} 中仍有未修复的竖排样式")
                    
                    # 检查是否有横排样式
                    if 'horizontal-tb' in content:
                        has_horizontal = True
                    
                    # 检查是否注入了修复样式
                    if 'epub-fixer-style' in content:
                        has_fix_style = True
        
        # 检查CSS文件
        for name in zip_file.namelist():
            if name.endswith('.css'):
                with zip_file.open(name) as f:
                    content = f.read().decode('utf-8')
                    
                    # 检查是否有修复样式CSS文件
                    if 'epub_fixer' in name:
                        has_fix_style = True
                    
                    # 检查竖排样式是否被注释或修复
                    lines = content.split('\n')
                    for line in lines:
                        if 'writing-mode' in line.lower() and 'vertical' in line.lower():
                            if not line.strip().startswith('/*'):
                                # 检查是否已被替换为horizontal
                                if 'horizontal' not in line.lower():
                                    still_has_vertical = True
                                    print(f"✗ CSS文件 {name} 中仍有未修复的竖排样式: {line.strip()}")
    
    print()
    print("验证结果:")
    print(f"  {'✓' if not still_has_vertical else '✗'} 竖排样式已移除")
    print(f"  {'✓' if has_horizontal else '✗'} 已添加横排样式")
    print(f"  {'✓' if has_fix_style else '✗'} 已注入修复样式")
    print()
    
    # 步骤5：测试批量处理
    print("步骤5: 测试批量处理功能...")
    test_files = [input_path]
    output_dir = '/tmp/batch_test'
    os.makedirs(output_dir, exist_ok=True)
    
    result = fixer.batch_fix(test_files, output_dir)
    
    print(f"  总计: {result['total']} 个文件")
    print(f"  成功: {result['success']} 个")
    print(f"  失败: {result['failed']} 个")
    
    batch_success = result['success'] == 1 and result['failed'] == 0
    print(f"  {'✓' if batch_success else '✗'} 批量处理测试")
    print()
    
    # 最终结果
    all_passed = (not still_has_vertical and has_horizontal and 
                  has_fix_style and batch_success)
    
    print("=" * 60)
    if all_passed:
        print("所有集成测试通过！✓")
    else:
        print("部分测试失败！✗")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    try:
        success = test_full_workflow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
