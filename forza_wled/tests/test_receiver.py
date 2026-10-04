import math
import struct
import unittest
from forza_wled import receiver


class ReceiverTests(unittest.TestCase):
    def packet(self, race=1, maximum=8000., idle=900., rpm=4000.):
        return struct.pack('<iIfff', race, 1234, maximum, idle, rpm) + bytes(324 - 20)

    def test_rpm_fraction(self):
        self.assertEqual(receiver.parse_forza(self.packet()), 0.5)
        self.assertIsNone(receiver.parse_forza(self.packet(race=0)))
        self.assertIsNone(receiver.parse_forza(self.packet()[:-1]))
        self.assertIsNone(receiver.parse_forza(self.packet(maximum=math.nan)))
        self.assertIsNone(receiver.parse_forza(self.packet(maximum=0)))

    def test_ddp_header_and_pixels(self):
        frame = receiver.make_frame(0.5, 300)
        self.assertEqual(frame[:10], struct.pack('!BBBBIH', 0x41, 0, 1, 1, 0, 900))
        self.assertEqual(len(frame), 910)
        self.assertNotEqual(frame[10:13], b'\0\0\0')
        self.assertEqual(frame[10 + 150 * 3:10 + 151 * 3], b'\0\0\0')
        self.assertEqual(receiver.make_frame(1., 300, True)[-3:], bytes((245, 0, 0)))
        full = receiver.make_frame(1., 300)
        self.assertEqual(full[10 + 165 * 3:10 + 166 * 3], bytes((0, 170, 12)))
        self.assertEqual(full[10 + 180 * 3:10 + 181 * 3], bytes((235, 115, 0)))
        self.assertEqual(full[10 + 230 * 3:10 + 231 * 3], bytes((245, 0, 0)))

    def test_physical_thresholds_are_configurable_without_changing_default(self):
        custom = receiver.make_frame(1., 10, green_until=0.3, amber_until=0.6)
        self.assertEqual(custom[10 + 2 * 3:10 + 3 * 3], bytes((0, 170, 12)))
        self.assertEqual(custom[10 + 4 * 3:10 + 5 * 3], bytes((235, 115, 0)))
        self.assertEqual(custom[10 + 7 * 3:10 + 8 * 3], bytes((245, 0, 0)))

if __name__ == '__main__':
    unittest.main()
