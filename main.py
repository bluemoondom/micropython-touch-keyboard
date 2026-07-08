from machine import Pin, SPI, PWM, I2C
import framebuf
import time
import math
import struct
import micropython
from array import array

DC   = 8
CS   = 9
SCK  = 10
MOSI = 11
RST  = 13
BL   = 25
I2C_SDA = 6
I2C_SCL = 7
TP_INT  = 21
TP_RST  = 22


class LCD_1inch28(framebuf.FrameBuffer):
    def __init__(self):
        self.width  = 240
        self.height = 240
        self.cs  = Pin(CS,  Pin.OUT)
        self.rst = Pin(RST, Pin.OUT) 
        self.cs(1)
        self.spi = SPI(1, 100_000_000, polarity=0, phase=0,
                       sck=Pin(SCK), mosi=Pin(MOSI), miso=None)
        self.dc = Pin(DC, Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(240 * 240 * 2)
        super().__init__(self.buffer, 240, 240, framebuf.RGB565)
        self.init_display()
        self.fill(0)
        self.show()
        self.pwm = PWM(Pin(BL))
        self.pwm.freq(5000)

    def write_cmd(self, cmd):
        self.cs(1); self.dc(0); self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1); self.dc(1); self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def set_bl_pwm(self, duty):
        self.pwm.duty_u16(duty)

    def init_display(self):
        self.rst(1); time.sleep(0.01)
        self.rst(0); time.sleep(0.01)
        self.rst(1); time.sleep(0.05)
        self.write_cmd(0xEF)
        self.write_cmd(0xEB); self.write_data(0x14)
        self.write_cmd(0xFE); self.write_cmd(0xEF)
        self.write_cmd(0xEB); self.write_data(0x14)
        self.write_cmd(0x84); self.write_data(0x40)
        self.write_cmd(0x85); self.write_data(0xFF)
        self.write_cmd(0x86); self.write_data(0xFF)
        self.write_cmd(0x87); self.write_data(0xFF)
        self.write_cmd(0x88); self.write_data(0x0A)
        self.write_cmd(0x89); self.write_data(0x21)
        self.write_cmd(0x8A); self.write_data(0x00)
        self.write_cmd(0x8B); self.write_data(0x80)
        self.write_cmd(0x8C); self.write_data(0x01)
        self.write_cmd(0x8D); self.write_data(0x01)
        self.write_cmd(0x8E); self.write_data(0xFF)
        self.write_cmd(0x8F); self.write_data(0xFF)
        self.write_cmd(0xB6); self.write_data(0x00); self.write_data(0x20)
        self.write_cmd(0x36); self.write_data(0x98)
        self.write_cmd(0x3A); self.write_data(0x05)
        self.write_cmd(0x90)
        self.write_data(0x08); self.write_data(0x08)
        self.write_data(0x08); self.write_data(0x08)
        self.write_cmd(0xBD); self.write_data(0x06)
        self.write_cmd(0xBC); self.write_data(0x00)
        self.write_cmd(0xFF)
        self.write_data(0x60); self.write_data(0x01); self.write_data(0x04)
        self.write_cmd(0xC3); self.write_data(0x13)
        self.write_cmd(0xC4); self.write_data(0x13)
        self.write_cmd(0xC9); self.write_data(0x22)
        self.write_cmd(0xBE); self.write_data(0x11)
        self.write_cmd(0xE1); self.write_data(0x10); self.write_data(0x0E)
        self.write_cmd(0xDF)
        self.write_data(0x21); self.write_data(0x0c); self.write_data(0x02)
        self.write_cmd(0xF0)
        self.write_data(0x45); self.write_data(0x09); self.write_data(0x08)
        self.write_data(0x08); self.write_data(0x26); self.write_data(0x2A)
        self.write_cmd(0xF1)
        self.write_data(0x43); self.write_data(0x70); self.write_data(0x72)
        self.write_data(0x36); self.write_data(0x37); self.write_data(0x6F)
        self.write_cmd(0xF2)
        self.write_data(0x45); self.write_data(0x09); self.write_data(0x08)
        self.write_data(0x08); self.write_data(0x26); self.write_data(0x2A)
        self.write_cmd(0xF3)
        self.write_data(0x43); self.write_data(0x70); self.write_data(0x72)
        self.write_data(0x36); self.write_data(0x37); self.write_data(0x6F)
        self.write_cmd(0xED); self.write_data(0x1B); self.write_data(0x0B)
        self.write_cmd(0xAE); self.write_data(0x77)
        self.write_cmd(0xCD); self.write_data(0x63)
        self.write_cmd(0x70)
        self.write_data(0x07); self.write_data(0x07); self.write_data(0x04)
        self.write_data(0x0E); self.write_data(0x0F); self.write_data(0x09)
        self.write_data(0x07); self.write_data(0x08); self.write_data(0x03)
        self.write_cmd(0xE8); self.write_data(0x34)
        self.write_cmd(0x62)
        self.write_data(0x18); self.write_data(0x0D); self.write_data(0x71)
        self.write_data(0xED); self.write_data(0x70); self.write_data(0x70)
        self.write_data(0x18); self.write_data(0x0F); self.write_data(0x71)
        self.write_data(0xEF); self.write_data(0x70); self.write_data(0x70)
        self.write_cmd(0x63)
        self.write_data(0x18); self.write_data(0x11); self.write_data(0x71)
        self.write_data(0xF1); self.write_data(0x70); self.write_data(0x70)
        self.write_data(0x18); self.write_data(0x13); self.write_data(0x71)
        self.write_data(0xF3); self.write_data(0x70); self.write_data(0x70)
        self.write_cmd(0x64)
        self.write_data(0x28); self.write_data(0x29); self.write_data(0xF1)
        self.write_data(0x01); self.write_data(0xF1); self.write_data(0x00)
        self.write_data(0x07)
        self.write_cmd(0x66)
        self.write_data(0x3C); self.write_data(0x00); self.write_data(0xCD)
        self.write_data(0x67); self.write_data(0x45); self.write_data(0x45)
        self.write_data(0x10); self.write_data(0x00); self.write_data(0x00)
        self.write_data(0x00)
        self.write_cmd(0x67)
        self.write_data(0x00); self.write_data(0x3C); self.write_data(0x00)
        self.write_data(0x00); self.write_data(0x00); self.write_data(0x01)
        self.write_data(0x54); self.write_data(0x10); self.write_data(0x32)
        self.write_data(0x98)
        self.write_cmd(0x74)
        self.write_data(0x10); self.write_data(0x85); self.write_data(0x80)
        self.write_data(0x00); self.write_data(0x00); self.write_data(0x4E)
        self.write_data(0x00)
        self.write_cmd(0x98); self.write_data(0x3e); self.write_data(0x07)
        self.write_cmd(0x35)
        self.write_cmd(0x21)
        self.write_cmd(0x11); time.sleep(0.12)
        self.write_cmd(0x29); time.sleep(0.02)
        self.write_cmd(0x21); self.write_cmd(0x11); self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00); self.write_data(0x00)
        self.write_data(0x00); self.write_data(0xef)
        self.write_cmd(0x2B)
        self.write_data(0x00); self.write_data(0x00)
        self.write_data(0x00); self.write_data(0xEF)
        self.write_cmd(0x2C)
        self.cs(1); self.dc(1); self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

