# -*- coding: utf-8 -*-
"""解压学生作业 zip，兼容中文文件名（GBK/UTF-8），并输出文件清单。

用法:
    python unzip_assignment.py <zip路径> [解压目标目录]

输出:
    在目标目录解压全部文件，并打印每个文件的相对路径与大小（字节）。
"""
import sys
import zipfile
import os


def fix_name(name: str) -> str:
    """修复 Windows 压缩包中中文文件名的编码问题。"""
    try:
        return name.encode("cp437").decode("gbk")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def main() -> None:
    if len(sys.argv) < 2:
        print("用法: python unzip_assignment.py <zip路径> [解压目标目录]")
        sys.exit(1)

    zip_path = sys.argv[1]
    if len(sys.argv) >= 3:
        dest = sys.argv[2]
    else:
        base = os.path.splitext(os.path.basename(zip_path))[0]
        dest = os.path.join(os.path.dirname(os.path.abspath(zip_path)), base + "_extracted")

    os.makedirs(dest, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            fixed = fix_name(info.filename)
            target = os.path.join(dest, fixed)
            if info.is_dir():
                os.makedirs(target, exist_ok=True)
                continue
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as dst:
                dst.write(src.read())

    print(f"已解压到: {dest}")
    print("文件清单:")
    for root, _dirs, files in os.walk(dest):
        for f in sorted(files):
            full = os.path.join(root, f)
            rel = os.path.relpath(full, dest)
            size = os.path.getsize(full)
            print(f"  {rel}  ({size} bytes)")


if __name__ == "__main__":
    main()
