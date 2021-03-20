import os, sys, time, subprocess, numpy
from PIL import Image
np = numpy

is_url = lambda url: "://" in url and url.split("://", 1)[0].rstrip("s") in ("http", "hxxp", "ftp", "fxp")
ffmpeg_start = ("ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-fflags", "+discardcorrupt+fastseek+genpts+igndts+flush_packets", "-err_detect", "ignore_err", "-hwaccel", "auto", "-vn")

hsv = sys.argv[-1] != "-hsv"
if not hsv:
    sys.argv.pop(-1)
if len(sys.argv) > 1:
    fn = sys.argv[1]
else:
    fn = input("Please input a filename or URL: ")

if len(sys.argv) > 2:
    fo = sys.argv[2]
    pcm = fo.endswith(".pcm")
else:
    fo = fn.rsplit("/", 1)[-1].split("?", 1)[0].rsplit(".", 1)[0] + ".wav"
    pcm = False

if is_url(fn):
    fi, fn = fn, "temp.tmp"
    subprocess.run(("py", "downloader.py", fi, fn))
    fn = "files/" + fn

if not pcm:
    cmd = ffmpeg_start + ("-f", "f32le", "-ac", "2", "-ar", "48k", "-i", "-", fo)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
else:
    f = open(fo, "wb")
img = Image.open(fn)
dfts = img.height >> 1
ffts = dfts - 1 << 1
# print(dfts, ffts)
if hsv:
    img = img.convert("HSV")

columns = np.asarray(img, dtype=np.float32)
for img in columns.swapaxes(0, 1):
    hue, sat, val = img[:len(img) // 2 << 1].T[:3]
    hue -= 128
    hue *= np.pi / 128
    phase = hue
    sat[sat == 0] = 255
    np.subtract(255, sat, out=sat)
    np.power(1.03125, sat, out=sat)
    val *= sat
    val *= ffts / 255 / 4096
    amplitude = val
    cpl = np.multiply(phase, 1j)
    np.exp(cpl, out=cpl)
    cpl *= amplitude
    lft, rft = cpl[::2], cpl[1::2]
    left, right = np.fft.irfft(lft[::-1]), np.fft.irfft(rft[::-1])
    arr = np.empty(ffts << 1, dtype=np.float32)
    arr[::2] = left
    arr[1::2] = right
    if pcm:
        arr *= 32767
        b = arr.astype(np.int16).tobytes()
        f.write(b)
    else:
        b = arr.tobytes()
        p.stdin.write(b)

if pcm:
    f.close()
else:
    p.stdin.close()