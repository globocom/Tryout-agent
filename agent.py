# -*- encoding: utf-8 -*-

import os
import subprocess

import settings
import git
import requests


def clone_challenge(challenge_repository, challenge_name):
    try:
        git.Git().clone(challenge_repository)
        if not os.path.exists(challenge_name):
            return "Can't download this repository", True
    except git.GitCommandError:
        pass
    return '', False


def _run_make_command(challenge_name, make_parameter, background=False):
    make_command = ["make", "-C", "{directory}".format(directory=challenge_name), make_parameter]
    try:
        if background:
            bg_process = subprocess.Popen(make_command, stdin=None, stdout=None, stderr=None)
            if bg_process.returncode != 0:
                bg_process.kill()
        else:
            output = subprocess.check_output(make_command, stderr=subprocess.STDOUT)
            return output, False
    except Exception as e:
        return "Have a error in make {parameter} error: {error}".format(parameter=make_parameter, error=e), True


def run_make_setup(challenge_name):
    return _run_make_command(challenge_name, "setup")


def run_make_run(challenge_name):
    return _run_make_command(challenge_name, "run", background=True)


def send_status(challenge_name, status_json):
    requests.post(settings.API_URL, status_json)


def main():
    status_json = dict()
    challenge_repository = os.environ.get("REPO")
    challenge_name = challenge_repository.split('/')[-1].replace('.git', '')

    msg, error = clone_challenge(challenge_repository, challenge_name)
    if error:
        status_json['clone_error'] = msg
        return

    msg, setup_error = run_make_setup(challenge_name)
    status_json['setup_output'] = msg
    if setup_error:
        return

    run_make_run(challenge_name)

    send_status(challenge_name, status_json)

if __name__ == '__main__':
    status = main()
