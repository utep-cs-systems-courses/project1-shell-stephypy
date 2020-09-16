#!/usr/bin/env python3

# Author: Stephanie Galvan
# Class: Theory of Operating Systems
# Assignment 1: Shell
# Python version: 3.7.0
# Description: To build a user shell for a Unix operating system

import os
import re
import sys
from aifc import Error


class NoArgumentsError(Error):
    """
    Raised when no argument was provided
    """
    pass


class TooManyArgumentsError(Error):
    """
    Raised when there are too many arguments
    """
    pass


def redirection(args_r):
    """
    Function to handle input and output redirection
    :param args_r: commands
    :return: args to be passed ine exec
    """
    # 1 output >
    if ">" in args_r:
        i = args_r.index(">")
        os.close(1)
        os.open(args_r[i + 1], os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(1, True)

    # 0 input <
    else:
        i = args_r.index("<")
        os.close(0)
        os.open(args_r[i + 1], os.O_RDONLY)
        os.set_inheritable(0, True)

    for dir in re.split(":", os.environ["PATH"]):  # try each directory in the path
        program = "%s/%s" % (dir, args_r[0])
        try:
            os.execve(program, args_r, os.environ)  # try to exec program
        except FileNotFoundError:  # ...expected
            pass  # ...fail quietly

    os.write(2, ("command %s not found \n" % (args_r[0])).encode())
    sys.exit(1)  # terminate with error


def execute_commands(args_e):
    """
    Function to execute commands by trying each directory in the path
    :param args_e: commands
    """

    # handle input/output redirection
    if ">" in args_e or "<" in args_e:
        redirection(args_e)

    # handle path names to execute
    elif "/" in args_e[0]:
        program = args_e[0]
        try:
            os.execve(program, args_e, os.environ)
        except FileNotFoundError:  # ...expected
            pass  # ...fail quietly

    else:
        for dir in re.split(":", os.environ["PATH"]):  # try each directory in the path
            program = "%s/%s" % (dir, args_e[0])
            try:
                os.execve(program, args_e, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly

    os.write(2, ("command %s not found \n" % (args_e[0])).encode())
    sys.exit(1)  # terminate with error


def pipe_command(args_p):
    """
    Handle pipes
    :param args_p: commands
    """
    pipe_left = args_p[0:args_p.index("|")]
    pipe_right = args_p[args_p.index("|") + 1:]

    pr, pw = os.pipe()
    rc = os.fork()

    # fork failure
    if rc < 0:
        sys.exit(1)

    # child - will write to pipe (left pipe)
    elif rc == 0:
        os.close(1)  # redirect child's stdout
        os.dup(pw)
        os.set_inheritable(1, True)
        for fd in (pr, pw):
            os.close(fd)
        execute_commands(pipe_left)
        os.write(2, ("Could not exec %s\n" % pipe_left[0]).encode())
        sys.exit(1)

    # parent (forked ok) (right pipe)
    else:
        os.close(0)
        os.dup(pr)
        os.set_inheritable(0, True)
        for fd in (pw, pr):
            os.close(fd)

        # handle two pipes
        if "|" in pipe_right:
            pipe_command(pipe_right)

        execute_commands(pipe_right)
        os.write(2, ("Could not exec %s\n" % pipe_right[0]).encode())
        sys.exit(1)


def shell():
    """
    A shell for a Unix operating system
    """

    while True:
        # default prompt
        command_string = "$ "
        if "PS1" in os.environ:
            command_string = os.environ["PS1"]

        # catching EOF error
        try:
            args = [str(n) for n in input(command_string).split()]
        except EOFError:
            sys.exit(1)

        # when empty, do nothing and continue
        if not args:
            continue

        # exit command
        elif args[0] == "exit":
            sys.exit(0)

        # change directories
        elif args[0] == "cd":
            try:
                if len(args) < 2:
                    raise NoArgumentsError
                elif len(args) > 2:
                    raise TooManyArgumentsError
                else:
                    os.chdir(args[1])
            except NoArgumentsError:
                os.write(2, "Error: Provide a directory".encode())
            except TooManyArgumentsError:
                os.write(2, "Error: Too many arguments".encode())
            except FileNotFoundError:
                os.write(2, ("Error: Directory %s not found\n" % args[1]).encode())

        # handle pipe
        elif "|" in args:
            pipe_command(args)

        # fork, exec, wait
        else:
            rc = os.fork()
            wait = True

            # handle background tasks (not working T^T)
            if "&" in args:
                args.remove("&")
                wait = False

            # fork failure
            if rc < 0:
                sys.exit(1)

            # child
            elif rc == 0:
                # executing commands
                execute_commands(args)
                sys.exit(0)

            # parent (forked ok)
            else:
                # process done
                if wait:
                    result = os.wait()
                    if result[1] != 0 and result[1] != 256:
                        os.write(2, ("Program terminated with exit code: %d\n" % result[1]).encode())


if __name__ == "__main__":
    shell()
