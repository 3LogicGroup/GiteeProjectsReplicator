# -*- coding: utf-8 -*-
# Author: Timur Gilmullin
# E-mail: tim55667757@gmail.com


"""
**Gitee Projects Replicator**, **GPReplicator** or **GPR** is the simple Python API for mirroring projects
from/to Chinese gitee.com to/from Russian gitee.ru or another git-repository as GitHub, GitLab etc.
Also, a mirrored project contains most important project artifacts: description, issues, milestones, releases and documentation.

Replication and synchronization worked throw HTTP API.v5 of Gitee service.

Also, GPReplicator can be used as a CLI manager to work with Gitee projects in the console.
For all examples, you will need to use the Gitee OAuth token.

Examples:

- 1
- 2
- 3

More CLI examples see in documentation:
- 🇷🇺 [In Russian](https://3logicgroup.github.io/GiteeProjectsReplicator/)
- 🇺🇸 [In English](https://github.com/3LogicGroup/GiteeProjectsReplicator/blob/master/README_EN.md)

See also:
- ⚙ [Documentation on GPReplicator class methods (for Python developers)]()
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
from typing import Optional, Union
from datetime import datetime, timedelta

from dateutil.tz import tzlocal
from argparse import ArgumentParser

import gpreplicator.UniLogger as uLog
import traceback as tb


# --- Common technical parameters:

uLogger = uLog.UniLogger
uLogger.level = 10  # debug level by default
uLogger.handlers[0].level = 10  # info level by default for STDOUT
uLogger.handlers[1].level = 10  # debug level by default for log.txt


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

        self.gAPIGateway = "https://gitee.ru/api/v5"
        """API gateway of Gitee service. Default: `https://gitee.ru/api/v5`"""

        self.gToken = None
        """Your API token at Gitee service. Default: `None`"""

        self.gOwner = None
        """Project owner on Gitee service. Default: `None`"""

        self.gProject = None
        """Project on Gitee service for mirroring. Default: `None`"""

    def ProjectFiles(self) -> dict:
        """
        Get project files.

        :return: dict with all project files objects.
        """
        files = {}

        uLogger.debug("Raw files tree data:")
        uLogger.debug(files)

        return files

    def Description(self) -> dict:
        """
        Get project description.

        :return: dict with project issues.
        """
        description = {}

        uLogger.debug("Raw description data:")
        uLogger.debug(description)

        return description

    def Issues(self) -> dict:
        """
        Get all project issues.

        :return: dict with project issues.
        """
        issues = {}

        uLogger.debug("Raw issues data:")
        uLogger.debug(issues)

        return issues

    def Milestones(self) -> dict:
        """
        Get all project milestones.

        :return: dict with project milestones.
        """
        milestones = {}

        uLogger.debug("Raw milestones data:")
        uLogger.debug(milestones)

        return milestones

    def Releases(self) -> dict:
        """
        Get all project published releases.

        :return: dict with project releases.
        """
        releases = {}

        uLogger.debug("Raw releases data:")
        uLogger.debug(releases)

        return releases


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

    parser.add_argument("--debug-level", "--verbosity", "-v", type=int, default=20, help="Option: showing STDOUT messages of minimal debug level, e.g., 10 = DEBUG, 20 = INFO, 30 = WARNING, 40 = ERROR, 50 = CRITICAL.")

    # commands:
    parser.add_argument("--files", "-f", action="store_true", help="Command: show Gitee project files.")
    parser.add_argument("--description", "-d", action="store_true", help="Command: show Gitee project description.")
    parser.add_argument("--issues", "-i", action="store_true", help="Command: show list of Gitee project issues.")
    parser.add_argument("--milestones", "-m", action="store_true", help="Command: show list of Gitee project milestones.")
    parser.add_argument("--releases", "-r", action="store_true", help="Command: show list of Gitee project releases.")

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
            projectModel.gAPIGatewayToken = args.gitee_gateway

        if args.gitee_token:
            projectModel.gToken = args.gitee_token

        if args.gitee_owner:
            projectModel.gOwner = args.gitee_owner

        if args.gitee_project:
            projectModel.gProject = args.gitee_project

        # --- do one or more commands:

        if args.files:
            projectModel.ProjectFiles()

        if args.description:
            projectModel.Description()

        if args.issues:
            projectModel.Issues()

        if args.milestones:
            projectModel.Milestones()

        if args.releases:
            projectModel.Releases()

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