i2c = I2C(1, scl=Pin(I2C_SCL), sda=Pin(I2C_SDA), freq=400_000)

class CST816S:
    def __init__(self, address=0x15):
        self._address = address
        self._bus = i2c
        self._rst = Pin(TP_RST, Pin.OUT)
        self._int = Pin(TP_INT, Pin.IN, Pin.PULL_UP)
        self._rst(0); time.sleep_ms(10)
        self._rst(1); time.sleep_ms(80)
        try:
            self._bus.writeto_mem(self._address, 0xFE, b'\x01')
        except OSError:
            pass

    def read(self):
        try:
            d = self._bus.readfrom_mem(self._address, 0x02, 5)
        except OSError:
            return (False, 0, 0)
        if (d[0] & 0x0F) == 0:
            return (False, 0, 0)
        x = ((d[1] & 0x0F) << 8) | d[2]
        y = ((d[3] & 0x0F) << 8) | d[4]
        return (True, x, y)


def colour(R, G, B):
    return (((G & 0b00011100) << 3) + ((B & 0b11111000) >> 3) << 8) \
           + (R & 0b11111000) + ((G & 0b11100000) >> 5)

C_BLACK  = colour(0, 0, 0)
C_BG     = colour(8, 10, 15)
C_INK    = colour(240, 240, 245)
C_TEXT   = colour(220, 210, 120)
C_BTN    = colour(0, 120, 115)
C_BTNTX  = colour(200, 255, 250)
C_HINT   = colour(60, 70, 80)
C_DIS    = colour(40, 44, 54) 
C_OK     = colour(80, 220, 120)
C_WARN   = colour(230, 120, 80)

