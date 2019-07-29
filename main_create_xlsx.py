#!/usr/bin/python3
import glob

from pyexcel.cookbook import merge_all_to_a_book

if __name__ == "__main__":
    merge_all_to_a_book(glob.glob("/home/rafael/*.csv"), "rev-sau-50.xlsx")