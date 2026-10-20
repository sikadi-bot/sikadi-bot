# -*- coding: utf-8 -*-
"""
一键同步：把本文件夹的改动提交并推送到 GitHub。
用法：双击同目录下的「一键备份.bat」。
"""
import os
import shutil
import subprocess
import sys
from datetime import datetime

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_NAME = os.path.basename(REPO_DIR)


def find_git():
    """按优先级找可用的 git.exe"""
    exe = shutil.which("git")
    if exe:
        return exe
    candidates = [
        r"C:\Program Files\Git\cmd\git.exe",
        r"C:\Program Files\Git\bin\git.exe",
        r"C:\Program Files (x86)\Git\cmd\git.exe",
        os.path.expanduser(r"~\AppData\Local\Programs\Git\cmd\git.exe"),
        r"E:\workbuddy\resources\vendor\PortableGit\cmd\git.exe",
        r"E:\workbuddy\resources\vendor\PortableGit\mingw64\bin\git.exe",
        r"D:\workbuddy\resources\vendor\PortableGit\cmd\git.exe",
        r"C:\workbuddy\resources\vendor\PortableGit\cmd\git.exe",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


GIT = find_git()


def git_capture(*args):
    """执行 git 并捕获输出"""
    return subprocess.run(
        [GIT, *args],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main():
    print("=" * 52)
    print("  同步到 GitHub ：" + REPO_NAME)
    print("=" * 52)

    if not GIT:
        print("\n找不到 git 程序，无法同步。")
        print("请把下面这段告诉帮你配置的人：")
        print("  sync.py 在所有候选路径中都找不到 git.exe")
        return 1

    # 1. 暂存全部改动
    print("\n[1/3] 扫描改动 ...")
    r = git_capture("add", "-A")
    if r.returncode != 0:
        print("  暂存失败：")
        print("  " + (r.stderr or r.stdout).strip())
        return 1

    # 2. 判断有没有东西要提交
    r = git_capture("status", "--porcelain")
    if r.returncode != 0:
        print("  读取状态失败：")
        print("  " + (r.stderr or r.stdout).strip())
        return 1

    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if not lines:
        print("  没有发现新改动。")
        print("\n结果：本地已是最新，不需要上传。")
        return 0

    print("  发现 " + str(len(lines)) + " 项改动：")
    for ln in lines[:12]:
        print("    " + ln)
    if len(lines) > 12:
        print("    ... 还有 " + str(len(lines) - 12) + " 项")

    # 3. 提交
    print("\n[2/3] 提交 ...")
    msg = "自动备份 " + datetime.now().strftime("%Y-%m-%d %H:%M")
    r = git_capture("commit", "-m", msg)
    if r.returncode != 0:
        print("  提交失败：")
        print("  " + (r.stdout + "\n" + r.stderr).strip())
        return 1
    print("  已提交：" + msg)

    # 4. 推送
    print("\n[3/3] 推送到 GitHub ...")
    print("  网络慢时可能要等十几秒，请不要关窗口。\n")
    r = subprocess.run([GIT, "push"], cwd=REPO_DIR)

    if r.returncode != 0:
        print("\n推送失败。常见的三种原因：")
        print("  1. 加速器没开 / 断网了  → 打开加速器后再双击一次本脚本")
        print("  2. GitHub 抽风           → 过几分钟再试")
        print("  3. SSH 22 端口被拦       → 告诉我，我换成 443 端口")
        print("\n你的改动已经保存在本地了，不会丢。")
        return 1

    print("\n" + "=" * 52)
    print("  同步完成，改动已上传到 GitHub")
    print("=" * 52)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n已取消。")
        sys.exit(1)
    except Exception as exc:
        print("\n出错了：" + str(exc))
        sys.exit(1)
