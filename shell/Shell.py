# Author: Stephanie Galvan
# Class: Theory of Operating Systems
# Assignment 1: Shell
# Python version: 3.7.0
# Description: To build a user shell for a Unix operating system

import os, sys, re

while True:
    # default prompt
    command = input("$ ")
    if command.strip() == "exit":
        sys.exit(0)
    else:
        continue
