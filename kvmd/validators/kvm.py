# ========================================================================== #
#                                                                            #
#    KVMD - The main Pi-KVM daemon.                                          #
#                                                                            #
#    Copyright (C) 2018  Maxim Devaev <mdevaev@gmail.com>                    #
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


import re

from typing import Any

from .. import keymap

from . import check_not_none_string
from . import check_string_in_list

from .basic import valid_number


# =====
def valid_atx_power_action(arg: Any) -> str:
    return check_string_in_list(arg, "ATX power action", ["on", "off", "off_hard", "reset_hard"])


def valid_atx_button(arg: Any) -> str:
    return check_string_in_list(arg, "ATX button", ["power", "power_long", "reset"])


def valid_msd_image_name(arg: Any) -> str:
    if len(str(arg).strip()) == 0:
        arg = None
    arg = check_not_none_string(arg, "MSD image name", strip=True)
    arg = re.sub(r"[^\w\.+@()\[\]-]", "_", arg)
    if arg == ".":
        arg = "_"
    if arg == "..":
        arg = "__"
    return arg[:255]


def valid_log_seek(arg: Any) -> int:
    return int(valid_number(arg, min=0, name="log seek"))


def valid_stream_quality(arg: Any) -> int:
    return int(valid_number(arg, min=1, max=100, name="stream quality"))


def valid_stream_fps(arg: Any) -> int:
    return int(valid_number(arg, min=0, max=120, name="stream FPS"))


# =====
def valid_hid_key(arg: Any) -> str:
    return check_string_in_list(arg, "HID key", keymap.KEYMAP, lower=False)


def valid_hid_mouse_move(arg: Any) -> int:
    arg = valid_number(arg, name="HID mouse move")
    return min(max(-32768, arg), 32767)


def valid_hid_mouse_button(arg: Any) -> str:
    return check_string_in_list(arg, "HID mouse button", ["left", "right"])


def valid_hid_mouse_wheel(arg: Any) -> int:
    arg = valid_number(arg, name="HID mouse wheel")
    return min(max(-128, arg), 127)
