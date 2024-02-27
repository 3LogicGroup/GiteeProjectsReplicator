# -*- coding: utf-8 -*-
# Author: Timur Gilmullin
# E-mail: tim55667757@gmail.com


"""
**Gitee Projects Replicator**, **GPReplicator** or **GPR** is the simple Python API for mirroring projects
from/to Chinese gitee.com and Russian gitee.ru or another git-repository as GitHub, GitLab etc.
Also, a mirrored project contains most important project artifacts: description, issues, milestones, releases and documentation.

Replication and synchronization worked throw HTTP API.v5 of Gitee service.

See also:
- 📚 [Main documentation with examples](https://github.com/3LogicGroup/GiteeProjectsReplicator/blob/master/README_EN.md)
- ⚙ [Documentation on GPReplicator class methods (for Python developers)](https://3logicgroup.github.io/GiteeProjectsReplicator/docs/gpreplicator/GPReplicator.html)

Also, GPReplicator can be used as a CLI manager to work with Gitee projects in the console.
For all examples, you will need to use the [Gitee OAuth token](https://gitee.com/api/v5/oauth_doc).

Examples:

- Get and show project tree files recursively (also replace API gateway for Chinese service):

  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "your_token" -go "project_group_owner" -gp "repository_name" --gitee-recursive --files`

  Example:

  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "token" -go tim55667757 -gp PriceGenerator --files`

- Get and show project releases:

  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "token" -go "owner" -gp "repository" --releases`

- Get and show project issues:

  `python3 GPReplicator.py -v 10 -gg https://gitee.ru/api/v5 -gt "token" -go "owner" -gp "repository" --issues`

More CLI examples see in documentation:
- 🇷🇺 [In Russian](https://3logicgroup.github.io/GiteeProjectsReplicator)
- 🇺🇸 [In English](https://github.com/3LogicGroup/GiteeProjectsReplicator/blob/master/README_EN.md)
"""


# Copyright (c) 2024 Gilmillin Timur Mansurovich
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
from datetime import datetime, timedelta

import json
import requests

from dateutil.tz import tzlocal
from time import sleep
from argparse import ArgumentParser

import gpreplicator.UniLogger as uLog
import traceback as tb

from multiprocessing import cpu_count, Lock
from multiprocessing.pool import ThreadPool


# --- Common technical parameters:

uLogger = uLog.UniLogger
uLogger.level = 10  # debug level by default
uLogger.handlers[0].level = 10  # info level by default for STDOUT
uLogger.handlers[1].level = 10  # debug level by default for log.txt

CPU_COUNT = cpu_count()  # host's real CPU count
CPU_USAGES = CPU_COUNT - 1 if CPU_COUNT > 1 else 1  # how many CPUs will be used for parallel calculations


