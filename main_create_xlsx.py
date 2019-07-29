#!/usr/bin/python3
import glob

from pyexcel.cookbook import merge_all_to_a_book

if __name__ == "__main__":
    merge_all_to_a_book(sorted(glob.glob("/home/rafael/Temp/rev-saude/por_ano/t2/classes/*.csv")), "/home/rafael/Temp/rev-saude/por_ano/t2/rev-sau-50.xlsx")