# ========================================================================== #
#                                                                            #
#    KVMD - The main PiKVM daemon.                                           #
#                                                                            #
#    Copyright (C) 2018-2022  Maxim Devaev <mdevaev@gmail.com>               #
#                                                                            #
#    This program is free software: you can redistribute it and/or modify    #
#    it under the terms of the GNU General Public License as published by    #
#    the Free Software Foundation, either version 3 of the License, or       #
#    (at your option) any later version.                                     #
#                                                                            #
#    This program is distributed in the hope that it will be useful,         #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#    GNU General Public License for more details.                            #
#                                                                            #
#    You should have received a copy of the GNU General Public License       #
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                            #
# ========================================================================== #


import sys
import os
import asyncio
import asyncio.subprocess
import argparse

from typing import List
from typing import Optional

import aiohttp

from ...logging import get_logger

from ... import aiotools
from ... import aioproc
from ... import htclient
from ... import htserver

from .. import init


# =====
async def _run_cmd_ws(cmd: List[str], ws: aiohttp.ClientWebSocketResponse) -> int:  # pylint: disable=too-many-branches
    logger = get_logger(0)
    receive_task: Optional[asyncio.Task] = None
    proc_task: Optional[asyncio.Task] = None
    proc: Optional[asyncio.subprocess.Process] = None  # pylint: disable=no-member
    retval = 1
    try:  # pylint: disable=too-many-nested-blocks
        while True:
            if receive_task is None:
                receive_task = asyncio.create_task(ws.receive())
            if proc_task is None and proc is not None:
                proc_task = asyncio.create_task(proc.wait())

            tasks = list(filter(None, [receive_task, proc_task]))
            done = (await aiotools.wait_first(*tasks))[0]

            if receive_task in done:
                msg = receive_task.result()
                if msg.type == aiohttp.WSMsgType.TEXT:
                    (event_type, event) = htserver.parse_ws_event(msg.data)
                    if event_type == "storage_state":
                        if event["data"]["write_allowed"] and proc is None:
                            proc = (await asyncio.create_subprocess_exec(
                                *cmd,
                                preexec_fn=os.setpgrp,
                                env={"KVMD_PST_DATA": event["data"]["path"]},
                            ))
                        elif not event["data"]["write_allowed"]:
                            logger.error("PST write is not allowed")
                            break
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    logger.error("PST connection closed")
                    break
                else:
                    logger.error("Unknown PST message type: %r", msg)
                    break
                receive_task = None

            if proc_task in done:
                assert proc is not None
                assert proc.returncode is not None
                logger.info("Process finished: returncode=%s", proc.returncode)
                break

    finally:
        if receive_task:
            receive_task.cancel()
        if proc_task:
            proc_task.cancel()
        if proc is not None:
            await aioproc.kill_process(proc, 1, logger)
            assert proc.returncode is not None
            retval = proc.returncode
    return retval


async def _run_cmd(cmd: List[str], unix_path: str) -> None:
    async with aiohttp.ClientSession(
        headers={"User-Agent": htclient.make_user_agent("KVMD-PSTRun")},
        connector=aiohttp.UnixConnector(path=unix_path),
        timeout=aiohttp.ClientTimeout(total=5),
    ) as session:
        async with session.ws_connect("http://localhost:0/ws") as ws:
            sys.exit(await _run_cmd_ws(cmd, ws))


# =====
def main(argv: Optional[List[str]]=None) -> None:
    (parent_parser, argv, config) = init(
        add_help=False,
        argv=argv,
    )
    parser = argparse.ArgumentParser(
        prog="kvmd-pstrun",
        description="Request the access to KVMD persistent storage and run the script",
        parents=[parent_parser],
    )
    parser.add_argument("cmd", nargs="+", help="Script with arguments to run")
    options = parser.parse_args(argv[1:])
    aiotools.run(_run_cmd(options.cmd, config.pst.server.unix))