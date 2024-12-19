"""
### Method:

1. **Bias Frames**: Bias frames are images taken with zero exposure time, capturing
   only the readout noise of the CCD camera. By analyzing the difference between
   two consecutive bias frames, we can isolate the readout noise component.

2. **Readout Noise Calculation**:
   To calculate the readout noise in Analog-to-Digital Units (ADU), we subtract
   two consecutive bias frames:

   data_diff = data1 - data2

   where `data1` and `data2` are the pixel values of the first and second bias frames, respectively.

3. **Readout Noise in ADU**:
   The standard deviation of the resulting difference image (`data_diff`) reflects the
   readout noise from both frames. Since noise is combined from each frame independently,
   we divide the standard deviation by \( \sqrt{2} \) to obtain the readout noise for a single frame:

   ron_adu = sigma / sqrt(2)

   where `sigma` is the standard deviation of `data_diff`.

### Parameters and Outputs:
- `filename_bias1`, `filename_bias2`: Paths to two consecutive bias frames.
- `window`: A selected region of the CCD (e.g., `x0, x1, y0, y1`) to avoid edge effects
  and obtain a more accurate measurement.
- `ron_adu`: The estimated readout noise in ADU for a single frame, useful for camera
  calibration and performance characterization.

The computed readout noise can then be used in further analyses to characterize the CCD camera's
sensitivity and noise behavior.
"""

import sys
from os.path import basename

import numpy as np
from astropy.io import fits


def calc_ron(filename_bias1, filename_bias2, window):
    x0, x1, y0, y1 = window
    with fits.open(filename_bias1) as hdu1:
        data1 = np.array(hdu1[0].data, dtype='float')
    with fits.open(filename_bias2) as hdu2:
        data2 = np.array(hdu2[0].data, dtype='float')
    data_diff = data1 - data2
    fits.writeto(f'bias_diff_{basename(filename_bias1).replace(".fit", "")}_'
                 f'{basename(filename_bias2).replace(".fit", "")}.fits',
                 data_diff, overwrite=True)
    sigma = np.std(data_diff[y0:y1, x0:x1], ddof=1)
    median = np.median(data_diff[y0:y1, x0:x1])
    mean = np.mean(data_diff[y0:y1, x0:x1])
    ron_adu = sigma / np.sqrt(2)
    print(f'{filename_bias1} {basename(filename_bias2)} difference: {median=:7.3f} {mean=:7.3f} {ron_adu=:5.3f}')
    return ron_adu


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Calculate Gain and RON from pairs of light and bias images')
#     parser.add_argument('bias1', type=str, help="name of the first bias file")
#     parser.add_argument('bias2', type=str, help="name of the second bias file")
#     parser.add_argument(
#         '--win',
#         type=lambda s: tuple(map(int, s.split(','))),
#         default=(1200, 1700, 1600, 2100),
#         help='cut out image: x_beg, x_end, y_beg, y_end'
#     )
#     args = parser.parse_args()
#     ron_in_adu = calc_ron(args.bias1, args.bias2, args.win)

win_ccd1 = (1200, 1700, 1600, 2100)
win_ccd2 = (2417, 2917, 2052, 2552)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('The first argument must be the name of file containing a sequential list of bias fits-files, '
              'taken quasi-simultaneously')
        sys.exit(1)

    input_file = sys.argv[1]
    win = win_ccd1
    with open(input_file, 'r') as f:
        fits_files = [line.strip() for line in f if line.strip()]

    ron = []
    for i in range(len(fits_files) - 1):
        file1 = fits_files[i]
        file2 = fits_files[i + 1]
        ron.append(calc_ron(file1, file2, win))

    print(f'{np.median(ron)=:5.3f} {np.mean(ron)=:5.3f}')
