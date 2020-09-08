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
    if command.strip() == "exit":
        sys.exit(0)
    else:
        # [TO BE UPDATED] To test that exec is working, just allow one word inputs by user
        if len(command.split()) != 1:
            os.write(1, "Error: Enter one word only\n".encode())

        # fork, exec, and wait part of the lab
        else:
            # fork (and printing the potential parent's pid)
            pid = os.getpid()
            os.write(1, ("about to fork (pid:%d)\n" % pid).encode())
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
                    os.write(1, ("Child %d:  ...trying to exec %s\n" % (os.getpid(), program)).encode())
                    try:
                        os.execve(program, args, os.environ)  # try to exec program
                    except FileNotFoundError:  # ...expected
                        pass  # ...fail quietly

                os.write(2, ("Child %d:    Could not exec %s\n" % (os.getpid(), args[0])).encode())
                sys.exit(1)  # terminate with error

            # parent (forked ok)
            else:
                # process done
                childPidCode = os.wait()
                os.write(1, ("\nParent %d: Child %d terminated with exit code %d\n" %
                             (pid, childPidCode[0], childPidCode[1])).encode())
