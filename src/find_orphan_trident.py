import os
import sys
# 引数で与えられたディレクトリ内で input-trident.txt だけがあって not-found.txt も output-*.overpassql もないパスを探して出力する

dir_path = sys.argv[1]


def find_orphan_trident(dir_path):
    for root, dirs, files in os.walk(dir_path):
        if "input-trident.txt" in files and not "not-found.txt" in files and not any(
            f.startswith("output-") and f.endswith(".overpassql") for f in files
        ):
            print(root)


find_orphan_trident(dir_path)
