# Author: Stephanie Galvan
# Class: Theory of Operating Systems
# Assignment 1: Shell
# Python version: 3.7.0
# Description: To build a user shell for a Unix operating system

import os
import re
import sys

while True:
    # default prompt
    command = input("$ ")
    if not command:
        # when empty, do nothing and continue
        continue
    elif command.strip() == "exit":
        sys.exit(0)
    else:
        rc = os.fork()

        # fork failure
        if rc < 0:
            os.write(2, ("fork failed, returning %d\n" % rc).encode())
            sys.exit(1)

        # child
        elif rc == 0:
            args = command.split()
            for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ)  # try to exec program
                except FileNotFoundError:  # ...expected
                    pass  # ...fail quietly

            os.write(2, ("Could not exec %s\n" % (args[0])).encode())
            sys.exit(1)  # terminate with error

        # parent (forked ok)
        else:
            # process done
            os.wait()
