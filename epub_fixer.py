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
            
            # 如果output_path为None，使用临时文件
            if output_path is None:
                output_path = input_path
            
            # 创建临时目录来处理EPUB
            with tempfile.TemporaryDirectory() as temp_dir:
                # 解压EPUB到临时目录
                with zipfile.ZipFile(input_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # 使用ebooklib读取EPUB结构（用于获取元数据和列表）
                book = epub.read_epub(input_path)
                
                # 查找并修复所有HTML文件
                for item in book.get_items():
                    if item.get_type() == 9:  # ITEM_DOCUMENT
                        # 找到文件在解压目录中的实际路径
                        file_found = False
                        for prefix in ['EPUB/', 'OEBPS/', '']:
                            file_path = os.path.join(temp_dir, prefix, item.file_name)
                            if os.path.exists(file_path):
                                # 读取并修复HTML内容
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read().encode('utf-8')
                                
                                fixed_content = self._fix_html_content(content)
                                
                                # 写回修复后的内容
                                with open(file_path, 'wb') as f:
                                    f.write(fixed_content)
                                
                                file_found = True
                                break
                        
                        if not file_found:
                            print(f"警告: 未找到文件 {item.file_name}")
                
                # 修复CSS样式表
                for item in book.get_items():
                    if item.get_type() == 2:  # ITEM_STYLE
                        file_found = False
                        for prefix in ['EPUB/', 'OEBPS/', '']:
                            file_path = os.path.join(temp_dir, prefix, item.file_name)
                            if os.path.exists(file_path):
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read().encode('utf-8')
                                
                                fixed_content = self._fix_css_content(content)
                                
                                with open(file_path, 'wb') as f:
                                    f.write(fixed_content)
                                
                                file_found = True
                                break
                
                # 添加全局修复CSS文件
                for prefix in ['EPUB/', 'OEBPS/', '']:
                    style_dir = os.path.join(temp_dir, prefix, 'style')
                    if os.path.exists(style_dir):
                        fix_css_path = os.path.join(style_dir, 'epub_fixer.css')
                        with open(fix_css_path, 'w', encoding='utf-8') as f:
                            f.write(self._get_fix_css())
                        break
                
                # 修复页面翻页方向（修改OPF文件）
                self._fix_opf_direction(temp_dir)
                
                # 重新打包EPUB
                with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                    # 首先添加mimetype文件（必须不压缩且首先添加）
                    mimetype_path = os.path.join(temp_dir, 'mimetype')
                    if os.path.exists(mimetype_path):
                        zip_out.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
                    
                    # 添加其他所有文件
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            if file == 'mimetype':
                                continue
                            file_path = os.path.join(root, file)
                            arc_name = os.path.relpath(file_path, temp_dir)
                            zip_out.write(file_path, arc_name)
            
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
    
    def _fix_page_progression_direction(self, book):
        """
        修复EPUB的页面翻页方向
        将右到左（RTL）改为左到右（LTR），适用于横排中文文本
        
        Args:
            book: EPUB book对象
        """
        # 检查并修复book.direction属性
        # RTL (right-to-left) 用于日文等竖排文本
        # LTR (left-to-right) 用于中文等横排文本
        if hasattr(book, 'direction'):
            if book.direction == 'rtl' or book.direction is None:
                # 如果是RTL或未设置（None），改为LTR
                book.direction = 'ltr'
        else:
            # 如果没有direction属性，设置为LTR
            book.direction = 'ltr'
    
    def _fix_opf_direction(self, epub_dir: str):
        """
        修复OPF文件中的页面翻页方向
        
        Args:
            epub_dir: EPUB解压目录
        """
        import xml.etree.ElementTree as ET
        
        # 查找OPF文件
        opf_path = None
        for prefix in ['EPUB/', 'OEBPS/', '']:
            for file in os.listdir(os.path.join(epub_dir, prefix)) if os.path.exists(os.path.join(epub_dir, prefix)) else []:
                if file.endswith('.opf'):
                    opf_path = os.path.join(epub_dir, prefix, file)
                    break
            if opf_path:
                break
        
        if not opf_path:
            return
        
        try:
            # 解析OPF文件
            tree = ET.parse(opf_path)
            root = tree.getroot()
            
            # 查找spine元素
            ns = {'opf': 'http://www.idpf.org/2007/opf'}
            spine = root.find('.//opf:spine', ns)
            
            if spine is not None:
                # 修改page-progression-direction属性
                if spine.get('page-progression-direction') == 'rtl':
                    spine.set('page-progression-direction', 'ltr')
            
            # 保存修改后的OPF文件
            tree.write(opf_path, encoding='utf-8', xml_declaration=True)
        except Exception as e:
            print(f"修复OPF文件时出错: {str(e)}")
    
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

/* 仅对文本元素应用text-orientation，避免影响图片 */
p, div, span, h1, h2, h3, h4, h5, h6 {
    text-orientation: mixed !important;
}

/* 确保中文字体正确显示 */
body, p, div, span {
    font-family: "Microsoft YaHei", "SimSun", "PingFang SC", "Noto Sans CJK SC", sans-serif;
}

/* 确保图片自动缩放以适应屏幕宽度 */
img {
    max-width: 100%;
    height: auto;
}

/* 确保SVG图片自动缩放以适应屏幕宽度 */
svg {
    max-width: 100%;
    height: auto;
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
