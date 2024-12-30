import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import shutil
import zipfile
import time
import subprocess

class LivpToZip:
    def __init__(self, master):
        self.master = master
        master.title("LIVP to ZIP Converter")
        self.set_window_properties()
        
        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 创建选择文件按钮
        self.select_button = ttk.Button(master, text="选择文件", command=self.select_files, style="TButton")
        self.select_button.pack(pady=20, expand=True)
        
        # 创建转换按钮
        self.convert_button = ttk.Button(master, text="转换并解压", command=self.convert_and_extract, state=tk.DISABLED, style="TButton")
        self.convert_button.pack(pady=20, expand=True)
        
        # 创建进度条
        self.progress = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10, expand=True)

        # 保存选择的文件路径
        self.selected_files = []

    def set_window_properties(self):
        """设置窗口属性"""
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = 400
        window_height = 300
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.master.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.master.resizable(True, True)

    def select_files(self):
        """让用户选择.livp文件"""
        files = filedialog.askopenfilenames(filetypes=[("LIVP files", "*.livp")])
        if files:
            self.selected_files = list(files)
            self.convert_button.config(state=tk.NORMAL)

    def convert_and_extract(self):
        """将.livp文件复制并重命名为.zip文件，然后解压到指定目录"""
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择一个或多个.livp文件。")
            return

        output_dir = filedialog.askdirectory(title="选择输出目录")
        if not output_dir:
            return

        # 初始化进度条
        self.progress['value'] = 0
        self.progress['maximum'] = len(self.selected_files)
        errors = []

        for idx, file_path in enumerate(self.selected_files):
            file_name = os.path.basename(file_path)
            zip_file_path = os.path.join(os.path.dirname(file_path), os.path.splitext(file_name)[0] + '.zip')
            shutil.copy2(file_path, zip_file_path)
            extract_dir = os.path.join(output_dir, os.path.splitext(file_name)[0])
            os.makedirs(extract_dir, exist_ok=True)
            
            try:
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            except zipfile.BadZipFile:
                errors.append(f"文件 {file_name} 不是一个有效的ZIP文件。")
            except Exception as e:
                errors.append(f"转换或解压文件 {file_name} 时出错: {str(e)}")
            
            try:
                time.sleep(1)
                subprocess.run(f"del /F /Q \"{zip_file_path}\"", shell=True, check=True)
            except subprocess.CalledProcessError:
                print(f"无法删除文件 {zip_file_path}，请手动删除。")
            except Exception as e:
                print(f"删除文件 {zip_file_path} 时发生错误: {str(e)}")
            
            # 更新进度条
            self.progress['value'] += 1
            self.master.update()  # 更新窗口显示进度条变化

        self.selected_files = []
        self.convert_button.config(state=tk.DISABLED)

        # 处理错误信息和显示总体提示
        if errors:
            error_message = "\n".join(errors)
            messagebox.showerror("错误", f"处理过程中出现了一些错误:\n{error_message}")
        else:
            messagebox.showinfo("成功", f"所有文件已成功转换并解压到 {output_dir}")

    def on_closing(self):
        if messagebox.askokcancel("退出", "您确定要退出程序吗？"):
            self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = LivpToZip(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
