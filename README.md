# PyTurboJPEG
A Python wrapper of libjpeg-turbo for decoding and encoding JPEG image.

## Prerequisites
- [libjpeg-turbo](https://github.com/libjpeg-turbo/libjpeg-turbo/releases)
- [numpy](https://github.com/numpy/numpy)

## Example

```python
import cv2
from turbojpeg import TurboJPEG, TJPF_GRAY, TJSAMP_GRAY, TJFLAG_PROGRESSIVE, TJFLAG_FASTUPSAMPLE, TJFLAG_FASTDCT

# specifying library path explicitly
# jpeg = TurboJPEG(r'D:\turbojpeg.dll')
# jpeg = TurboJPEG('/usr/lib64/libturbojpeg.so')
# jpeg = TurboJPEG('/usr/local/lib/libturbojpeg.dylib')

# using default library installation
jpeg = TurboJPEG()

# decoding input.jpg to BGR array
in_file = open('input.jpg', 'rb')
bgr_array = jpeg.decode(in_file.read())
in_file.close()
cv2.imshow('bgr_array', bgr_array)
cv2.waitKey(0)

# decoding input.jpg to BGR array with fast upsample and fast DCT. (i.e. fastest speed but lower accuracy)
in_file = open('input.jpg', 'rb')
bgr_array = jpeg.decode(in_file.read(), flags=TJFLAG_FASTUPSAMPLE|TJFLAG_FASTDCT)
in_file.close()
cv2.imshow('bgr_array', bgr_array)
cv2.waitKey(0)

# direct rescaling 1/2 while decoding input.jpg to BGR array
in_file = open('input.jpg', 'rb')
bgr_array_half = jpeg.decode(in_file.read(), scaling_factor=(1, 2))
in_file.close()
cv2.imshow('bgr_array_half', bgr_array_half)
cv2.waitKey(0)

# getting possible scaling factors for direct rescaling
scaling_factors = jpeg.scaling_factors

# decoding JPEG image properties
in_file = open('input.jpg', 'rb')
width, height, jpeg_subsample, jpeg_colorspace = jpeg.decode_header(in_file.read())
in_file.close()

# decoding input.jpg to YUV array
in_file = open('input.jpg', 'rb')
buffer_array, plane_sizes = jpeg.decode_to_yuv(in_file.read())
in_file.close()

# decoding input.jpg to YUV planes
in_file = open('input.jpg', 'rb')
planes = jpeg.decode_to_yuv_planes(in_file.read())
in_file.close()

# encoding BGR array to output.jpg with default settings.
out_file = open('output.jpg', 'wb')
out_file.write(jpeg.encode(bgr_array))
out_file.close()

# encoding BGR array to output.jpg with TJSAMP_GRAY subsample.
out_file = open('output_gray.jpg', 'wb')
out_file.write(jpeg.encode(bgr_array, jpeg_subsample=TJSAMP_GRAY))
out_file.close()

# encoding BGR array to output.jpg with quality level 50. 
out_file = open('output_quality_50.jpg', 'wb')
out_file.write(jpeg.encode(bgr_array, quality=50))
out_file.close()

# encoding BGR array to output.jpg with quality level 100 and progressive entropy coding.
out_file = open('output_quality_100_progressive.jpg', 'wb')
out_file.write(jpeg.encode(bgr_array, quality=100, flags=TJFLAG_PROGRESSIVE))
out_file.close()

# decoding input.jpg to grayscale array
in_file = open('input.jpg', 'rb')
gray_array = jpeg.decode(in_file.read(), pixel_format=TJPF_GRAY)
in_file.close()
cv2.imshow('gray_array', gray_array)
cv2.waitKey(0)

# scale with quality but leaves out the color conversion step
in_file = open('input.jpg', 'rb')
out_file = open('scaled_output.jpg', 'wb')
out_file.write(jpeg.scale_with_quality(in_file.read(), scaling_factor=(1, 4), quality=70))
out_file.close()
in_file.close()

# lossless crop image
out_file = open('lossless_cropped_output.jpg', 'wb')
out_file.write(jpeg.crop(open('input.jpg', 'rb').read(), 8, 8, 320, 240))
out_file.close()
```

```python
# using PyTurboJPEG with ExifRead to transpose an image if the image has an EXIF Orientation tag.
#
# pip install PyTurboJPEG -U
# pip install exifread -U

import cv2
import numpy as np
import exifread
from turbojpeg import TurboJPEG

def transposeImage(image, orientation):
    """See Orientation in https://www.exif.org/Exif2-2.PDF for details."""
    if orientation == None: return image
    val = orientation.values[0]
    if val == 1: return image
    elif val == 2: return np.fliplr(image)
    elif val == 3: return np.rot90(image, 2)
    elif val == 4: return np.flipud(image)
    elif val == 5: return np.rot90(np.flipud(image), -1)
    elif val == 6: return np.rot90(image, -1)
    elif val == 7: return np.rot90(np.flipud(image))
    elif val == 8: return np.rot90(image)

# using default library installation
turbo_jpeg = TurboJPEG()
# open jpeg file
in_file = open('foobar.jpg', 'rb')
# parse orientation
orientation = exifread.process_file(in_file).get('Image Orientation', None)
# seek file position back to 0 before decoding JPEG image
in_file.seek(0)
# start to decode the JPEG file
image = turbo_jpeg.decode(in_file.read())
# transpose image based on EXIF Orientation tag
transposed_image = transposeImage(image, orientation)
# close the file since it's no longer needed.
in_file.close()

cv2.imshow('transposed_image', transposed_image)
cv2.waitKey(0)
```

## Installation

### macOS
- brew install jpeg-turbo
- pip install -U git+git://github.com/lilohuang/PyTurboJPEG.git

### Windows 
- Download [libjpeg-turbo official installer](https://sourceforge.net/projects/libjpeg-turbo/files) 
- pip install -U git+git://github.com/lilohuang/PyTurboJPEG.git

### Linux
- RHEL/CentOS/Fedora
  - Download [libjpeg-turbo.repo](https://libjpeg-turbo.org/pmwiki/uploads/Downloads/libjpeg-turbo.repo) to /etc/yum.repos.d/
  - sudo yum install libjpeg-turbo-official
  - pip install -U git+git://github.com/lilohuang/PyTurboJPEG.git

- Ubuntu
  - sudo apt-get update
  - sudo apt-get install libturbojpeg
  - pip install -U git+git://github.com/lilohuang/PyTurboJPEG.git

## Benchmark 

### macOS
- macOS Sierra 10.12.6
- Intel(R) Core(TM) i5-3210M CPU @ 2.50GHz
- opencv-python 3.4.0.12 (pre-built)
- turbo-jpeg 1.5.3 (pre-built)

| Function              | Wall-clock time |
| ----------------------|-----------------|
| cv2.imdecode()        |   0.528 sec     |
| TurboJPEG.decode()    |   0.191 sec     |
| cv2.imencode()        |   0.875 sec     |
| TurboJPEG.encode()    |   0.176 sec     |

### Windows 
- Windows 7 Ultimate 64-bit
- Intel(R) Xeon(R) E3-1276 v3 CPU @ 3.60 GHz
- opencv-python 3.4.0.12 (pre-built)
- turbo-jpeg 1.5.3 (pre-built)

| Function              | Wall-clock time |
| ----------------------|-----------------|
| cv2.imdecode()        |   0.358 sec     |
| TurboJPEG.decode()    |   0.135 sec     |
| cv2.imencode()        |   0.581 sec     |
| TurboJPEG.encode()    |   0.140 sec     |
