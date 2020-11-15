/*****************************************************************************
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
*****************************************************************************/


#pragma once


namespace PROTO {
	const uint8_t MAGIC			= 0x33;
	const uint16_t CRC_POLINOM	= 0xA001;

	namespace RESP { // Plain responses
		// const uint8_t OK =			0x20; // Legacy
		const uint8_t NONE =			0x24;
		const uint8_t CRC_ERROR =		0x40;
		const uint8_t INVALID_ERROR =	0x45;
		const uint8_t TIMEOUT_ERROR =	0x48;
	};

	namespace PONG { // Complex response
		const uint8_t PREFIX =				0x80;
		const uint8_t CAPS =				0b00000001;
		const uint8_t SCROLL =				0b00000010;
		const uint8_t NUM =					0b00000100;
		const uint8_t KEYBOARD_OFFLINE =	0b00001000;
		const uint8_t MOUSE_OFFLINE =		0b00010000;
	};

	namespace CMD {
		const uint8_t PING =		0x01;
		const uint8_t REPEAT =		0x02;
		const uint8_t RESET_HID =	0x10;

		namespace KEYBOARD {
			const uint8_t KEY =	0x11;
		};

		namespace MOUSE {
			const uint8_t MOVE =	0x12;
			const uint8_t BUTTON =	0x13;
			const uint8_t WHEEL =	0x14;
			namespace LEFT {
				const uint8_t SELECT =	0b10000000;
				const uint8_t STATE =	0b00001000;
			};
			namespace RIGHT {
				const uint8_t SELECT =	0b01000000;
				const uint8_t STATE =	0b00000100;
			};
			namespace MIDDLE {
				const uint8_t SELECT =	0b00100000;
				const uint8_t STATE =	0b00000010;
			};
			namespace EXTRA_UP {
				const uint8_t SELECT =	0b10000000;
				const uint8_t STATE =	0b00001000;
			};
			namespace EXTRA_DOWN {
				const uint8_t SELECT =	0b01000000;
				const uint8_t STATE =	0b00000100;
			};
		};
	};
};


uint16_t protoCrc16(const uint8_t *buffer, unsigned length) {
	uint16_t crc = 0xFFFF;

	for (unsigned byte_count = 0; byte_count < length; ++byte_count) {
		crc = crc ^ buffer[byte_count];
		for (unsigned bit_count = 0; bit_count < 8; ++bit_count) {
			if ((crc & 0x0001) == 0) {
				crc = crc >> 1;
			} else {
				crc = crc >> 1;
				crc = crc ^ PROTO::CRC_POLINOM;
			}
		}
	}
	return crc;
}
