#! /usr/bin/env python3
# main.py
# 2022-12-23
# @ekivemark
#
# Import mtls Bundles to HAPI
# Assumptions: Dockerized HAPI is running on Port 8080
# Point to HAPI via BASE_URI

import os
import argparse
import random
import string
import subprocess
from icecream import ic
from bundle_handler import bundle_seq_load, remove_dead_records
from settings import BUNDLE_FOLDER, DEFAULT_REPO

GROUP_ID = ""

CLI = argparse.ArgumentParser()

CLI.add_argument(
    "--git_repo_uri",
    nargs=1,
    required=False,
    default=[DEFAULT_REPO],
    type=str,  # any type/callable can be used here
    help="URL to the git repo holding mTLS bundles"
)
CLI.add_argument(
    "--git_temp_target",
    nargs=1,
    required=False,
    type=str,  # any type/callable can be used here
    help="folder location to git clone into"
)
CLI.add_argument(
    "--clone",
    nargs=1,
    required=False,
    type=str,  # any type/callable can be used here
    default=["True"],
    help="Clone = True | False. If False provide --git_temp_target"
)



def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def clean_string(input):
    # remove dangerous characters from input string

    remove = ["|", ">", "<"]
    cleaned = input
    for r in remove:
        cleaned = cleaned.replace(r, "")
        # ic(cleaned)
    return cleaned


if __name__ == "__main__":
    args = CLI.parse_args()
    git_repo = clean_string(args.git_repo_uri[0])
    clone_it = clean_string(args.clone[0])
    if clone_it.lower() == "false":
        clone = False
    else:
        clone = True
    target_dir = ""
    try:
        target_dir = clean_string(args.git_temp_target[0])
    except TypeError:
        target_dir = "./tmp/" + id_generator()

    ic(target_dir)
    if target_dir == "":
        target_dir = "./tmp/" + id_generator()
    ic(git_repo, target_dir)
    if clone:
        cmd = subprocess.call(["mkdir", target_dir])
        git_command = "git clone " + git_repo + " " + target_dir
        ic(git_command)
        cmd = subprocess.call(["git", "clone", git_repo, target_dir])

        ic(cmd)

    bundles = os.listdir(target_dir + BUNDLE_FOLDER)
    ic(bundles)
    processed_bundle = bundle_seq_load(bundles, path=target_dir + BUNDLE_FOLDER)
    print(f"Processed Records:{processed_bundle}")
    # result = remove_dead_records(processed_bundle)

    # print(f"Removed Records:{result}")
    print("Done.")
