class A { unsafe void F(byte[] b) { fixed (byte* p = b) { *p = 1; } } }
