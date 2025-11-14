#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EPUB格式修复工具GUI界面
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from typing import List
from epub_fixer import EPUBFixer


class EPUBFixerGUI:
    """EPUB格式修复工具图形界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("EPUB格式修复工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.fixer = EPUBFixer()
        self.selected_files: List[str] = []
        
        self._create_widgets()
        self._setup_layout()
        
    def _create_widgets(self):
        """创建界面组件"""
        # 标题
        title_label = ttk.Label(
            self.root,
            text="EPUB格式修复工具",
            font=("Arial", 16, "bold")
        )
        self.title_label = title_label
        
        # 说明文本
        desc_label = ttk.Label(
            self.root,
            text="修复机翻后的EPUB文件中的文字排版方向和字体问题",
            font=("Arial", 10)
        )
        self.desc_label = desc_label
        
        # 文件选择框架
        file_frame = ttk.LabelFrame(self.root, text="文件选择", padding=10)
        self.file_frame = file_frame
        
        # 单文件选择按钮
        single_file_btn = ttk.Button(
            file_frame,
            text="选择单个文件",
            command=self._select_single_file
        )
        self.single_file_btn = single_file_btn
        
        # 批量文件选择按钮
        batch_file_btn = ttk.Button(
            file_frame,
            text="选择多个文件",
            command=self._select_batch_files
        )
        self.batch_file_btn = batch_file_btn
        
        # 清除选择按钮
        clear_btn = ttk.Button(
            file_frame,
            text="清除选择",
            command=self._clear_selection
        )
        self.clear_btn = clear_btn
        
        # 文件列表框架
        list_frame = ttk.Frame(self.root)
        self.list_frame = list_frame
        
        # 文件列表
        files_listbox = tk.Listbox(list_frame, height=10)
        self.files_listbox = files_listbox
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=files_listbox.yview)
        self.scrollbar = scrollbar
        files_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 选项框架
        options_frame = ttk.LabelFrame(self.root, text="处理选项", padding=10)
        self.options_frame = options_frame
        
        # 覆盖原文件选项
        self.overwrite_var = tk.BooleanVar(value=False)
        overwrite_check = ttk.Checkbutton(
            options_frame,
            text="覆盖原文件（不勾选则保存到新位置）",
            variable=self.overwrite_var
        )
        self.overwrite_check = overwrite_check
        
        # 输出目录选择
        output_frame = ttk.Frame(options_frame)
        self.output_frame = output_frame
        
        output_label = ttk.Label(output_frame, text="输出目录:")
        self.output_label = output_label
        
        self.output_path_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var, width=40)
        self.output_entry = output_entry
        
        output_browse_btn = ttk.Button(
            output_frame,
            text="浏览...",
            command=self._select_output_dir
        )
        self.output_browse_btn = output_browse_btn
        
        # 进度框架
        progress_frame = ttk.LabelFrame(self.root, text="处理进度", padding=10)
        self.progress_frame = progress_frame
        
        # 进度条
        progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar = progress_bar
        
        # 进度标签
        progress_label = ttk.Label(progress_frame, text="就绪")
        self.progress_label = progress_label
        
        # 控制按钮框架
        control_frame = ttk.Frame(self.root)
        self.control_frame = control_frame
        
        # 开始处理按钮
        start_btn = ttk.Button(
            control_frame,
            text="开始处理",
            command=self._start_processing,
            style="Accent.TButton"
        )
        self.start_btn = start_btn
        
        # 退出按钮
        quit_btn = ttk.Button(
            control_frame,
            text="退出",
            command=self.root.quit
        )
        self.quit_btn = quit_btn
        
    def _setup_layout(self):
        """设置布局"""
        # 标题
        self.title_label.pack(pady=10)
        self.desc_label.pack(pady=5)
        
        # 文件选择框架
        self.file_frame.pack(fill="x", padx=20, pady=10)
        self.single_file_btn.pack(side="left", padx=5)
        self.batch_file_btn.pack(side="left", padx=5)
        self.clear_btn.pack(side="left", padx=5)
        
        # 文件列表
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.files_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # 选项框架
        self.options_frame.pack(fill="x", padx=20, pady=10)
        self.overwrite_check.pack(anchor="w", pady=5)
        self.output_frame.pack(fill="x", pady=5)
        self.output_label.pack(side="left", padx=5)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.output_browse_btn.pack(side="left", padx=5)
        
        # 进度框架
        self.progress_frame.pack(fill="x", padx=20, pady=10)
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_label.pack(pady=5)
        
        # 控制按钮
        self.control_frame.pack(pady=10)
        self.start_btn.pack(side="left", padx=10)
        self.quit_btn.pack(side="left", padx=10)
        
        # 绑定覆盖选项变化事件
        self.overwrite_var.trace('w', self._on_overwrite_changed)
        self._on_overwrite_changed()
        
    def _select_single_file(self):
        """选择单个文件"""
        filename = filedialog.askopenfilename(
            title="选择EPUB文件",
            filetypes=[("EPUB文件", "*.epub"), ("所有文件", "*.*")]
        )
        
        if filename:
            self.selected_files = [filename]
            self._update_file_list()
            
    def _select_batch_files(self):
        """选择多个文件"""
        filenames = filedialog.askopenfilenames(
            title="选择EPUB文件",
            filetypes=[("EPUB文件", "*.epub"), ("所有文件", "*.*")]
        )
        
        if filenames:
            self.selected_files = list(filenames)
            self._update_file_list()
            
    def _clear_selection(self):
        """清除选择"""
        self.selected_files = []
        self._update_file_list()
        
    def _update_file_list(self):
        """更新文件列表显示"""
        self.files_listbox.delete(0, tk.END)
        for filepath in self.selected_files:
            self.files_listbox.insert(tk.END, os.path.basename(filepath))
            
    def _select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_path_var.set(directory)
            
    def _on_overwrite_changed(self, *args):
        """覆盖选项变化时的处理"""
        if self.overwrite_var.get():
            # 覆盖原文件，禁用输出目录选择
            self.output_entry.config(state="disabled")
            self.output_browse_btn.config(state="disabled")
        else:
            # 不覆盖，启用输出目录选择
            self.output_entry.config(state="normal")
            self.output_browse_btn.config(state="normal")
            
    def _start_processing(self):
        """开始处理文件"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要处理的EPUB文件！")
            return
            
        if not self.overwrite_var.get() and not self.output_path_var.get():
            messagebox.showwarning("警告", "请选择输出目录或勾选覆盖原文件！")
            return
            
        # 禁用控制按钮
        self._set_controls_enabled(False)
        
        # 在新线程中处理
        thread = threading.Thread(target=self._process_files)
        thread.daemon = True
        thread.start()
        
    def _process_files(self):
        """处理文件（在后台线程中运行）"""
        try:
            output_dir = None if self.overwrite_var.get() else self.output_path_var.get()
            
            # 重置进度
            self.progress_bar['value'] = 0
            self.progress_bar['maximum'] = len(self.selected_files)
            
            if len(self.selected_files) == 1:
                # 单文件处理
                self._update_progress(0, 1, "正在处理...")
                success = self.fixer.fix_epub(self.selected_files[0], 
                                              os.path.join(output_dir, os.path.basename(self.selected_files[0])) if output_dir else None)
                self._update_progress(1, 1, "完成！")
                
                if success:
                    self._show_result("成功", "文件处理完成！")
                else:
                    self._show_result("错误", "文件处理失败！")
            else:
                # 批量处理
                result = self.fixer.batch_fix(self.selected_files, output_dir)
                
                message = f"处理完成！\n\n"
                message += f"总计: {result['total']} 个文件\n"
                message += f"成功: {result['success']} 个\n"
                message += f"失败: {result['failed']} 个"
                
                if result['failed_files']:
                    message += "\n\n失败的文件:\n"
                    for f in result['failed_files']:
                        message += f"- {os.path.basename(f)}\n"
                
                self._update_progress(result['success'], result['total'], "完成！")
                self._show_result("批量处理完成", message)
                
        except Exception as e:
            self._show_result("错误", f"处理过程中出现错误:\n{str(e)}")
        finally:
            # 重新启用控制按钮
            self._set_controls_enabled(True)
            
    def _update_progress(self, current, total, message):
        """更新进度显示"""
        def update():
            self.progress_bar['value'] = current
            self.progress_label.config(text=f"{message} ({current}/{total})")
            
        self.root.after(0, update)
        
    def _show_result(self, title, message):
        """显示结果对话框"""
        def show():
            messagebox.showinfo(title, message)
            
        self.root.after(0, show)
        
    def _set_controls_enabled(self, enabled):
        """启用/禁用控制按钮"""
        def update():
            state = "normal" if enabled else "disabled"
            self.single_file_btn.config(state=state)
            self.batch_file_btn.config(state=state)
            self.clear_btn.config(state=state)
            self.start_btn.config(state=state)
            self.overwrite_check.config(state=state)
            if not self.overwrite_var.get():
                self.output_browse_btn.config(state=state)
                
        self.root.after(0, update)


def main():
    """主函数"""
    root = tk.Tk()
    app = EPUBFixerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