FONT = bytes([
    0x00,0x00,0x00,0x00,0x00, 0x00,0x00,0x5F,0x00,0x00, 0x00,0x07,0x00,0x07,0x00,
    0x14,0x7F,0x14,0x7F,0x14, 0x24,0x2A,0x7F,0x2A,0x12, 0x23,0x13,0x08,0x64,0x62,
    0x36,0x49,0x56,0x20,0x50, 0x00,0x08,0x07,0x03,0x00, 0x00,0x1C,0x22,0x41,0x00,
    0x00,0x41,0x22,0x1C,0x00, 0x2A,0x1C,0x7F,0x1C,0x2A, 0x08,0x08,0x3E,0x08,0x08,
    0x00,0x80,0x70,0x30,0x00, 0x08,0x08,0x08,0x08,0x08, 0x00,0x00,0x60,0x60,0x00,
    0x20,0x10,0x08,0x04,0x02, 0x3E,0x51,0x49,0x45,0x3E, 0x00,0x42,0x7F,0x40,0x00,
    0x72,0x49,0x49,0x49,0x46, 0x21,0x41,0x49,0x4D,0x33, 0x18,0x14,0x12,0x7F,0x10,
    0x27,0x45,0x45,0x45,0x39, 0x3C,0x4A,0x49,0x49,0x31, 0x41,0x21,0x11,0x09,0x07,
    0x36,0x49,0x49,0x49,0x36, 0x46,0x49,0x49,0x29,0x1E, 0x00,0x00,0x14,0x00,0x00,
    0x00,0x40,0x34,0x00,0x00, 0x00,0x08,0x14,0x22,0x41, 0x14,0x14,0x14,0x14,0x14,
    0x00,0x41,0x22,0x14,0x08, 0x02,0x01,0x59,0x09,0x06, 0x3E,0x41,0x5D,0x59,0x4E,
    0x7C,0x12,0x11,0x12,0x7C, 0x7F,0x49,0x49,0x49,0x36, 0x3E,0x41,0x41,0x41,0x22,
    0x7F,0x41,0x41,0x41,0x3E, 0x7F,0x49,0x49,0x49,0x41, 0x7F,0x09,0x09,0x09,0x01,
    0x3E,0x41,0x41,0x51,0x73, 0x7F,0x08,0x08,0x08,0x7F, 0x00,0x41,0x7F,0x41,0x00,
    0x20,0x40,0x41,0x3F,0x01, 0x7F,0x08,0x14,0x22,0x41, 0x7F,0x40,0x40,0x40,0x40,
    0x7F,0x02,0x1C,0x02,0x7F, 0x7F,0x04,0x08,0x10,0x7F, 0x3E,0x41,0x41,0x41,0x3E,
    0x7F,0x09,0x09,0x09,0x06, 0x3E,0x41,0x51,0x21,0x5E, 0x7F,0x09,0x19,0x29,0x46,
    0x26,0x49,0x49,0x49,0x32, 0x03,0x01,0x7F,0x01,0x03, 0x3F,0x40,0x40,0x40,0x3F,
    0x1F,0x20,0x40,0x20,0x1F, 0x3F,0x40,0x38,0x40,0x3F, 0x63,0x14,0x08,0x14,0x63,
    0x03,0x04,0x78,0x04,0x03, 0x61,0x59,0x49,0x4D,0x43,
])

def _char(asc, xt, yt, sz, col):
    if asc < 32 or asc > 90:
        asc = 32
    code = (asc - 32) * 5
    for ii in range(5):
        line = FONT[code + ii]
        for yy in range(8):
            if (line >> yy) & 1:
                if sz == 1:
                    LCD.pixel(xt + ii, yt + yy, col)
                else:
                    LCD.fill_rect(xt + ii*sz, yt + yy*sz, sz, sz, col)

def prnt_st(s, x, y, sz, col):
    move = 6 if sz == 1 else (11 if sz == 2 else 17)
    for ch in s:
        _char(ord(ch), x, y, sz, col)
        x += move

def cntr_st(s, y, sz, col):
    w = 6 if sz == 1 else (11 if sz == 2 else 17)
    x = (240 - len(s) * w) // 2
    prnt_st(s, x, y, sz, col)

