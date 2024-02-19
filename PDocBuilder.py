# -*- coding: utf-8 -*-
# Author: Timur Gilmullin

"""
A coroutine that generates the API documentation for the GPReplicator module using pdoc-engine: https://pdoc.dev/docs/pdoc.html

To build new documentation:
1. Remove the `./docs` directory from the repository root.
2. Go to the root of the repository.
3. Just run: `python PDocBuilder.py`.
"""


import os
import sys
import pdoc
from pathlib import Path


curdir = os.path.curdir

sys.path.extend([
    curdir,
    os.path.abspath(os.path.join(curdir, "gpreplicator")),
])

pdoc.render.configure(
    docformat="restructuredtext",
    favicon="https://3logic.ru/local/templates/corporate.static/inc/favicon/apple-touch-icon.png",
    footer_text="Gitee Projects Replicator is the simple Python API for mirroring projects from/to Chinese gitee.com and Russian gitee.ru",
    logo="https://www.tadviser.ru/images/b/ba/3LOGIC_GROUP.png",
    show_source=False,
    template_directory=Path("docs", "templates").resolve(),
)
pdoc.pdoc(
    Path("gpreplicator").resolve(),
    output_directory=Path("docs").resolve(),
)
