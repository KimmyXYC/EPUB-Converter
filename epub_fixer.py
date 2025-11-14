#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB格式修复核心模块
修复机翻后的EPUB文件中的文字排版方向和字体问题
"""

import os
import zipfile
import tempfile
import shutil
from typing import List, Optional
from ebooklib import epub
from bs4 import BeautifulSoup


class EPUBFixer:
    """EPUB格式修复器"""
    
    def __init__(self):
        self.processed_files = 0
        self.total_files = 0
        self.current_file = ""
        
    def fix_epub(self, input_path: str, output_path: Optional[str] = None) -> bool:
        """
        修复单个EPUB文件
        
        Args:
            input_path: 输入EPUB文件路径
            output_path: 输出EPUB文件路径，如果为None则覆盖原文件
            
        Returns:
            bool: 修复是否成功
        """
        try:
            self.current_file = os.path.basename(input_path)
            
            # 读取EPUB文件
            book = epub.read_epub(input_path)
            
            # 修复所有HTML文档
            for item in book.get_items():
                if item.get_type() == 9:  # ITEM_DOCUMENT
                    content = item.get_content()
                    if content:  # 确保内容不为空
                        fixed_content = self._fix_html_content(content)
                        item.set_content(fixed_content)
            
            # 修复CSS样式表
            for item in book.get_items():
                if item.get_type() == 2:  # ITEM_STYLE (CSS files)
                    content = item.get_content()
                    if content:  # 确保内容不为空
                        fixed_content = self._fix_css_content(content)
                        item.set_content(fixed_content)
            
            # 添加全局修复CSS文件
            fix_css = epub.EpubItem(
                uid="epub_fixer_style",
                file_name="style/epub_fixer.css",
                media_type="text/css",
                content=self._get_fix_css().encode('utf-8')
            )
            book.add_item(fix_css)
            
            # 修复TOC中的UID问题
            self._fix_toc_uids(book)
            
            # 保存修复后的EPUB
            if output_path is None:
                output_path = input_path
            
            epub.write_epub(output_path, book)
            self.processed_files += 1
            
            return True
            
        except Exception as e:
            print(f"修复文件 {input_path} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _fix_html_content(self, content: bytes) -> bytes:
        """
        修复HTML内容中的排版和字体问题
        
        Args:
            content: 原始HTML内容
            
        Returns:
            bytes: 修复后的HTML内容
        """
        try:
            # 使用html.parser来处理XHTML，保持更好的兼容性
            soup = BeautifulSoup(content, 'html.parser')
            
            # 修复body标签的writing-mode
            body = soup.find('body')
            if body:
                # 移除可能导致竖排的样式
                if body.get('style'):
                    style = body.get('style', '')
                    style = self._fix_style_attribute(style)
                    body['style'] = style
            
            # 修复所有标签的style属性
            for tag in soup.find_all(style=True):
                style = tag.get('style', '')
                fixed_style = self._fix_style_attribute(style)
                tag['style'] = fixed_style
            
            # 在head中添加修复样式
            head = soup.find('head')
            if head:
                # 检查是否已经存在修复样式
                existing_style = head.find('style', id='epub-fixer-style')
                if not existing_style:
                    style_tag = soup.new_tag('style')
                    style_tag['id'] = 'epub-fixer-style'
                    style_tag.string = self._get_fix_css()
                    head.append(style_tag)
            
            return str(soup).encode('utf-8')
            
        except Exception as e:
            print(f"修复HTML内容时出错: {str(e)}")
            return content
    
    def _fix_style_attribute(self, style: str) -> str:
        """
        修复style属性中的排版问题
        
        Args:
            style: 原始style字符串
            
        Returns:
            str: 修复后的style字符串
        """
        # 移除竖排相关的样式
        style_rules = [s.strip() for s in style.split(';') if s.strip()]
        fixed_rules = []
        
        for rule in style_rules:
            # 移除或修复writing-mode
            if 'writing-mode' in rule.lower():
                # 将竖排改为横排
                if 'vertical' in rule.lower() or 'tb' in rule.lower():
                    fixed_rules.append('writing-mode: horizontal-tb')
                    continue
            
            # 移除text-orientation
            if 'text-orientation' in rule.lower():
                continue
            
            # 移除-webkit-writing-mode
            if '-webkit-writing-mode' in rule.lower():
                continue
                
            # 移除-epub-writing-mode
            if '-epub-writing-mode' in rule.lower():
                continue
            
            fixed_rules.append(rule)
        
        return '; '.join(fixed_rules)
    
    def _fix_css_content(self, content: bytes) -> bytes:
        """
        修复CSS内容中的排版问题
        
        Args:
            content: 原始CSS内容
            
        Returns:
            bytes: 修复后的CSS内容
        """
        try:
            css_text = content.decode('utf-8')
            
            # 修复writing-mode相关的CSS规则
            lines = css_text.split('\n')
            fixed_lines = []
            
            for line in lines:
                line_lower = line.lower()
                
                # 替换竖排为横排
                if 'writing-mode' in line_lower and ('vertical' in line_lower or 'tb-rl' in line_lower or 'tb' in line_lower):
                    # 替换为横排
                    fixed_lines.append(line.replace('vertical-rl', 'horizontal-tb')
                                          .replace('vertical-lr', 'horizontal-tb')
                                          .replace('tb-rl', 'horizontal-tb')
                                          .replace('tb-lr', 'horizontal-tb'))
                    continue
                
                # 注释掉text-orientation
                if 'text-orientation' in line_lower:
                    fixed_lines.append('/* ' + line + ' */')
                    continue
                
                # 注释掉-webkit-writing-mode和-epub-writing-mode如果是竖排
                if ('-webkit-writing-mode' in line_lower or '-epub-writing-mode' in line_lower):
                    if 'vertical' in line_lower:
                        fixed_lines.append('/* ' + line + ' */')
                        continue
                
                fixed_lines.append(line)
            
            return '\n'.join(fixed_lines).encode('utf-8')
            
        except Exception as e:
            print(f"修复CSS内容时出错: {str(e)}")
            return content
    
    def _fix_toc_uids(self, book):
        """
        修复TOC中Link对象缺少UID的问题
        
        Args:
            book: EPUB book对象
        """
        import uuid
        
        def fix_toc_item(item):
            """递归修复TOC项"""
            if isinstance(item, tuple):
                # 处理嵌套的TOC结构
                for sub_item in item:
                    fix_toc_item(sub_item)
            elif isinstance(item, list):
                for sub_item in item:
                    fix_toc_item(sub_item)
            elif hasattr(item, 'uid'):
                if item.uid is None:
                    # 为Link对象生成UID
                    item.uid = str(uuid.uuid4())
        
        if book.toc:
            if isinstance(book.toc, (list, tuple)):
                for item in book.toc:
                    fix_toc_item(item)
            else:
                fix_toc_item(book.toc)
    
    def _get_fix_css(self) -> str:
        """
        获取用于修复排版的CSS规则
        
        Returns:
            str: CSS规则字符串
        """
        return """