def load_model(path="emnist_w.bin"):
    import gc
    with open(path, "rb") as f:
        magic = f.read(4)
        if magic == b"EMK1":
            raise ValueError("Stary format vah — pretrenuj pomoci "
                             "train_emnist_balanced.py")
        if magic != b"EMK2":
            raise ValueError("Spatny format emnist_w.bin")
        n_in, n_h, n_out = struct.unpack("<HHH", f.read(6))
        s1, hs, s2 = struct.unpack("<fff", f.read(12))
        gc.collect()
        w1 = bytearray(n_h * n_in)
        if f.readinto(w1) != n_h * n_in:
            raise ValueError("Poskozeny soubor vah (W1)")
        b1 = array('f', struct.unpack("<%df" % n_h, f.read(4 * n_h)))
        w2 = bytearray(n_out * n_h)
        if f.readinto(w2) != n_out * n_h:
            raise ValueError("Poskozeny soubor vah (W2)")
        b2 = array('f', struct.unpack("<%df" % n_out, f.read(4 * n_out)))
        cmap = f.read(n_out).decode()
    gc.collect()
    return n_in, n_h, n_out, s1, hs, s2, w1, b1, w2, b2, cmap


@micropython.viper
def _dense(x: ptr8, w: ptr8, out: ptr32, n_in: int, n_out: int):
    for o in range(n_out):
        acc = 0
        base = o * n_in
        for i in range(n_in):
            acc += int(x[i]) * (int(w[base + i]) - 128)
        out[o] = acc


class EmnistNet:
    def __init__(self, path="emnist_w.bin"):
        (self.n_in, self.n_h, self.n_out, self.s1, self.hs, self.s2,
         self.w1, self.b1, self.w2, self.b2, self.cmap) = load_model(path)
        self._acc1 = array('i', [0] * self.n_h)
        self._hq   = bytearray(self.n_h)
        self._acc2 = array('i', [0] * self.n_out)

    def predict(self, x_u8, allowed=None):
        _dense(x_u8, self.w1, self._acc1, self.n_in, self.n_h)
        k1 = self.s1 / 255.0
        hs = self.hs
        b1 = self.b1
        hq = self._hq
        for j in range(self.n_h):
            v = self._acc1[j] * k1 + b1[j]
            if v <= 0.0:
                hq[j] = 0
            elif v >= hs:
                hq[j] = 255
            else:
                hq[j] = int(v / hs * 255.0 + 0.5)
        _dense(hq, self.w2, self._acc2, self.n_h, self.n_out)
        k2 = self.s2 * hs / 255.0
        b2 = self.b2
        if allowed is None:
            allowed = range(self.n_out)
        best, bi = -1e30, -1
        logits = []
        for c in allowed:
            s = self._acc2[c] * k2 + b2[c]
            logits.append(s)
            if s > best:
                best, bi = s, c
        tot = 0.0
        for s in logits:
            tot += math.exp(s - best)
        return bi, 1.0 / tot

TXT_Y    = 22
CANV_Y0  = 46
CANV_Y1  = 158
PEN_R    = 5
IDLE_MS  = 700

MAX_CHARS = 12

BTNS = (
    ( 18, 162, 44, 22),
    ( 70, 184, 44, 22),
    (126, 184, 44, 22),
    (178, 162, 44, 22),
)
BTN_LABELS = ("", "SPC", "CLR", "DEL")
MODE_NAMES = ("ALL", "ABC", "123")
mode = 0

def chord(y):
    dy = y - 120
    q = 14400 - dy * dy
    return int(math.sqrt(q)) if q > 0 else 0

def _rrdx(row, h, r):
    if r <= 0:
        return 0
    if row < r:
        dy = r - row
    elif row >= h - r:
        dy = row - (h - r - 1)
    else:
        return 0
    sq = r * r - dy * dy
    return r - int(math.sqrt(sq)) if sq >= 0 else r