class GiteeTransport:
    """
    This class implements methods to work with Gitee HTTP API service.

    - Russian Gitee service: https://gitee.ru
      - Russian service API gateway: https://gitee.ru/api/v5
      - Russian service swagger documentation: https://gitee.ru/api/v5/swagger
    - Chinese Gitee service: https://gitee.com
      - Chinese service API gateway: https://gitee.com/api/v5
      - Chinese service swagger documentation: https://gitee.com/api/v5/swagger

    Examples to work with API:
    - https://gitee.ru/api/v5/swagger
    - https://gitee.com/api/v5/swagger

    About `gToken` for Gitee OAuth:
    - https://gitee.ru/api/v5/oauth_doc
    - https://gitee.com/api/v5/oauth_doc
    """

    def __init__(self):
        """Main class init."""

        self.__lock = Lock()  # initialize multiprocessing mutex lock

        self.gAPIGateway = "https://gitee.ru/api/v5"
        """API gateway of Gitee service. Default: `https://gitee.ru/api/v5`"""

        self.timeout = 15
        """Server operations timeout in seconds. Default: `15`."""

        self.retry = 3
        """
        How many times retry after first request if a 5xx server errors occurred. If set to 0, then only first main
        request will be sent without retries. This allows you to reduce the number of calls to the server API for all methods.

        3 times of retries by default.
        """

        self.pause = 5
        """Sleep time in seconds between retries, in all network requests 5 seconds by default."""

        self.headers = {
            "Content-Type": "application/json",
            "charset": "UTF-8",
            "accept": "application/json",
            "x-app-name": "3LogicGroup.GPReplicator",
        }
        """
        Headers which send in every request to broker server.

        Default: `{"Content-Type": "application/json", "charset": "UTF-8", "accept": "application/json", "x-app-name": "3LogicGroup.GPReplicator"}`.
        """

        self.body = None
        """Request body which send to broker server. Default: `None`."""

        self.gToken = None
        """
        Your API token at Gitee service.

        You can also use the environment variable `GITEE_TOKEN` or the key `--gitee-token` to define this parameter.
        
        Default: `None`.
        """

        try:
            self.gToken = r"{}".format(os.environ["GITEE_TOKEN"])
            uLogger.debug("API token for Gitee service set up from environment variable `GITEE_TOKEN`")

        except KeyError:
            uLogger.debug("Environment variable `GITEE_TOKEN` is empty. So you can use the variable `gToken` or the key `--gitee-token` to define it.")

        self.gOwner = None
        """
        Project owner on Gitee service. This is the space name to which the repository belongs (name of enterprise, organization or individual.

        You can also use the environment variable `GITEE_OWNER` or the key `--gitee-owner` to define this parameter.

        Default: `None`.
        """

        try:
            self.gOwner = r"{}".format(os.environ["GITEE_OWNER"])
            uLogger.debug("Space name for Gitee service set up from environment variable `GITEE_OWNER`")

        except KeyError:
            uLogger.debug("Environment variable `GITEE_OWNER` is empty. So you can use the variable `gOwner` or the key `--gitee-owner` to define it.")

        self.gProject = None
        """
        Project or repository name on Gitee service for mirroring.

        You can also use the environment variable `GITEE_PROJECT` or the key `--gitee-project` to define this parameter.

        Default: `None`.
        """

        try:
            self.gProject = r"{}".format(os.environ["GITEE_PROJECT"])
            uLogger.debug("Project name for Gitee service set up from environment variable `GITEE_PROJECT`")

        except KeyError:
            uLogger.debug("Environment variable `GITEE_PROJECT` is empty. So you can use the variable `gProject` or the key `--gitee-project` to define it.")

        self.gSHA = None
        """It can be the branch name (such as master), commit or the SHA value, which you are interested in. It used in some class methods. Default: `None`"""

        self.gRecursive = False
        """You can set this variable to `True` if you want to receive data from Gitee service recursively. It used in some class methods. Default: `False`"""

        self.moreDebug = False
        """Enables more debug information in this class, such as net request/response body and headers in all methods. `False` by default."""

    def _ParseJSON(self, rawData="{}") -> dict:
        """
        Support function: parse JSON from response string.

        :param rawData: this is a string with JSON-formatted text.
        :return: JSON (dictionary), parsed from server response string. If an error occurred, then return empty dict `{}`.
        """
        try:
            responseJSON = json.loads(rawData) if rawData else {}

            if self.moreDebug:
                uLogger.debug("JSON-data of raw response body:\n{}".format(json.dumps(responseJSON, indent=4)))

            return responseJSON

        except Exception as e:
            uLogger.debug(tb.format_exc())
            uLogger.error("An empty dict will be return, because an error occurred in `_ParseJSON()` method with comment: {}".format(e))

            return {}

    def SendAPIRequest(self, url: str, reqType: str = "GET"):
        """
        Send GET or POST request to API server and receive JSON object.

        self.header: dictionary of headers.
        self.body: request body. `None` by default.
        self.timeout: global request timeout, `15` seconds by default.
        :param url: url with REST request.
        :param reqType: send "GET" or "POST" request. `"GET"` by default.
        :return: response JSON (list, dictionary or list of dictionaries).
        """
        if reqType.upper() not in ("GET", "POST"):
            uLogger.error("You can define request type: `GET` or `POST`!")
            raise Exception("Incorrect value")

        if self.moreDebug:
            uLogger.debug("Request parameters:")
            uLogger.debug("    - REST API URL: {}".format(url))
            uLogger.debug("    - request type: {}".format(reqType))
            uLogger.debug("    - headers:\n{}".format(str(self.headers)))
            uLogger.debug("    - raw request body:\n{}".format(self.body))

        with self.__lock:  # acquire the mutex lock
            counter = 0
            response = None
            errMsg = ""

            while not response and counter <= self.retry:
                if reqType == "GET":
                    response = requests.get(url, headers=self.headers, data=self.body, timeout=self.timeout)

                if reqType == "POST":
                    response = requests.post(url, headers=self.headers, data=self.body, timeout=self.timeout)

                if self.moreDebug:
                    uLogger.debug("Response:")
                    uLogger.debug("    - status code: {}".format(response.status_code))
                    uLogger.debug("    - reason: {}".format(response.reason))
                    uLogger.debug("    - body length: {}".format(len(response.text)))
                    uLogger.debug("    - headers:\n{}".format(response.headers))

                # Server returns some headers:
                # - `x-ratelimit-limit` — shows the settings of the current user limit for this method.
                # - `x-ratelimit-remaining` — the number of remaining requests of this type per minute.
                # - `x-ratelimit-reset` — time in seconds before resetting the request counter.
                # if "x-ratelimit-remaining" in response.headers.keys() and response.headers["x-ratelimit-remaining"] == "0":
                #     rateLimitWait = int(response.headers["x-ratelimit-reset"])
                #     uLogger.debug("Rate limit exceeded. Waiting {} sec. for reset rate limit and then repeat...".format(rateLimitWait))
                #     sleep(rateLimitWait)

                # Error status codes: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
                if 400 <= response.status_code < 500:
                    msg = "status code: [{}], response body: {}".format(response.status_code, response.text)
                    uLogger.debug("    - not oK, but do not retry for 4xx errors, {}".format(msg))

                    if "code" in response.text and "message" in response.text:
                        msgDict = self._ParseJSON(rawData=response.text)
                        uLogger.debug("HTTP-status code [{}], server message: {}".format(response.status_code, msgDict["message"]))

                    counter = self.retry + 1  # do not retry for 4xx errors

                if 500 <= response.status_code < 600:
                    errMsg = "status code: [{}], response body: {}".format(response.status_code, response.text)
                    uLogger.debug("    - not oK, {}".format(errMsg))

                    if "code" in response.text and "message" in response.text:
                        errMsgDict = self._ParseJSON(rawData=response.text)
                        uLogger.debug("HTTP-status code [{}], error message: {}".format(response.status_code, errMsgDict["message"]))

                    counter += 1

                    if counter <= self.retry:
                        uLogger.debug("Retry: [{}]. Wait {} sec. and try again...".format(counter, self.pause))
                        sleep(self.pause)

            responseJSON = self._ParseJSON(rawData=response.text)

            if errMsg:
                uLogger.error("Server returns not `oK` status! See full debug log.")
                uLogger.error("    - not oK, {}".format(errMsg))

        return responseJSON

    def Files(self) -> dict:
        """
        Get all project files.

        All the variables: `gOwner`, `gProject` and `gSHA` must be defined for using this method!

        `gSHA` can be the branch name (such as master), commit or the SHA value, which you are interested in.

        Also, you can set the `gRecursive` variable to `True` if you want to receive all tree files in all directories recursively.

        :return: dictionary with user's portfolio data.
        """
        if self.gOwner is None or not self.gOwner or self.gProject is None or not self.gProject or self.gSHA is None or not self.gSHA:
            uLogger.error("All the variables: `gOwner`, `gProject` and `gSHA` must be defined for using `Files()` method!")
            raise Exception("Some parameters are required")

        uLogger.debug("Requesting all project files. Wait, please...")

        projectFilesURL = self.gAPIGateway + f"/repos/{self.gOwner}/{self.gProject}/git/trees/{self.gSHA}?recursive={1 if self.gRecursive else 0}"
        projectFiles = self.SendAPIRequest(projectFilesURL, reqType="GET")

        if projectFiles is not None and isinstance(projectFiles, dict) and "tree" in projectFiles.keys():
            count = len(projectFiles['tree'])

            if self.moreDebug:
                uLogger.debug(f"Project files data successfully received. Records: [{count}]")

            if count:
                info = []

                for item in projectFiles['tree']:
                    info.append("|-> " + item['path'] + f"{'' if item['type'] != 'tree' else '/'}")

                infoText = f"{'List of all project files' if self.gRecursive else 'List of project files in root directory'} [{count}]:\n. {self.gProject} repository\n" + "\n".join(sorted(info))

                uLogger.info(infoText)

        return projectFiles

    def Issues(self) -> dict:
        """
        Get all project issues.

        All the variables: `gOwner` and `gProject` must be defined for using this method!

        :return: dict with all issues data.
        """
        if self.gOwner is None or not self.gOwner or self.gProject is None or not self.gProject:
            uLogger.error("All the variables: `gOwner` and `gProject` must be defined for using `Issues()` method!")
            raise Exception("Some parameters are required")

        uLogger.debug("Requesting all project issues. Wait, please...")

        issuesURL = self.gAPIGateway + f"/repos/{self.gOwner}/{self.gProject}/issues?state=all"
        issues = self.SendAPIRequest(issuesURL, reqType="GET")

        count = len(issues)
        if issues is not None and isinstance(issues, list) and count:
            if self.moreDebug:
                uLogger.debug(f"Project issues data successfully received. Records: [{count}]")

            info = []

            for item in issues:
                info.append(f"State: [{item['state']}] Type: [{item['issue_type']}] Created: [{item['created_at'].split('T')[0]}] Title: [{item['title']}]{' Milestone: [' + item['milestone']['title'] + ']' if item['milestone'] else ''}")

            infoText = f"{'List of all project issues'} [{count}]:\n" + "\n".join(sorted(info))

            uLogger.info(infoText)

        else:
            uLogger.info("There are no project issues")

        return issues

    def Milestones(self) -> list[dict]:
        """
        Get all project milestones.

        All the variables: `gOwner` and `gProject` must be defined for using this method!

        :return: list of dict with milestones data.
        """
        if self.gOwner is None or not self.gOwner or self.gProject is None or not self.gProject:
            uLogger.error("All the variables: `gOwner` and `gProject` must be defined for using `Milestones()` method!")
            raise Exception("Some parameters are required")

        uLogger.debug("Requesting all project milestones. Wait, please...")

        milestonesURL = self.gAPIGateway + f"/repos/{self.gOwner}/{self.gProject}/milestones"
        milestones = self.SendAPIRequest(milestonesURL, reqType="GET")

        count = len(milestones)
        if milestones is not None and isinstance(milestones, list) and count:
            if self.moreDebug:
                uLogger.debug(f"Project milestones data successfully received. Records: [{count}]")

            info = []

            for item in milestones:
                info.append(f"State: [{item['state']}] Created: [{item['created_at'].split('T')[0]}] Deadline: [{item['due_on'].split('T')[0]}] Title: [{item['title']}] Open/Closed issues: [{item['open_issues']}/{item['closed_issues']}]")

            infoText = f"{'List of all project milestones'} [{count}]:\n" + "\n".join(sorted(info))

            uLogger.info(infoText)

        else:
            uLogger.info("There are no project milestones")

        return milestones

    def Releases(self) -> list[dict]:
        """
        Get all project published releases data.

        All the variables: `gOwner` and `gProject` must be defined for using this method!

        :return: list of dict with releases.
        """
        if self.gOwner is None or not self.gOwner or self.gProject is None or not self.gProject:
            uLogger.error("All the variables: `gOwner` and `gProject` must be defined for using `Releases()` method!")
            raise Exception("Some parameters are required")

        uLogger.debug("Requesting all project releases. Wait, please...")

        releasesURL = self.gAPIGateway + f"/repos/{self.gOwner}/{self.gProject}/releases"
        releases = self.SendAPIRequest(releasesURL, reqType="GET")

        count = len(releases)
        if releases is not None and isinstance(releases, list) and count:
            if self.moreDebug:
                uLogger.debug(f"Project releases data successfully received. Records: [{count}]")

            info = []

            for item in releases:
                info.append(f"Created: [{item['created_at'].split('T')[0]}] Tag: [{item['tag_name']}] Release name: [{item['name']}]{' [Pre-release]' if item['prerelease'] else ''}")

            infoText = f"{'List of all project releases'} [{count}]:\n" + "\n".join(sorted(info))

            uLogger.info(infoText)

        else:
            uLogger.info("There are no project releases")

        return releases

    def Tags(self) -> list[dict]:
        """
        Get all project tags.

        All the variables: `gOwner` and `gProject` must be defined for using this method!

        :return: list of dict with project tags.
        """
        if self.gOwner is None or not self.gOwner or self.gProject is None or not self.gProject:
            uLogger.error("All the variables: `gOwner` and `gProject` must be defined for using `Tags()` method!")
            raise Exception("Some parameters are required")

        uLogger.debug("Requesting project tags. Wait, please...")

        tagsURL = self.gAPIGateway + f"/repos/{self.gOwner}/{self.gProject}/tags"
        tags = self.SendAPIRequest(tagsURL, reqType="GET")

        count = len(tags)
        if tags is not None and isinstance(tags, list) and count:
            if self.moreDebug:
                uLogger.debug(f"Project tags data successfully received. Records: [{count}]")

            info = []

            for item in tags:
                info.append(f"Created: [{item['commit']['date'].split('T')[0]}] Name: [{item['name']}]")

            infoText = f"{'List of all project tags'} [{count}]:\n" + "\n".join(sorted(info))

            uLogger.info(infoText)

        else:
            uLogger.info("There are no project tags")

        return tags


