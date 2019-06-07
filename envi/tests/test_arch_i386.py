import envi
import envi.memcanvas as e_memcanvas
import vivisect
import unittest

# name, bytes, va, repr, txtRender
i386SingleByteOpcodes = [
    ('add', '0001', 0x40, 'add byte [ecx],al', 'add byte [ecx],al'),
    ('adc', '83D306', 0x40, 'adc ebx,6', 'adc ebx,6'),
    ('jg', '7faa', 0x400, 'jg 0x000003ac', 'jg 0x000003ac'),
    ('rep movsb', 'f3a4', 0x40, 'rep: movsb ', 'rep: movsb '),
    ('mov al', 'b0aa', 0x40, 'mov al,170', 'mov al,170'),
    ('mov ebx', 'b8aaaa4040', 0x40, 'mov eax,0x4040aaaa', 'mov eax,0x4040aaaa'),
    ('inc ebx', '43', 0x40, 'inc ebx', 'inc ebx'),
    ('call ebx', 'ffd3', 0x40, 'call ebx', 'call ebx'),
    ('call lit', 'e801010101', 0x40, 'call 0x01010146', 'call 0x01010146'),
    ('mov dword', '89aa41414141', 0x40, 'mov dword [edx + 1094795585],ebp', 'mov dword [edx + 1094795585],ebp'),
    ('imul 1', 'f6aaaaaaaaaa', 0x40, 'imul al,byte [edx - 1431655766]', 'imul al,byte [edx - 1431655766]'),
    ('imul 2', 'f7aaaaaaaaaa', 0x40, 'imul eax,dword [edx - 1431655766]', 'imul eax,dword [edx - 1431655766]'),
    ('push', 'fff0', 0x40, 'push eax', 'push eax'),
    ('nop 1', '90', 0x40, 'nop ', 'nop '),
    ('nop 2', '0f1fc0', 0x40, 'nop eax', 'nop eax'),
    ('nop 3', 'f30f1fc0', 0x40, 'rep: nop eax', 'rep: nop eax'),
    ('pop', '8ff0', 0x40, 'pop eax', 'pop eax'),
    ('pop', '8ffb', 0x40, 'pop ebx', 'pop ebx'),
    ('BSWAP (eax)', '0fc84141', 0x40, 'bswap eax', 'bswap eax'),
    ('BSWAP (ebx)', '0fcb4141', 0x40, 'bswap ebx', 'bswap ebx'),
    ('BSWAP (eax)', 'f30fc84141', 0x40, 'rep: bswap eax', 'rep: bswap eax'),
    ('BSWAP (ebx)', 'f30fcb4141', 0x40, 'rep: bswap ebx', 'rep: bswap ebx'),
    ('setg (al)', '0f9fc0', 0x40, 'setg al', 'setg al'),
    ('setg (dl)', '0f9fc2', 0x40, 'setg dl', 'setg dl'),
    ('rep setg (al)', 'f30f9fc0', 0x40, 'rep: setg al', 'rep: setg al'),
    ('rep setg (dl)', 'f30f9fc2', 0x40, 'rep: setg dl', 'rep: setg dl'),
    ('prefix scas', 'f2ae', 0x40, 'repnz: scasb ', 'repnz: scasb '),
]

