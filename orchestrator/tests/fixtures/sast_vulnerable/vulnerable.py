import os
def run_command(cmd):
    os.system(cmd)  # B605/B607: Possible shell injection or dangerous system call