class GPReplicator(GiteeTransport):
    def __init__(self):
        super().__init__()


def ParseArgs():
    """This function get and parse command line keys."""
    parser = ArgumentParser()  # command-line string parser

    parser.description = "Gitee Projects Replicator (GPReplicator or GPR) is the simple Python API for mirroring projects from/to Chinese gitee.com to/from Russian gitee.ru or another git-repository as GitHub, GitLab etc. Also, mirrored project contains most important project artifacts: description, issues, milestones, releases and documentation."
    parser.usage = "\n/as module/ python GPReplicator.py [some options] [one command]\n/as CLI tool/ gpreplicator [some options] [one command]"

    # options:
    parser.add_argument("--gitee-gateway", "-gg", type=str, help="Option: API gateway of Gitee service.")

    parser.add_argument("--gitee-token", "-gt", type=str, help="Option: your API token on Gitee service.")
    parser.add_argument("--gitee-owner", "-go", type=str, help="Option: project owner on Gitee service.")
    parser.add_argument("--gitee-project", "-gp", type=str, help="Option: project on Gitee service for mirroring.")
    parser.add_argument("--gitee-sha", "-gs", "-gsha", type=str, help="Option: it can be the branch name (such as master), commit or the SHA value, which you are interested in.")
    parser.add_argument("--gitee-recursive", "-gr", action="store_true", help="Option: You can set this flag if you want to receive data from Gitee service recursively.")

    parser.add_argument("--debug-level", "--verbosity", "-v", type=int, default=20, help="Option: showing STDOUT messages of minimal debug level, e.g., 10 = DEBUG, 20 = INFO, 30 = WARNING, 40 = ERROR, 50 = CRITICAL.")

    # commands:
    parser.add_argument("--files", "-f", action="store_true", help="Command: show Gitee project files.")
    parser.add_argument("--issues", "-i", action="store_true", help="Command: show list of Gitee project issues.")
    parser.add_argument("--milestones", "-m", action="store_true", help="Command: show list of Gitee project milestones.")
    parser.add_argument("--releases", "-r", action="store_true", help="Command: show list of Gitee project releases.")
    parser.add_argument("--tags", "-t", action="store_true", help="Command: show list of Gitee project tags.")

    cmdArgs = parser.parse_args()
    return cmdArgs


