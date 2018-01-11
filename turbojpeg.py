# -*- coding: UTF-8 -*-
#
# PyTurboJPEG - An experimental Python wrapper of TurboJPEG for decoding and encoding JPEG image.
#
# Copyright (c) 2018, LiloHuang. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ctypes import *
import platform
import numpy as np

# default libTurboJPEG library path
DEFAULT_LIB_PATH = {
    'Darwin' : '/usr/local/opt/jpeg-turbo/lib/libturbojpeg.dylib',   # for Mac OS X
    'Linux'  : '/opt/libjpeg-turbo/lib64/libturbojpeg.so',           # for Linux
    'Windows': 'C:/libjpeg-turbo64/bin/turbojpeg.dll'                # for Windows
}

# pixel formats
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
TJPF_RGB = 0
TJPF_BGR = 1
TJPF_RGBX = 2
TJPF_BGRX = 3
TJPF_XBGR = 4
TJPF_XRGB = 5
TJPF_GRAY = 6
TJPF_RGBA = 7
TJPF_BGRA = 8
TJPF_ABGR = 9
TJPF_ARGB = 10
TJPF_CMYK = 11

# chrominance subsampling options
# see details in https://github.com/libjpeg-turbo/libjpeg-turbo/blob/master/turbojpeg.h
TJSAMP_444 = 0
TJSAMP_422 = 1
TJSAMP_420 = 2
TJSAMP_GRAY = 3
TJSAMP_440 = 4

class TurboJPEG(object):
    """An experimental Python wrapper of TurboJPEG for decoding and encoding JPEG image."""
    def __init__(self, lib_path=None):
        turbo_jpeg = cdll.LoadLibrary(
            DEFAULT_LIB_PATH[platform.system()] if lib_path is None else lib_path)
        self.__init_decompress = turbo_jpeg.tjInitDecompress
        self.__init_decompress.restype = c_void_p
        self.__init_compress = turbo_jpeg.tjInitCompress
        self.__init_compress.restype = c_void_p
        self.__destroy = turbo_jpeg.tjDestroy
        self.__destroy.argtypes = [c_void_p]
        self.__destroy.restype = c_int
        self.__decompress_header = turbo_jpeg.tjDecompressHeader3
        self.__decompress_header.argtypes = [
            c_void_p, POINTER(c_ubyte), c_ulong, POINTER(c_int),
            POINTER(c_int), POINTER(c_int), POINTER(c_int)]
        self.__decompress_header.restype = c_int
        self.__decompress = turbo_jpeg.tjDecompress2
        self.__decompress.argtypes = [
            c_void_p, POINTER(c_ubyte), c_ulong, POINTER(c_ubyte),
            c_int, c_int, c_int, c_int, c_int]
        self.__decompress.restype = c_int
        self.__compress = turbo_jpeg.tjCompress2
        self.__compress.argtypes = [
            c_void_p, POINTER(c_ubyte), c_int, c_int, c_int, c_int,
            POINTER(c_void_p), POINTER(c_ulong), c_int, c_int, c_int]
        self.__compress.restype = c_int
        self.__free = turbo_jpeg.tjFree
        self.__free.argtypes = [c_void_p]
        self.__free.restype = None
        self.__get_error_str = turbo_jpeg.tjGetErrorStr
        self.__get_error_str.restype = c_char_p

    def decode(self, jpeg_buf, pixel_format=TJPF_BGR):
        """decode JPEG memory buffer to numpy array."""
        handle = self.__init_decompress()
        try:
            pixel_size = [3, 3, 4, 4, 4, 4, 1, 4, 4, 4, 4, 4]
            width = c_int()
            height = c_int()
            jpeg_subsample = c_int()
            jpeg_colorspace = c_int()
            jpeg_array = np.frombuffer(jpeg_buf, dtype=np.uint8)
            src_addr = jpeg_array.ctypes.data_as(POINTER(c_ubyte))
            status = self.__decompress_header(
                handle, src_addr, jpeg_array.size, byref(width), byref(height),
                byref(jpeg_subsample), byref(jpeg_colorspace))
            if status != 0:
                raise IOError(self.__get_error_str().decode())
            img_array = np.empty(
                [height.value, width.value, pixel_size[pixel_format]],
                dtype=np.uint8)
            dest_addr = img_array.ctypes.data_as(POINTER(c_ubyte))
            status = self.__decompress(
                handle, src_addr, jpeg_array.size, dest_addr, width.value,
                0, height.value, pixel_format, 0)
            if status != 0:
                raise IOError(self.__get_error_str().decode())
            return img_array
        finally:
            self.__destroy(handle)

    def encode(self, img_array, quality=85, pixel_format=TJPF_BGR, jpeg_subsample=TJSAMP_422):
        """encode numpy array to JPEG memory buffer."""
        handle = self.__init_compress()
        try:
            jpeg_buf = c_void_p()
            jpeg_size = c_ulong()
            height, width, _ = img_array.shape
            src_addr = img_array.ctypes.data_as(POINTER(c_ubyte))
            status = self.__compress(
                handle, src_addr, width, 0, height, pixel_format,
                byref(jpeg_buf), byref(jpeg_size), jpeg_subsample, quality, 0)
            if status != 0:
                raise IOError(self.__get_error_str().decode())
            dest_buf = create_string_buffer(jpeg_size.value)
            memmove(dest_buf, jpeg_buf.value, jpeg_size.value)
            self.__free(jpeg_buf)
            return dest_buf.raw
        finally:
            self.__destroy(handle)

if __name__ == '__main__':
    jpeg = TurboJPEG()
    in_file = open('input.jpg', 'rb')
    img_array = jpeg.decode(in_file.read())
    in_file.close()
    out_file = open('output.jpg', 'wb')
    out_file.write(jpeg.encode(img_array))
    out_file.close()
    import cv2
    cv2.imshow('image', img_array)
    cv2.waitKey(0)