def filled_rrect(x, y, w, h, r, col):
    r = min(r, w // 2, h // 2)
    for row in range(h):
        d = _rrdx(row, h, r)
        lw = w - 2 * d
        if lw > 0:
            LCD.hline(x + d, y + row, lw, col)

def draw_static():
    LCD.fill(C_BLACK)
    LCD.fill_rect(0, CANV_Y0, 240, CANV_Y1 - CANV_Y0, C_BG)
    a = chord(CANV_Y0 - 1)
    LCD.hline(120 - a, CANV_Y0 - 1, 2 * a, C_HINT)
    a = chord(CANV_Y1)
    LCD.hline(120 - a, CANV_Y1, 2 * a, C_HINT)
    for i in range(len(BTNS)):
        bx, by, bw, bh = BTNS[i]
        filled_rrect(bx, by, bw, bh, 8, C_BTN)
        lab = BTN_LABELS[i]
        if lab:
            prnt_st(lab, bx + (bw - 17) // 2, by + (bh - 8) // 2, 1, C_BTNTX)
    draw_mode()

def draw_mode():
    bx, by, bw, bh = BTNS[0]
    filled_rrect(bx, by, bw, bh, 8, C_BTN if mode == 0 else C_OK)
    lab = MODE_NAMES[mode]
    prnt_st(lab, bx + (bw - 17) // 2, by + (bh - 8) // 2, 1,
            C_BTNTX if mode == 0 else C_BLACK)

def btn_hit(tx, ty):
    for i in range(len(BTNS)):
        bx, by, bw, bh = BTNS[i]
        if bx - 5 <= tx <= bx + bw + 5 and by - 5 <= ty <= by + bh + 5:
            return i
    return -1

def draw_text():
    LCD.fill_rect(0, TXT_Y - 2, 240, 22, C_BLACK)
    if text:
        cntr_st(text[-MAX_CHARS:], TXT_Y, 2, C_TEXT)
    else:
        cntr_st("NAKRESLI PISMENO", TXT_Y + 4, 1, C_HINT)

def clear_canvas():
    global bbox, has_ink
    LCD.fill_rect(0, CANV_Y0, 240, CANV_Y1 - CANV_Y0, C_BG)
    bbox = [1000, 1000, -1, -1]
    has_ink = False

def pen_dot(x, y):
    global has_ink
    for dy in range(-PEN_R, PEN_R + 1):
        yy = y + dy
        if yy <= CANV_Y0 or yy >= CANV_Y1:
            continue
        a = int(math.sqrt(PEN_R * PEN_R - dy * dy))
        x0 = max(0, x - a)
        LCD.hline(x0, yy, min(240, x + a + 1) - x0, C_INK)
    if x - PEN_R < bbox[0]: bbox[0] = max(0, x - PEN_R)
    if y - PEN_R < bbox[1]: bbox[1] = max(CANV_Y0 + 1, y - PEN_R)
    if x + PEN_R > bbox[2]: bbox[2] = min(239, x + PEN_R)
    if y + PEN_R > bbox[3]: bbox[3] = min(CANV_Y1 - 1, y + PEN_R)
    has_ink = True

def pen_line(x0, y0, x1, y1):
    d = max(abs(x1 - x0), abs(y1 - y0))
    if d == 0:
        pen_dot(x1, y1)
        return
    for i in range(0, d + 1, 2):
        pen_dot(x0 + (x1 - x0) * i // d, y0 + (y1 - y0) * i // d)

_x28 = bytearray(784)

def rasterize():
    bx, by, bx2, by2 = bbox
    bw = bx2 - bx + 1
    bh = by2 - by + 1
    if bw < 3 or bh < 3:
        return False
    side = bw if bw > bh else bh
    tw = max(1, (bw * 20 + side // 2) // side)
    th = max(1, (bh * 20 + side // 2) // side)

    grid = bytearray(tw * th)
    px = LCD.pixel
    for gy in range(th):
        y0 = by + bh * gy // th
        y1 = by + bh * (gy + 1) // th
        if y1 <= y0: y1 = y0 + 1
        for gx in range(tw):
            x0 = bx + bw * gx // tw
            x1 = bx + bw * (gx + 1) // tw
            if x1 <= x0: x1 = x0 + 1
            cnt = 0
            for yy in range(y0, y1):
                for xx in range(x0, x1):
                    if px(xx, yy) == C_INK:
                        cnt += 1
            area = (y1 - y0) * (x1 - x0)
            g = cnt * 510 // area
            grid[gy * tw + gx] = 255 if g > 255 else g

    sg = sx = sy = 0
    for gy in range(th):
        for gx in range(tw):
            g = grid[gy * tw + gx]
            sg += g; sx += g * gx; sy += g * gy
    if sg == 0:
        return False
    comx = sx / sg
    comy = sy / sg

    ox = int(14 - comx + 0.5)
    oy = int(14 - comy + 0.5)
    ox = min(max(ox, 0), 28 - tw)
    oy = min(max(oy, 0), 28 - th)

    for i in range(784):
        _x28[i] = 0
    for gy in range(th):
        dst = (gy + oy) * 28 + ox
        src = gy * tw
        for gx in range(tw):
            _x28[dst + gx] = grid[src + gx]
    return True


LCD = LCD_1inch28()
LCD.set_bl_pwm(65535)
touch = CST816S()

try:
    net = EmnistNet()
    model_ok = True
    model_err = ""

    ALLOWED = (
        None,
        tuple(i for i, ch in enumerate(net.cmap) if ch.isalpha()),
        tuple(i for i, ch in enumerate(net.cmap) if ch.isdigit()),
    )
except Exception as e:
    net = None
    model_ok = False
    model_err = str(e)


USB_KBD     = True
HOST_QWERTZ = False

hid   = None
mouse = None
usb_err = ""
if USB_KBD:
    try:
        import usb.device
        from usb.device.keyboard import KeyboardInterface
        from usb.device.hid import HIDInterface

        _PAD_DESC = bytes((
            0x05, 0x01, 0x09, 0x02, 0xA1, 0x01,
            0x09, 0x01, 0xA1, 0x00,
            0x05, 0x09, 0x19, 0x01, 0x29, 0x03,
            0x15, 0x00, 0x25, 0x01,
            0x95, 0x03, 0x75, 0x01, 0x81, 0x02,
            0x95, 0x01, 0x75, 0x05, 0x81, 0x01,
            0x05, 0x01, 0x09, 0x30, 0x09, 0x31, 0x09, 0x38,
            0x15, 0x81, 0x25, 0x7F,
            0x75, 0x08, 0x95, 0x03, 0x81, 0x06,
            0xC0, 0xC0,
        ))

        class PadMouse(HIDInterface):
            def __init__(self):
                super().__init__(_PAD_DESC, protocol=2,
                                 interface_str="RP2350 Touchpad")
                self.btn = 0
                self._buf = bytearray(4)

            def flush(self, dx=0, dy=0, wh=0):
                if self.busy():
                    return False
                struct.pack_into("Bbbb", self._buf, 0,
                                 self.btn, dx, dy, wh)
                self.send_report(self._buf)
                return True

            def set_btn(self, mask, down):
                if down:
                    self.btn |= mask
                else:
                    self.btn &= (~mask) & 0xFF
                for _ in range(60): 
                    if self.flush():
                        return
                    time.sleep_ms(1)

        hid   = KeyboardInterface()
        mouse = PadMouse()

        usb.device.get().init(hid, mouse, builtin_driver=True)
    except ImportError:
        hid   = None
        mouse = None
    except Exception as e:
        hid   = None
        mouse = None
        usb_err = str(e)
        print("USB init selhal:", e)

def usb_send(ch):
    if hid is None:
        return
    try:
        if not hid.is_open():
            return
        if ch == " ":
            code = 44 
        elif ch == "\b":
            code = 42 
        elif "0" <= ch <= "9":
            d = ord(ch) - 48
            if HOST_QWERTZ:
                code = 98 if d == 0 else 88 + d 
            else:
                code = 39 if d == 0 else 29 + d 
        else:
            i = ord(ch) - 65
            if not 0 <= i < 26:
                return
            code = 4 + i
            if HOST_QWERTZ:
                if code == 28:   code = 29
                elif code == 29: code = 28
        t0 = time.ticks_ms()
        while hid.busy():
            if time.ticks_diff(time.ticks_ms(), t0) > 50:
                return
            time.sleep_ms(1)
        hid.send_keys((code,))
        time.sleep_ms(10)
        t0 = time.ticks_ms()
        while hid.busy():
            if time.ticks_diff(time.ticks_ms(), t0) > 50:
                return
            time.sleep_ms(1)
        hid.send_keys(())
        time.sleep_ms(5)
    except Exception:
        pass

TOPB = (92, 2, 56, 16) 

def draw_topbtn():
    if mouse is None:
        return 
    bx, by, bw, bh = TOPB
    filled_rrect(bx, by, bw, bh, 8, C_OK if usb_state else C_DIS)
    lab = "MOUSE" if screen == 0 else "KEYB"
    col = C_BLACK if usb_state else C_HINT
    prnt_st(lab, bx + (bw - len(lab) * 6) // 2, by + (bh - 8) // 2, 1, col)

def top_hit(tx, ty):
    bx, by, bw, bh = TOPB
    return bx - 6 <= tx <= bx + bw + 6 and ty <= by + bh + 5

PAD_Y0 = 24
PAD_Y1 = 158
PAD_SPEED = 3.5
SCROLL_DIV = 10

PBTNS = (
    ( 32, 174, 52, 24),
    ( 94, 186, 52, 24),
    (156, 174, 52, 24),
)
PBTN_LABELS = ("LEFT", "SCROLL", "RIGHT")

def draw_pad_static():
    LCD.fill(C_BLACK)
    LCD.fill_rect(0, PAD_Y0, 240, PAD_Y1 - PAD_Y0, C_BG)
    a = chord(PAD_Y0 - 1)
    LCD.hline(120 - a, PAD_Y0 - 1, 2 * a, C_HINT)
    a = chord(PAD_Y1)
    LCD.hline(120 - a, PAD_Y1, 2 * a, C_HINT)
    cntr_st("TOUCHPAD", (PAD_Y0 + PAD_Y1) // 2 - 4, 1, C_HINT)
    for i in range(len(PBTNS)):
        draw_pbtn(i, False)
    draw_topbtn()

def draw_pbtn(i, active):
    bx, by, bw, bh = PBTNS[i]
    on = active or (i == 1 and scr_mode)
    filled_rrect(bx, by, bw, bh, 8, C_OK if on else C_BTN)
    lab = PBTN_LABELS[i]
    prnt_st(lab, bx + (bw - len(lab) * 6) // 2, by + (bh - 8) // 2, 1,
            C_BLACK if on else C_BTNTX)

def pbtn_hit(tx, ty):
    for i in range(len(PBTNS)):
        bx, by, bw, bh = PBTNS[i]
        if bx - 5 <= tx <= bx + bw + 5 and by - 5 <= ty <= by + bh + 5:
            return i
    return -1

def reset_kbd_state():
    global bbox, has_ink
    bbox = [1000, 1000, -1, -1]
    has_ink = False

text = ""
bbox = [1000, 1000, -1, -1]
has_ink = False
screen = 0 
usb_state = False
scr_mode = False

draw_static()
if not model_ok:
    cntr_st("CHYBA MODELU:", 92, 1, C_WARN)
    cntr_st(model_err[:34].upper(), 106, 1, C_WARN)
    cntr_st("NAHRAJ NOVY EMNIST_W.BIN", 120, 1, C_WARN)
draw_text()
if usb_err:
    cntr_st(("USB CHYBA: " + usb_err)[:34].upper(), 36, 1, C_WARN)
draw_topbtn()
LCD.show()

usb_chk    = 0
was_down   = False
last_x = last_y = 0
last_lift  = time.ticks_ms()
last_show  = 0
dirty      = False
in_canvas  = False

p_zone      = 0 
p_btn_held  = -1
p_t_down    = 0
p_moved     = 0
p_dragging  = False
p_last_tap  = -10000
fx = fy = fw = 0.0 

def switch_screen():
    global screen, in_canvas, p_zone, p_dragging, fx, fy, fw
    screen ^= 1
    in_canvas = False
    p_zone = 0
    fx = fy = fw = 0.0
    if p_dragging and mouse is not None:
        try: mouse.set_btn(1, False)
        except Exception: pass
    p_dragging = False
    reset_kbd_state()
    if screen == 0:
        draw_static()
        draw_text()
        draw_topbtn()
    else:
        draw_pad_static()

def _fatal(e):
    try:
        LCD.fill_rect(0, 56, 240, 116, C_BLACK)
        cntr_st("CHYBA PROGRAMU:", 62, 1, C_WARN)
        s = repr(e).upper()
        y = 78
        while s and y < 168:
            cntr_st(s[:26], y, 1, C_WARN)
            s = s[26:]
            y += 12
        LCD.show()
    except Exception:
        pass

try:
    while True:
        down, tx, ty = touch.read()
        now = time.ticks_ms()

        if down and not was_down and top_hit(tx, ty) and mouse is not None:
            if usb_state:
                switch_screen()
                dirty = True
            was_down = True
            time.sleep_ms(5)
            continue

        if screen == 0:
            if down:
                if not was_down:
                    in_canvas = CANV_Y0 < ty < CANV_Y1
                    if not in_canvas:
                        b = btn_hit(tx, ty)
                        if b == 0:
                            mode = (mode + 1) % 3
                            draw_mode()
                            dirty = True
                        elif b == 1:
                            text += " "
                            usb_send(" ")
                        elif b == 2:
                            text = ""
                        elif b == 3:
                            text = text[:-1]
                            usb_send("\b")
                        if b >= 1:
                            draw_text()
                            dirty = True
                if in_canvas and model_ok:
                    cy = min(max(ty, CANV_Y0 + 1), CANV_Y1 - 1)
                    if was_down:
                        pen_line(last_x, last_y, tx, cy)
                    else:
                        pen_dot(tx, cy)
                    dirty = True
                    last_x, last_y = tx, cy
                else:
                    last_x, last_y = tx, ty
                was_down = True
            else:
                if was_down:
                    last_lift = now
                was_down = False

                if has_ink and model_ok and time.ticks_diff(now, last_lift) > IDLE_MS:
                    if rasterize():
                        t0 = time.ticks_ms()
                        cls, conf = net.predict(_x28, ALLOWED[mode])
                        dt = time.ticks_diff(time.ticks_ms(), t0)
                        letter = net.cmap[cls]
                        if "a" <= letter <= "z":
                            letter = chr(ord(letter) - 32)
                        text += letter
                        usb_send(letter)
                        if len(text) > 60:
                            text = text[-60:]
                        draw_text()
                        LCD.fill_rect(0, CANV_Y1 - 14, 240, 13, C_BG)
                        cntr_st("%s  %d%%  %dMS" % (letter, int(conf * 100), dt),
                                CANV_Y1 - 13, 1, C_OK if conf > 0.5 else C_WARN)
                        LCD.show()
                        time.sleep_ms(350)
                    clear_canvas()
                    dirty = True

        else:
            if down:
                if not was_down:
                    if PAD_Y0 < ty < PAD_Y1:
                        p_zone = 1
                        p_t_down = now
                        p_moved = 0
                        if (not scr_mode
                                and time.ticks_diff(now, p_last_tap) < 300):
                            p_dragging = True
                            if mouse is not None:
                                mouse.set_btn(1, True)
                    else:
                        pb = pbtn_hit(tx, ty)
                        if pb == 1:
                            scr_mode = not scr_mode
                            draw_pbtn(1, False)
                            dirty = True
                            p_zone = 0
                        elif pb >= 0:
                            p_zone = 2
                            p_btn_held = pb
                            draw_pbtn(pb, True)
                            dirty = True
                            if mouse is not None:
                                mouse.set_btn(1 if pb == 0 else 2, True)
                        else:
                            p_zone = 0
                elif p_zone == 1:
                    dx = tx - last_x
                    dy = ty - last_y
                    p_moved += abs(dx) + abs(dy)
                    if scr_mode:
                        fw -= dy / SCROLL_DIV
                    else:
                        fx += dx * PAD_SPEED
                        fy += dy * PAD_SPEED
                last_x, last_y = tx, ty
                was_down = True
            else:
                if was_down:
                    if p_zone == 1:
                        dur = time.ticks_diff(now, p_t_down)
                        if p_dragging:
                            p_dragging = False
                            if mouse is not None:
                                mouse.set_btn(1, False)
                        elif (not scr_mode and dur < 250 and p_moved < 8
                              and mouse is not None):
                            mouse.set_btn(1, True)
                            time.sleep_ms(15)
                            mouse.set_btn(1, False)
                        p_last_tap = now
                    elif p_zone == 2 and p_btn_held >= 0:
                        if mouse is not None:
                            mouse.set_btn(1 if p_btn_held == 0 else 2, False)
                        draw_pbtn(p_btn_held, False)
                        dirty = True
                        p_btn_held = -1
                    p_zone = 0
                was_down = False

            if mouse is not None and usb_state:
                mx = int(fx); my = int(fy); mw = int(fw)
                if mx or my or mw:
                    if mx > 127: mx = 127
                    elif mx < -127: mx = -127
                    if my > 127: my = 127
                    elif my < -127: my = -127
                    if mw > 7: mw = 7
                    elif mw < -7: mw = -7
                    if mouse.flush(mx, my, mw):
                        fx -= mx; fy -= my; fw -= mw

        if hid is not None and time.ticks_diff(now, usb_chk) > 500:
            usb_chk = now
            st = hid.is_open()
            if st != usb_state:
                usb_state = st
                draw_topbtn()
                dirty = True
                if not st and screen == 1:
                    switch_screen()

        if dirty and time.ticks_diff(now, last_show) > 40:
            LCD.show()
            last_show = now
            dirty = False

        time.sleep_ms(5)
except Exception as _e:
    _fatal(_e)
    raise