def Main():
    """
    Main function for work with GPReplicator in the console.

    See examples:
    - 🇷🇺 [In Russian](https://3logicgroup.github.io/GiteeProjectsReplicator/)
    - 🇺🇸 [In English](https://github.com/3LogicGroup/GiteeProjectsReplicator/blob/master/README_EN.md)
    """
    args = ParseArgs()  # get and parse command-line parameters
    exitCode = 0

    if args.debug_level:
        uLogger.level = 10  # always debug level by default
        uLogger.handlers[0].level = args.debug_level  # level for STDOUT
        uLogger.handlers[1].level = 10  # always debug level for log.txt

    start = datetime.now(tzlocal())
    uLogger.debug(uLog.sepLine)
    uLogger.debug("GPReplicator started: {}".format(start.strftime("%Y-%m-%d %H:%M:%S")))

    projectModel = GPReplicator()

    try:
        # --- set options:

        if args.gitee_gateway:
            projectModel.gAPIGateway = args.gitee_gateway

        if args.gitee_token:
            projectModel.gToken = args.gitee_token

        if args.gitee_owner:
            projectModel.gOwner = args.gitee_owner

        if args.gitee_project:
            projectModel.gProject = args.gitee_project

        if args.gitee_sha:
            projectModel.gSHA = args.gitee_sha

        if args.gitee_recursive is not None:
            projectModel.gRecursive = args.gitee_recursive

        # --- do one or more commands:

        if args.files:
            projectModel.Files()

        if args.issues:
            projectModel.Issues()

        if args.milestones:
            projectModel.Milestones()

        if args.releases:
            projectModel.Releases()

        if args.tags:
            projectModel.Tags()

    except Exception as e:
        uLogger.error(e)
        exc = tb.format_exc().split("\n")

        for line in exc:
            if line:
                uLogger.debug(line)

        exitCode = 255

    finally:
        finish = datetime.now(tzlocal())

        if exitCode == 0:
            uLogger.debug("All GPReplicator operations are finished success (summary code is 0).")

        else:
            uLogger.error("An errors occurred during the work! See full debug log with --debug-level 10. Summary code: {}".format(exitCode))

        uLogger.debug("GPReplicator work duration: {}".format(finish - start))
        uLogger.debug("GPReplicator work finished: {}".format(finish.strftime("%Y-%m-%d %H:%M:%S")))

        sys.exit(exitCode)


if __name__ == "__main__":
    Main()
