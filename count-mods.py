#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统计整合包里模组的数量与体积。

不需要安装任何依赖，Python 3.6+ 直接跑：

    python count-mods.py            # 概览：数量、总体积、最大的几个
    python count-mods.py --list     # 额外列出全部模组文件名
    python count-mods.py ./mods     # 指定别的目录
"""
import argparse
import os
import sys

# Windows 控制台默认编码可能不是 UTF-8，模组名里有非 ASCII 字符时会炸
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ENABLED_EXT = ".jar"
DISABLED_EXT = ".jar.disabled"
TOP_N = 8


def human(size):
    """字节数转成人能读的单位。"""
    step = 1024.0
    for unit in ("B", "KB", "MB", "GB"):
        if size < step or unit == "GB":
            return "%.2f %s" % (size, unit)
        size /= step


def scan(mods_dir):
    """扫一遍目录，返回 (启用的, 禁用的)，每项为 (文件名, 字节数)。"""
    enabled, disabled = [], []
    if not os.path.isdir(mods_dir):
        sys.exit("找不到模组目录：%s" % mods_dir)

    for name in sorted(os.listdir(mods_dir)):
        path = os.path.join(mods_dir, name)
        if not os.path.isfile(path):
            continue
        size = os.path.getsize(path)
        if name.lower().endswith(DISABLED_EXT):
            disabled.append((name, size))
        elif name.lower().endswith(ENABLED_EXT):
            enabled.append((name, size))
    return enabled, disabled


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="统计 Minecraft 整合包里的模组数量与体积")
    parser.add_argument("directory", nargs="?", default=os.path.join(here, "mods"),
                        help="模组目录，默认为脚本同级的 mods/")
    parser.add_argument("--list", action="store_true", help="额外列出全部模组文件名")
    parser.add_argument("--top", type=int, default=TOP_N, help="显示体积最大的几个，默认 8")
    args = parser.parse_args()

    enabled, disabled = scan(args.directory)
    total = len(enabled) + len(disabled)
    if total == 0:
        sys.exit("目录里没有找到任何 .jar 文件：%s" % args.directory)

    enabled_size = sum(s for _, s in enabled)
    disabled_size = sum(s for _, s in disabled)
    all_size = enabled_size + disabled_size

    print("模组目录：%s" % os.path.abspath(args.directory))
    print("-" * 52)
    print("已启用模组：%d 个" % len(enabled))
    print("已禁用模组：%d 个" % len(disabled))
    print("合        计：%d 个" % total)
    print("-" * 52)
    print("启用体积：%s" % human(enabled_size))
    if disabled:
        print("禁用体积：%s" % human(disabled_size))
    print("总体积  ：%s" % human(all_size))
    print("平均体积：%s" % human(all_size / total))

    if args.top > 0:
        print("-" * 52)
        print("体积最大的 %d 个：" % args.top)
        for name, size in sorted(enabled + disabled, key=lambda x: x[1], reverse=True)[:args.top]:
            print("  %10s  %s" % (human(size), name))

    if args.list:
        print("-" * 52)
        print("全部模组（%d 个）：" % total)
        for i, (name, size) in enumerate(enabled + disabled, 1):
            print("  %3d. %s  [%s]" % (i, name, human(size)))


if __name__ == "__main__":
    main()