/* EPUB格式修复样式 */
body {
    writing-mode: horizontal-tb !important;
    -webkit-writing-mode: horizontal-tb !important;
    -epub-writing-mode: horizontal-tb !important;
    direction: ltr;
}

* {
    text-orientation: mixed !important;
}

/* 确保中文字体正确显示 */
body, p, div, span {
    font-family: "Microsoft YaHei", "SimSun", "PingFang SC", "Noto Sans CJK SC", sans-serif;
}
"""
    
    def batch_fix(self, input_paths: List[str], output_dir: Optional[str] = None) -> dict:
        """
        批量修复EPUB文件
        
        Args:
            input_paths: 输入EPUB文件路径列表
            output_dir: 输出目录，如果为None则覆盖原文件
            
        Returns:
            dict: 包含成功和失败统计的字典
        """
        self.total_files = len(input_paths)
        self.processed_files = 0
        
        success_count = 0
        failed_files = []
        
        for input_path in input_paths:
            if output_dir:
                filename = os.path.basename(input_path)
                output_path = os.path.join(output_dir, filename)
            else:
                output_path = None
            
            if self.fix_epub(input_path, output_path):
                success_count += 1
            else:
                failed_files.append(input_path)
        
        return {
            'total': self.total_files,
            'success': success_count,
            'failed': len(failed_files),
            'failed_files': failed_files
        }
    
    def get_progress(self) -> tuple:
        """
        获取处理进度
        
        Returns:
            tuple: (已处理数量, 总数量, 当前文件名)
        """
        return (self.processed_files, self.total_files, self.current_file)