i386MultiByteOpcodes = [
    ('CVTTPS2PI', '0f2caaaaaaaa41', 0x40, 'cvttps2pi mm5,qword [edx + 1101703850]', 'cvttps2pi mm5,qword [edx + 1101703850]'),
    ('CVTTSS2SI', 'f30f2caaaaaaaa41', 0x40, 'cvttss2si ebp,dword [edx + 1101703850]', 'cvttss2si ebp,dword [edx + 1101703850]'),
    ('CVTTSS2SI', 'f30f2ce9414141', 0x40, 'cvttss2si ebp,xmm1', 'cvttss2si ebp,xmm1'),
    ('CVTTPD2PI', '660f2caaaaaaaa41', 0x40, 'cvttpd2pi oword [edx + 1101703850],oword [edx + 1101703850]', 'cvttpd2pi oword [edx + 1101703850],oword [edx + 1101703850]'),
    ('CVTTSD2SI', 'f20f2caaaaaaaa41', 0x40, 'cvttsd2si ebp,qword [edx + 1101703850]', 'cvttsd2si ebp,qword [edx + 1101703850]'),
    ('ADDPS', '0f58aa4141414141', 0x40, 'addps xmm5,oword [edx + 1094795585]', 'addps xmm5,oword [edx + 1094795585]'),
    ('MOVAPS', '0f28aa41414141', 0x40, 'movaps xmm5,oword [edx + 1094795585]', 'movaps xmm5,oword [edx + 1094795585]'),
    ('MOVAPD', '660f28aa41414141', 0x40, 'movapd xmm5,oword [edx + 1094795585]', 'movapd xmm5,oword [edx + 1094795585]'),
    ('PMULLW (66)', '660faa41414141', 0x40, 'rsm ', 'rsm '),
    ('CMPXCH8B', '0fc70a', 0x40, 'cmpxch8b qword [edx]', 'cmpxch8b qword [edx]'),
    ('MOVD (66)',   '660f7ecb414141', 0x40, 'movd ebx,xmm1', 'movd ebx,xmm1'),
    ('MOVD', '0F6E0D41414100', 0x40, 'movd mm1,dword [0x00414141]', 'movd mm1,dword [0x00414141]'),
    ('MOVQ', '0F6FCB', 0x40, 'movq mm1,mm3', 'movq mm1,mm3'),
    ('PSRAW',  '0FE1CA4141', 0x40, 'psraw mm1,mm2', 'psraw mm1,mm2'),
    ('PSRLQ (66)',  '660FF3CB4141', 0x40, 'psllq xmm1,xmm3', 'psllq xmm1,xmm3'),
    ('PALIGNR', '0F3A0FDC03', 0x40, 'palignr xmm3,xmm4,3', 'palignr xmm3,xmm4,3'),
    ('PALIGNR (66)',  '660F3A0FCA07', 0x40, 'palignr xmm1,xmm2,7', 'palignr xmm1,xmm2,7'),
    ('PSLLQ (reg)',  '660FF3CA', 0x40, 'psllq xmm1,xmm2', 'psllq xmm1,xmm2'),
    ('PSLLW (regs)',  '0F71F108', 0x40, 'psllw mm1,8', 'psllw mm1,8'),
    ('PSLLQ (66)',  '660F73F108', 0x40, 'psllq xmm1,8', 'psllq xmm1,8'),
    ('PSRLW (66)',  '660F71D611', 0x40, 'psrlw xmm6,17', 'psrlw xmm6,17'),
    ('PSRAD (66)',  '660F72E704', 0x40, 'psrad xmm7,4', 'psrad xmm7,4'),
    ('PSRLQ (66)',  '660F73D308', 0x40, 'psrlq xmm3,8', 'psrlq xmm3,8'),
    ('PSRAW (66)',  '660F71E1084141', 0x40, 'psraw xmm1,8', 'psraw xmm1,8'),
    ('PSRLDQ (66)', '660f73faaa4141', 0x40, 'psldq xmm2,170', 'psldq xmm2,170'),
    ('LFENCE', '0faee8', 0x40, 'lfence ', 'lfence '),
    ('LFENCE', '0faeea', 0x40, 'lfence ', 'lfence '),
    ('LFENCE', '0faeec', 0x40, 'lfence ', 'lfence '),
    ('LFENCE', '0faeef', 0x40, 'lfence ', 'lfence '),
    ('MFENCE', '0faef0', 0x40, 'mfence ', 'mfence '),
    ('MFENCE', '0faef2', 0x40, 'mfence ', 'mfence '),
    ('MFENCE', '0faef5', 0x40, 'mfence ', 'mfence '),
    ('MFENCE', '0faef7', 0x40, 'mfence ', 'mfence '),

    ('CVTTSS2SI', 'f30f2cc8', 0x40, 'cvttss2si ecx,xmm0', 'cvttss2si ecx,xmm0'),
    ('PREFIXES', 'f0673e2e65f30f10ca', 0x40, 'addr lock cs ds gs: movss xmm1,xmm2', 'addr lock cs ds gs: movss xmm1,xmm2'),
    ('BSR', '0fbdc3414141', 0x40, 'bsr eax,ebx', 'bsr eax,ebx'),
    ('LZNT', 'f30fbdc3414141', 0x40, 'lzcnt eax,ebx', 'lzcnt eax,ebx'),

    # Because of how the MODRM Bytes are set, these map to the same instruction
    # TODO: Would these be the same to a real x86 chip?
    ('PSRLDQ (66)', '660f73b5aa4141', 0x40, 'psllq xmm5,170', 'psllq xmm5,170'),
    ('PSRLDQ (66)', '660f73f5aa4141', 0x40, 'psllq xmm5,170', 'psllq xmm5,170'),

    # Same for these two
    ('PSRLDQ (66)', '660f73b1aa4141', 0x40, 'psllq xmm1,170', 'psllq xmm1,170'),
    ('PSRLDQ (66)', '660f73b9aa4141', 0x40, 'psldq xmm1,170', 'psldq xmm1,170'),

    ('PCMPISTRI', '660f3a630f0d', 0x40, 'pcmpistri xmm1,oword [edi],13', 'pcmpistri xmm1,oword [edi],13'),
    ('PSHUFB', '660F3800EF', 0x40, 'pshufb xmm5,xmm7', 'pshufb xmm5,xmm7'),
    ('RDTSC', '0F31', 0x40, 'rdtsc ', 'rdtsc '),
    ('RDTSCP', '0F01F9', 0x40, 'rdtscp ', 'rdtscp '),
    ('CVTDQ2PD', 'f30fe6c0', 0x40, 'cvtdq2pd xmm0,xmm0', 'cvtdq2pd xmm0,xmm0'),
    ('MOVQ', 'F30F7ECB', 0x40, 'movq xmm1,xmm3', 'movq xmm1,xmm3'),
    ('MOVQ (F3)', 'F30F7E0D41414100', 0x40, 'movq xmm1,qword [0x00414141]', 'movq xmm1,qword [0x00414141]'),
    ('MOVSD', 'f20f10ca', 0x40, 'movsd xmm1,xmm2', 'movsd xmm1,xmm2'),
    ('MOVSD (PREFIX)', 'f3f20f10ca', 0x40, 'rep: movsd xmm1,xmm2', 'rep: movsd xmm1,xmm2'),
    ('POPCNT', '66f30fb8c3', 0x40, 'popcnt ax,bx', 'popcnt ax,bx'),
    ('POPCNT', 'f30fb8c4', 0x40, 'popcnt eax,esp', 'popcnt eax,esp'),
    ('POPCNT', 'f30fb80541414100', 0x40, 'popcnt eax,dword [0x00414141]', 'popcnt eax,dword [0x00414141]'),
    ('LZCNT', 'f30fbdc4', 0x40, 'lzcnt eax,esp', 'lzcnt eax,esp'),
    ('LZCNT', 'f30fbd0541414100', 0x40, 'lzcnt eax,dword [0x00414141]', 'lzcnt eax,dword [0x00414141]'),
    ('MOVDQU', 'F30F6FCA', 0x40, 'movdqu xmm1,xmm2', 'movdqu xmm1,xmm2'),
    ('MOVDQU (MEM)', 'F30F6F4810', 0x40, 'movdqu xmm1,oword [eax + 16]', 'movdqu xmm1,oword [eax + 16]'),
    ('MOVDQU (REP)', 'F3F30F6FCA', 0x40, 'movdqu xmm1,xmm2', 'movdqu xmm1,xmm2'),

    ('MOVSD', 'f20f100d28330608', 0x40, 'movsd xmm1,oword [0x08063328]', 'movsd xmm1,oword [0x08063328]'),
    ('MOVSD 2', 'f20f1145f0', 0x40, 'movsd oword [ebp - 16],xmm0', 'movsd oword [ebp - 16],xmm0'),
    ('MOVSD 3', 'f20f100d70790908', 0x40, 'movsd xmm1,oword [0x08097970]', 'movsd xmm1,oword [0x08097970]'),
    ('MOVSS', 'f30f1045f8', 0x40, 'movss xmm0,oword [ebp - 8]', 'movss xmm0,oword [ebp - 8]'),
    ('MOVSS 2', 'f30f1055d0', 0x40, 'movss xmm2,oword [ebp - 48]', 'movss xmm2,oword [ebp - 48]'),
    ('MOVSS 3', 'F30F110D41414100', 0x40, 'movss dword [0x00414141],xmm1', 'movss dword [0x00414141],xmm1'),
    ('CVTSI2SS', 'f30f2ac8', 0x40, 'cvtsi2ss xmm1,eax', 'cvtsi2ss xmm1,eax'),
    ('MULSS', 'f30f59ca', 0x40, 'mulss xmm1,xmm2', 'mulss xmm1,xmm2'),
    ('SUBSS', 'f30f5cc1', 0x40, 'subss xmm0,xmm1', 'subss xmm0,xmm1'),
    ('CVTSS2SD', 'f30f5ac0', 0x40, 'cvtss2sd xmm0,xmm0', 'cvtss2sd xmm0,xmm0'),
    ('SQRTSS', 'f30f51d9', 0x40, 'sqrtss xmm3,xmm1', 'sqrtss xmm3,xmm1'),
    ('VMXON', 'f30fc73541414100', 0x40, 'vmxon qword [0x00414141]', 'vmxon qword [0x00414141]'),
    ('MULSD', 'f20f59c1', 0x40, 'mulsd xmm0,xmm1', 'mulsd xmm0,xmm1'),
]


