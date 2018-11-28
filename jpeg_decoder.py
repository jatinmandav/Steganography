import random
from B import *
import math

def create(value=None, *args):
    if len(args) and args[0]:
        return [create(value,*args[1:]) for i in range(round(args[0]))]
    else: return value

class jpegDecoder(object):
    def __init__(self,data):
        self.data=data

    def readHeads(self):
        self.APP = [0xe0,0xe1,0xe3,0xe4,0xe5,0xe6,0xe7,0xe8,0xe9,0xea,0xeb,0xec,0xed,0xee,0xef]
        self.DRI, self.DNL, self.EOI = 0xdd, 0xdc, 0xd9
        self.huffval = create([], 4)
        self.valptr = create([], 4)
        self.mincode = create([], 4)
        self.maxcode = create([], 4)
        self.zz = create(0, 64)
        self.qnt = create(0, 4, 64)
        self.size = len(self.data)
        self.ri = 0
        self.data_index = -1
        while True:
            if self.get_byte()==255:
                b=self.get_byte()
                if b==192:
                    self.lf = self.get_int()
                    self.p = self.get_byte()
                    self.y = self.get_int()
                    self.x = self.get_int()
                    self.nf = self.get_byte()
                    self.c = create(0, self.nf)
                    self.h = create(0, self.nf)
                    self.v = create(0, self.nf)
                    self.t = create(0, self.nf)
                    for lp in range(self.nf):
                        self.c[lp] = self.get_byte()
                        self.h[lp], self.v[lp] = self.get_double_four_bits()
                        self.t[lp] = self.get_byte()
                elif b==196:
                    self.lh = self.get_int()
                    def _fill_value(index):
                        self.getHuff()
                        self.lh -= self._ln
                        self.huffval[index] = self._huffval
                        self.valptr[index] = self._valptr
                        self.maxcode[index] = self._maxcode
                        self.mincode[index] = self._mincode
                    while self.lh > 0:
                        self.tc, self.th = self.get_double_four_bits()
                        if self.th == 0:
                            if self.tc == 0: _fill_value(0)
                            else: _fill_value(1)
                        else:
                            if self.tc == 0: _fill_value(2)
                            else: _fill_value(3)
                elif b == 219:
                    self.lq = self.get_int()
                    self.pq, self.tq = self.get_double_four_bits()
                    if self.tq in range(4):
                        for lp in range(64):
                            self.qnt[self.tq][lp] = self.get_byte()
                elif b == 217 or b == 218:
                    break
                elif b in self.APP:
                    for i in range(self.get_int() - 2): self.get_byte()
                elif b == self.DRI:
                    self.get_int()
                    self.ri = self.get_int()
        self.ls = self.get_int()
        self.ns = self.get_byte()
        self.cs = create(0, self.ns)
        self.td = create(0, self.ns)
        self.ta = create(0, self.ns)
        for lp in range(self.ns):
            self.cs[lp] = self.get_byte()
            self.td[lp], self.ta[lp] = self.get_double_four_bits()
        self.ss = self.get_byte()
        self.se = self.get_byte()
        self.ah, self.al = self.get_double_four_bits()

    def get_byte(self):
        self.data_index+=1
        return self.data[self.data_index]

    def get_double_four_bits(self):
        b = self.get_byte()
        return b >> 4, b & 0x0f

    def get_int(self):
        return (self.get_byte() << 8) ^ self.get_byte()

    def getHuff(self):
        self._bits     = create(0, 17)
        self._huffval  = create(0, 256)
        self._huffcode = create(0, 257)
        self._huffsize = create(0, 257)
        self._ehufco   = create(0, 257)
        self._ehufsi   = create(0, 257)
        self._mincode  = create(0, 17)
        self._maxcode  = create(0, 18)
        self._valptr   = create(0, 17)
        self._ln = 19 + self.get_table_data()
        self.generate_size_table()
        self.generate_code_table()
        self.order_codes()
        self.decode_tables()

    def get_table_data(self):
        count = 0
        for x in range(1, 17):
            self._bits[x] = self.get_byte()
            count += self._bits[x]
        for x in range(0, count):
            self._huffval[x] = self.get_byte()
        return count

    def generate_size_table(self):
        k, i, j = 0, 1, 1
        while True:
            if j > self._bits[i]:
                j = 1
                i += 1
                if i > 16: break
            else:
                self._huffsize[k] = i
                k += 1
                j += 1
        self._huffsize[k] = 0
        self._lastk = k

    def generate_code_table(self):
        k, code, si = 0, 0, self._huffsize[0]
        while True:
            self._huffcode[k] = code
            k += 1
            code += 1
            if self._huffsize[k] == si: continue
            if self._huffsize[k] == 0: break
            while True:
                code <<= 1
                si += 1
                if self._huffsize[k] == si: break

    def order_codes(self):
        k = 0
        while True:
            i = self._huffval[k]
            self._ehufco[i] = self._huffcode[k]
            self._ehufsi[i] = self._huffsize[k]
            k += 1
            if k >= self._lastk: break

    def decode_tables(self):
        i, j = 0, 0
        while True:
            i += 1
            if i > 16: return
            if self._bits[i] == 0:
                self._maxcode[i] = -1
            else:
                self._valptr[i] = j
                self._mincode[i] = self._huffcode[j]
                j += self._bits[i] - 1
                self._maxcode[i] = self._huffcode[j]
                j += 1

    def readImage(self):
        pred = create(0, self.nf)
        self.CNT = 0
        buff = create(0, 2 * 8 * 8 * self.get_block_count())
        pos, mcu_count = 0, 0
        while True:
            for n_comp in range(0, self.nf):
                for cnt in range(self.h[n_comp] * self.v[n_comp]):
                    self.hftbl = self.td[n_comp] * 2
                    tmp = self._internal_decode()
                    self.diff = self.receive(tmp)
                    self.zz[0] = pred[0] + self.extend(self.diff, tmp)
                    pred[n_comp] = self.zz[0]
                    self.hftbl = self.ta[n_comp] * 2 + 1
                    self.decode_ac_coefficients()
                    for lp in range(64):
                        buff[pos] = self.zz[lp]
                        pos += 1
            mcu_count += 1
            if mcu_count == self.ri:
                mcu_count = 0
                self.CNT = 0
                pred[n_comp] = create(0, self.nf)
                self.get_byte()
                tmp_b = self.get_byte()
                if tmp_b == EOI: break
            if self.size-self.data_index-1 <= 2:
                if self.size-self.data_index-1 == 2:
                    self.get_byte()
                    if self.get_byte() != self.EOI:
                        print('File does not end with EOI')
                else:
                    if self.size-self.data_index-1 == 1:
                        print('ERROR: last byte: %X' % self.get_byte())
                    print('File Does not end with EOI')
                break
        self.coeff=buff[:pos]

    def get_next_bit(self):
        if not self.CNT:
            self.CNT = 8
            self.B = self.get_byte()
            if self.B == 255:
                self.get_byte()
        BIT = self.B & 0x80
        BIT >>= 7
        self.CNT -= 1
        self.B <<= 1
        return BIT

    def get_block_count(self):
        square = lambda x: x * x
        if self.nf == 1:
            return square((self.x + 7) / 8)
        elif self.nf == 3:
            return 6 * square((self.x + 15) / 16)
        else: print('components\'s number is neither 1 nor 3')

    def _internal_decode(self):
        i, cd = 1, self.get_next_bit()
        while cd > self.maxcode[self.hftbl][i]:
            cd = (cd << 1) + self.get_next_bit()
            i += 1
        j = self.valptr[self.hftbl][i]
        j += cd - self.mincode[self.hftbl][i]
        return self.huffval[self.hftbl][j]

    def receive(self, sss):
        v, i = 0, 0
        while i != sss:
            i += 1
            v = (v << 1) + self.get_next_bit()
        return v

    def extend(self, v, t):
        if t == 0: return v
        vt = 0x01 << t - 1
        if v < vt:
            vt = (-1 << t) + 1
            v += vt
        return v

    def decode_ac_coefficients(self):
        k = 1
        self.zz = [0] * 64
        while True:
            rs = self._internal_decode()
            ssss = rs % 16
            r = rs >> 4
            if ssss == 0:
                if r == 15: k += 16
                else: return
            else:
                k += r
                self.zz[k%64] = self.extend(self.receive(ssss), ssss)
                if k == 63: return
                else: k += 1
