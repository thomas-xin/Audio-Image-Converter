# Audio-Image-Converter

Converts audio to and from a square image representing the time-frequency domain. Achieves almost 50% compression ratio on most files with almost completely transparent reconstruction, especially in HSV mode.

The image represents the fourier transform of the audio, with X axis representing time, Y axis representing frequency, hue representing phase, and amplitude being represented as a floating-point number of base 1.03125, with value as the mantissa and inverse saturation as the exponent.

Of course this isn't completely lossless; there are only 256 possible hue angles, which decreases with lowered saturation, and rises with the value/luminance of the colour, meaning that the wave phases will be very slightly off, especially for extremely soft and extremely loud sounds (both cases of which the phase won't matter as much, which is why I made such a choice to store the values this way). The conversion between hsv and rgb itself is a lossy process, and nearly all the calculations in this program are done with single precision floats, and then truncated, which results in very slight quality loss as well.

All in all, I think this does pretty well still, especially compared to my first few attempts which basically flooded the audio with popping and crackling sounds 🙃