class i386InstructionSet(unittest.TestCase):
    _arch = envi.getArchModule("i386")

    def test_envi_i386_disasm_Specific_SingleByte_Instrs(self):
        '''
        pick 10 arbitrary 1-byte-operands
        '''
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, bytez, va, reprOp, renderOp in i386SingleByteOpcodes:

            op = self._arch.archParseOpcode(bytez.decode('hex'), 0, va)
            # print("'%s', 0x%x, '%s' == '%s'" % (bytez, va, repr(op), reprOp))
            self.assertEqual(repr(op), reprOp)

            scanv.clearCanvas()
            op.render(scanv)
            # print("render:  %s" % repr(scanv.strval))
            self.assertEqual(scanv.strval, renderOp)

    def test_envi_i386_disasm_Specific_MultiByte_Instrs(self):
        '''
        pick 10 arbitrary 2- and 3-byte operands
        '''
        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)

        for name, bytez, va, reprOp, renderOp in i386MultiByteOpcodes:

            op = self._arch.archParseOpcode(bytez.decode('hex'), 0, va)
            # print("'%s', 0x%x, '%s' == '%s'" % (bytez, va, repr(op), reprOp))
            self.assertEqual(repr(op), reprOp)

            scanv.clearCanvas()
            op.render(scanv)
            # print("render:  %s" % repr(scanv.strval))
            self.assertEqual(scanv.strval, renderOp)
    '''
    def test_envi_i386_disasm_A(self):
        pass
    def test_envi_i386_disasm_C(self):
        pass
    def test_envi_i386_disasm_D(self):
        pass
    def test_envi_i386_disasm_E(self):
        pass
    def test_envi_i386_disasm_F(self):
        pass
    def test_envi_i386_disasm_G(self):
        pass
    def test_envi_i386_disasm_I(self):
        pass
    def test_envi_i386_disasm_J(self):
        pass
    def test_envi_i386_disasm_L(self):
        pass
    def test_envi_i386_disasm_M(self):
        pass
    def test_envi_i386_disasm_N(self):
        pass
    def test_envi_i386_disasm_O(self):
        pass
    def test_envi_i386_disasm_P(self):
        pass
    def test_envi_i386_disasm_Q(self):
        pass
    def test_envi_i386_disasm_R(self):
        pass
    def test_envi_i386_disasm_S(self):
        pass
    def test_envi_i386_disasm_U(self):
        pass
    def test_envi_i386_disasm_V(self):
        pass
    def test_envi_i386_disasm_W(self):
        pass
    def test_envi_i386_disasm_X(self):
        pass
    def test_envi_i386_disasm_Y(self):
        pass
    '''

    def checkOpcode(self, hexbytez, va, oprepr, opcheck, opercheck, renderOp):

        op = self._arch.archParseOpcode(hexbytez.decode('hex'), 0, va)

        self.assertEqual( repr(op), oprepr )
        opvars = vars(op)
        for opk,opv in opcheck.items():
            # print("op: %s %s" % (opk,opv))
            self.assertEqual( (opk, opvars.get(opk)), (opk, opv) )

        for oidx in range(len(op.opers)):
            oper = op.opers[oidx]
            opervars = vars(oper)
            for opk,opv in opercheck[oidx].items():
                # print("oper: %s %s" % (opk,opv))
                self.assertEqual( (opk, opervars.get(opk)), (opk, opv) )

        vw = vivisect.VivWorkspace()
        scanv = e_memcanvas.StringMemoryCanvas(vw)
        op.render(scanv)
        #print "render:  %s" % repr(scanv.strval)
        self.assertEqual( scanv.strval, renderOp )

    def test_envi_i386_disasm_Reg_Operands(self):
        '''
        test an opcode encoded with an Reg operand
        _0      add al      04
        G       add         02
        C       mov         0f20
        D       mov         0f21
        P       punpcklbw   0f60
        S       mov         8c
        U       movmskps    0f50
        V       sqrtps      0f51

        '''
        opbytez = '0032'
        oprepr = 'add byte [edx],dh'
        opcheck =  {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = [{'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 2}, {'tsize': 1, 'reg': 134742018}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0440'
        oprepr = 'add al,64'
        opcheck = {'iflags': 65536, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 1, 'reg': 524288}, {'tsize': 1, 'imm': 64} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0218'
        oprepr = 'add bl,byte [eax]'
        opcheck = {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'add', 'opcode': 8193, 'size': 2}
        opercheck = ( {'tsize': 1, 'reg': 524291}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 0} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f2018'
        oprepr = 'mov dword [eax],ctrl3'
        opcheck =  {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'mov', 'opcode': 24577, 'size': 3}
        opercheck = ( {'disp': 0, 'tsize': 4, '_is_deref': True, 'reg': 0}, {'tsize': 4, 'reg': 35} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_i386_disasm_Imm_Operands(self):
        '''
        test an opcode encoded with an Imm operand
        _0      rol         d000
        A       callf       9a
        '''
        opbytez = 'd000'
        oprepr = 'rol byte [eax],1'
        opcheck =  {'iflags': 65536, 'va': 16384, 'prefixes': 0, 'mnem': 'rol', 'opcode': 8201, 'size': 2}
        opercheck = ( {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 0}, {'tsize': 4, 'imm': 1} )
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        # this is failing legitimately... we decode this opcode wrong
        opbytez = '9aaa11aabbcc33'
        oprepr = 'callf 0x33cc:0xbbaa11aa'
        opcheck =  {'iflags': 65540, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'callf', 'opcode': 4099, 'size': 7}
        opercheck = [{'tsize': 6, 'imm': 56954414829994}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_i386_disasm_PcRel_Operands(self):
        '''
        test an opcode encoded with an PcRelative operand
        '''
        pass

    def test_envi_i386_disasm_RegMem_Operands(self):
        '''
        test an opcode encoded with an RegMem operand
        X       outsb       6e
        Y       insd        6d
        '''
        opbytez = '6e'
        oprepr = 'outsb edx,byte [esi]'
        opcheck = {'iflags': 65538, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'outsb', 'opcode': 57347, 'size': 1}
        opercheck = [{'tsize': 4, 'reg': 2}, {'disp': 0, 'tsize': 1, '_is_deref': True, 'reg': 6}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '6d'
        oprepr = 'insd dword [esi],edx'
        opcheck =  {'iflags': 65538, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'insd', 'opcode': 57346, 'size': 1}
        opercheck = [{'disp': 0, 'tsize': 4, '_is_deref': True, 'reg': 6}, {'tsize': 4, 'reg': 2}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_i386_disasm_ImmMem_Operands(self):
        '''
        test an opcode encoded with an ImmMem operand
        O       mov         a1
        '''
        opbytez = 'a1a2345678'
        oprepr = 'mov eax,dword [0x785634a2]'
        opcheck =  {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'mov', 'opcode': 24577, 'size': 5}
        opercheck = [{'tsize': 4, 'reg': 0}, {'tsize': 4, '_is_deref': True, 'imm': 2018915490}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

    def test_envi_i386_disasm_SIB_Operands(self):
        '''
        exercize the entire SIB operand space
        A       jmp         ea
        E       lar         0f02
        Q       cvttps2pi   0f2c
        W       cvttps2pi   0f2c
        '''
        opbytez = 'eaa123456789ab'          # this wants more bytes, why?
        oprepr = 'jmp 0xab89:0x674523a1'       # this repr's wrong.  it should be ab89:674523a1
        opcheck = {'iflags': 65545, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'jmp', 'opcode': 4097, 'size': 7}
        opercheck = [{'tsize': 6, 'imm': 188606631453601}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)

        opbytez = '0f02aabbccddee'
        oprepr = 'lar ebp,word [edx - 287454021]'
        opcheck = {'iflags': 65538, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'lar', 'opcode': 57344, 'size': 7}
        opercheck = [{'tsize': 4, 'reg': 5}, {'disp': -287454021, 'tsize': 2, '_is_deref': True, 'reg': 2}]
        self.checkOpcode( opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr )

        opbytez = '0f2caabbccddeeff'
        oprepr = 'cvttps2pi mm5,qword [edx - 287454021]'
        opcheck = {'iflags': 65536, 'va': 16384, 'repr': None, 'prefixes': 0, 'mnem': 'cvttps2pi', 'opcode': 61440}
        opercheck = [{'tsize': 8, 'reg': 13}, {'disp': -287454021, 'tsize': 8, '_is_deref': True, 'reg': 2}]
        self.checkOpcode(opbytez, 0x4000, oprepr, opcheck, opercheck, oprepr)
