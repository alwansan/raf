import unittest
from tools.gt_fft_bank_numeric import audit as a
class NumericTests(unittest.TestCase):
    def test_opcode_counts(self):
        p=a.opcode_profile("%1 = OpBitcast %2 %3\n%4 = OpExtInst %2 %5 Sqrt %6\n")
        self.assertEqual(p["ops"]["OpBitcast"],1);self.assertEqual(p["ext"]["Sqrt"],1)
        self.assertEqual(p["ops"]["OpImageWrite"],0)
    def test_bank_source_mapping(self):
        dx="class Dx11FFT { public Dx11FFT(ComputeShader sh,int n,bool high,bool two):base(n,high,two,true) {} }"
        gpu="class GpuFFT { protected GpuFFT(int n,bool h,bool t,bool u){_HighPrecision=h;_TwoChannels=t;} }"
        waves="class W { private GpuFFT ChooseBestFFTAlgorithm(bool twoChannels) {return new Dx11FFT(sh,n,true,twoChannels);} }"
        x=a.bank_contract(dx,gpu,waves)
        self.assertEqual(x["caller_fourth_to_two_channels"],"direct")
        self.assertEqual(x["bank_to_two_channels"],"direct")
        self.assertEqual(x["bank_to_high_precision"],"other")
    def test_reversed_caller(self):
        dx="class Dx11FFT { public Dx11FFT(ComputeShader sh,int n,bool h,bool t):base(n,h,!t,true) {} }"
        gpu="class GpuFFT { protected GpuFFT(int n,bool h,bool t,bool u){_HighPrecision=h;_TwoChannels=t;} }"
        waves="class W { private GpuFFT ChooseBestFFTAlgorithm(bool twoChannels) {return new Dx11FFT(sh,n,true,!twoChannels);} }"
        r=a.bank_contract(dx,gpu,waves)
        self.assertEqual(r["caller_fourth_to_two_channels"],"inverted")
        self.assertEqual(r["bank_to_two_channels"],"inverted")
if __name__=="__main__":unittest.main()
