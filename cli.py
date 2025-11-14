#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB格式修复工具命令行界面
适用于无图形界面的环境
"""

import sys
import os
import argparse
from epub_fixer import EPUBFixer


def main():
    """命令行主函数"""
    parser = argparse.ArgumentParser(
        description='EPUB格式修复工具 - 修复机翻后的文字排版和字体问题',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 修复单个文件（覆盖原文件）
  %(prog)s input.epub

  # 修复单个文件（保存到新文件）
  %(prog)s input.epub -o output.epub

  # 批量修复（保存到指定目录）
  %(prog)s file1.epub file2.epub file3.epub -d ./fixed/

  # 批量修复（覆盖原文件）
  %(prog)s *.epub --overwrite
        """
    )
    
    parser.add_argument(
        'files',
        nargs='+',
        help='要修复的EPUB文件路径（可以是多个文件）'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='输出文件路径（仅用于单文件处理）'
    )
    
    parser.add_argument(
        '-d', '--output-dir',
        help='输出目录（用于批量处理）'
    )
    
    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='覆盖原文件（如果不指定输出路径）'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细处理信息'
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if len(args.files) > 1 and args.output:
        print("错误: 处理多个文件时不能使用 -o/--output 参数，请使用 -d/--output-dir")
        sys.exit(1)
    
    if not args.overwrite and not args.output and not args.output_dir:
        print("错误: 必须指定输出位置 (-o, -d) 或使用 --overwrite")
        sys.exit(1)
    
    # 创建修复器
    fixer = EPUBFixer()
    
    # 处理文件
    if len(args.files) == 1:
        # 单文件处理
        input_file = args.files[0]
        
        if not os.path.exists(input_file):
            print(f"错误: 文件不存在: {input_file}")
            sys.exit(1)
        
        if args.output:
            output_file = args.output
        elif args.output_dir:
            output_file = os.path.join(args.output_dir, os.path.basename(input_file))
            os.makedirs(args.output_dir, exist_ok=True)
        else:
            output_file = None  # 覆盖原文件
        
        print(f"正在处理: {input_file}")
        if args.verbose:
            print(f"  输出到: {output_file if output_file else '(覆盖原文件)'}")
        
        success = fixer.fix_epub(input_file, output_file)
        
        if success:
            print("✓ 处理完成!")
            sys.exit(0)
        else:
            print("✗ 处理失败!")
            sys.exit(1)
    
    else:
        # 批量处理
        print(f"开始批量处理 {len(args.files)} 个文件...")
        
        # 检查文件是否存在
        valid_files = []
        for f in args.files:
            if not os.path.exists(f):
                print(f"警告: 文件不存在，跳过: {f}")
            else:
                valid_files.append(f)
        
        if not valid_files:
            print("错误: 没有有效的文件可处理")
            sys.exit(1)
        
        output_dir = args.output_dir if args.output_dir else None
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        result = fixer.batch_fix(valid_files, output_dir)
        
        print()
        print("=" * 50)
        print("批量处理完成!")
        print(f"  总计: {result['total']} 个文件")
        print(f"  成功: {result['success']} 个")
        print(f"  失败: {result['failed']} 个")
        
        if result['failed_files']:
            print()
            print("失败的文件:")
            for f in result['failed_files']:
                print(f"  - {f}")
        print("=" * 50)
        
        sys.exit(0 if result['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
