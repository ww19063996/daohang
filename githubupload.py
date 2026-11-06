import base64
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests


def upload_to_github():
    token = entry_token.get().strip()
    repo = entry_repo.get().strip()  # 格式: 用户名/仓库名
    branch = entry_branch.get().strip() or "main"
    file_path = entry_file.get().strip()
    commit_msg = (
        entry_msg.get().strip() or f"Upload {os.path.basename(file_path)}"
    )

    if not all([token, repo, file_path]):
        messagebox.showerror(
            "提示", "请填写完整的 Token、仓库名（用户名/仓库）并选择文件！"
        )
        return

    if not os.path.exists(file_path):
        messagebox.showerror("错误", "所选文件不存在！")
        return

    file_name = os.path.basename(file_path)
    url = f"https://api.github.com/repos/{repo}/contents/{file_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    status_label.config(text="正在读取并上传文件...", fg="blue")
    root.update()

    try:
        # 读取文件并转换为 Base64
        with open(file_path, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 检查远程是否存在同名文件，获取 SHA（覆盖写入必须携带 SHA）
        sha = None
        check_res = requests.get(
            f"{url}?ref={branch}", headers=headers, timeout=10
        )
        if check_res.status_code == 200:
            sha = check_res.json().get("sha")

        payload = {"message": commit_msg, "content": content_b64, "branch": branch}
        if sha:
            payload["sha"] = sha

        # 上传/更新文件
        put_res = requests.put(url, headers=headers, json=payload, timeout=20)
        if put_res.status_code in [200, 201]:
            status_label.config(text="上传成功！", fg="green")
            messagebox.showinfo("成功", f"文件 {file_name} 已成功推送至 GitHub！")
        else:
            err_msg = put_res.json().get("message", put_res.text)
            status_label.config(text="上传失败", fg="red")
            messagebox.showerror("上传失败", f"错误码: {put_res.status_code}\n{err_msg}")
    except Exception as e:
        status_label.config(text="请求异常", fg="red")
        messagebox.showerror("异常", str(e))


def select_file():
    path = filedialog.askopenfilename()
    if path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, path)


# 构建图形界面
root = tk.Tk()
root.title("GitHub 极简文件直传工具")
root.geometry("520x360")
root.resizable(False, False)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill=tk.BOTH, expand=True)

# Token
tk.Label(frame, text="GitHub Token (替代密码):", anchor="w").pack(
    fill=tk.X, pady=(0, 2)
)
entry_token = tk.Entry(frame, show="*")
entry_token.pack(fill=tk.X, pady=(0, 10))

# 仓库
tk.Label(frame, text="目标仓库 (格式: 你的用户名/仓库名):", anchor="w").pack(
    fill=tk.X, pady=(0, 2)
)
entry_repo = tk.Entry(frame)
entry_repo.pack(fill=tk.X, pady=(0, 10))

# 分支
tk.Label(frame, text="分支名 (默认 main):", anchor="w").pack(
    fill=tk.X, pady=(0, 2)
)
entry_branch = tk.Entry(frame)
entry_branch.insert(0, "main")
entry_branch.pack(fill=tk.X, pady=(0, 10))

# 本地文件
tk.Label(frame, text="本地文件路径:", anchor="w").pack(fill=tk.X, pady=(0, 2))
file_box = tk.Frame(frame)
file_box.pack(fill=tk.X, pady=(0, 10))
entry_file = tk.Entry(file_box)
entry_file.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
btn_browse = tk.Button(file_box, text="选择文件", command=select_file)
btn_browse.pack(side=tk.RIGHT)

# 提交信息
tk.Label(frame, text="提交说明 (可选):", anchor="w").pack(fill=tk.X, pady=(0, 2))
entry_msg = tk.Entry(frame)
entry_msg.pack(fill=tk.X, pady=(0, 15))

# 上传按钮
btn_upload = tk.Button(
    frame,
    text="确认上传至 GitHub",
    bg="#2da44e",
    fg="white",
    font=("Arial", 11, "bold"),
    command=upload_to_github,
)
btn_upload.pack(fill=tk.X, ipady=4)

status_label = tk.Label(frame, text="", pady=5)
status_label.pack()

root.mainloop()