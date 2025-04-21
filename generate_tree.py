import os
import argparse
from pathlib import Path

def generate_tree(directory, prefix='', ignore_dirs=None, ignore_files=None, max_depth=None, current_depth=0):
    """生成目录树结构"""
    if ignore_dirs is None:
        ignore_dirs = ['.git', 'node_modules', '__pycache__', 'venv', '.idea', '.vscode']
    
    if ignore_files is None:
        ignore_files = ['.DS_Store', '.env', '.gitignore']
    
    if max_depth is not None and current_depth > max_depth:
        return

    # 获取目录下所有内容
    try:
        items = list(os.listdir(directory))
    except PermissionError:
        print(f"{prefix}├── {os.path.basename(directory)} [访问被拒绝]")
        return

    # 分离文件夹和文件
    dirs = []
    files = []
    for item in sorted(items):
        full_path = os.path.join(directory, item)
        if os.path.isdir(full_path) and item not in ignore_dirs:
            dirs.append(item)
        elif os.path.isfile(full_path) and item not in ignore_files:
            files.append(item)
    
    # 总计数
    count = len(dirs) + len(files)
    
    # 处理文件夹
    for i, d in enumerate(dirs):
        full_path = os.path.join(directory, d)
        is_last = i == len(dirs) - 1 and len(files) == 0
        
        if is_last:
            print(f"{prefix}└── {d}/")
            generate_tree(full_path, prefix + "    ", ignore_dirs, ignore_files, max_depth, current_depth + 1)
        else:
            print(f"{prefix}├── {d}/")
            generate_tree(full_path, prefix + "│   ", ignore_dirs, ignore_files, max_depth, current_depth + 1)
    
    # 处理文件
    for i, f in enumerate(files):
        is_last = i == len(files) - 1
        if is_last:
            print(f"{prefix}└── {f}")
        else:
            print(f"{prefix}├── {f}")

def main():
    parser = argparse.ArgumentParser(description='生成目录树结构')
    parser.add_argument('directory', nargs='?', default='.', help='要生成树状图的目录路径')
    parser.add_argument('-d', '--depth', type=int, help='遍历的最大深度')
    parser.add_argument('--ignore-dir', action='append', help='要忽略的目录名')
    parser.add_argument('--ignore-file', action='append', help='要忽略的文件名')
    parser.add_argument('-o', '--output', help='输出文件，不指定则输出到控制台')
    
    args = parser.parse_args()
    
    directory = os.path.abspath(args.directory)
    
    ignore_dirs = ['.git', 'node_modules', '__pycache__', 'venv', '.idea', '.vscode']
    if args.ignore_dir:
        ignore_dirs.extend(args.ignore_dir)
    
    ignore_files = ['.DS_Store', '.env', '.gitignore']
    if args.ignore_file:
        ignore_files.extend(args.ignore_file)
    
    # 重定向输出到文件
    if args.output:
        original_stdout = sys.stdout
        with open(args.output, 'w', encoding='utf-8') as f:
            sys.stdout = f
            print(f"目录树: {directory}\n")
            generate_tree(directory, '', ignore_dirs, ignore_files, args.depth)
            sys.stdout = original_stdout
        print(f"目录树已保存到 {args.output}")
    else:
        print(f"目录树: {directory}\n")
        generate_tree(directory, '', ignore_dirs, ignore_files, args.depth)

if __name__ == "__main__":
    import sys
    main()
