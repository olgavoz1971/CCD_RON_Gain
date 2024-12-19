"""
### Method:
The gain (in e-/ADU) is estimated using two consecutive light frames.
By subtracting these frames, we isolate the photon noise and the readout noise (RON).
The photon noise follows a Poisson distribution, and the readout noise is assumed to be constant.
The gain is calculated using the formula:

Gain (e-/ADU) = (average photon count) / (variance of the difference / 2 - RON^2)

Where:
  - count = median signal value of the light frames.
  - sigma = standard deviation of the difference between the two frames (photon noise).
  - RON = readout noise in ADU.

This method assumes the light frames are equally exposed and that the readout noise is constant.

### Parameters and Outputs:
- `filename1`, `filename2`: Paths to two consecutive light frames.
- `window`: A selected region of the CCD (e.g., `x0, x1, y0, y1`) to avoid edge effects
  and obtain a more accurate measurement.
- `ron_adu`: The estimated readout noise in ADU for a single frame

The second method for estimating the gain involves fitting a linear model to the relationship
between the squared noise (sigma^2) and the average signal (count) for light frames.
The noise is dominated by photon noise, and the relationship between noise and signal
is assumed to be linear.

The gain (in e-/ADU) is estimated as the inverse of twice the slope (k) of the fitted line:

Gain (e-/ADU) = 1 / (2 * k)

Where:
  - sigma^2 = variance (squared noise) of the frames (sigma^2 = (sigma^2 of the diff. light frames) / 2 - RON^2)
  - count = mean signal (average counts in ADU),
  - k = slope of the fitted line.

This method can also help identify non-linearity in the detector response, as deviations
from a straight-line relationship may indicate non-linear behavior.

"""


import sys
from os.path import basename
from astropy.io import fits
import numpy as np


def preprocess_light(filename, superbias_data):
    with fits.open(filename) as hdu:
        header = hdu[0].header
        exptime = header['EXPTIME']
        data = np.array((hdu[0].data - superbias_data), dtype='float')
        return exptime, data


def calc_gain(filename1, filename2, filename_superbias, ron_adu, window):
    x0, x1, y0, y1 = window
    with fits.open(filename_superbias) as hdu:
        superbias_data = hdu[0].data
    exptime1, data1 = preprocess_light(filename1, superbias_data)
    exptime2, data2 = preprocess_light(filename2, superbias_data)

    count1 = np.median(data1[y0:y1, x0:x1])
    count2 = np.median(data2[y0:y1, x0:x1])
    # print(np.max(data1[y0:y1, x0:x1]), np.max(data2[y0:y1, x0:x1]))
    count = (count1 + count2) / 2.0

    data_diff = data1 - (data2 / count2) * count1
    fits.writeto(f'light_diff_{basename(filename1).replace(".fit", "")}_'
                 f'{basename(filename2).replace(".fit", "")}.fits',
                 data_diff, overwrite=True)

    sigma = np.std(data_diff[y0:y1, x0:x1], ddof=1)
    median = np.median(data_diff[y0:y1, x0:x1])
    gain = count / (sigma ** 2 / 2 - ron_adu ** 2)
    ron_e = ron_adu * gain
    print(f'light {count=:7.1f}  sigma^2 {sigma ** 2 / 2 - ron_adu ** 2:7.2f} '
          f'{median=:5.2f} ADU {gain=:5.2f}, {ron_e=:5.2f} '
          f'{basename(filename1).replace(".fit", "")} '
          f'{basename(filename2).replace(".fit", "")}')

    return gain


# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='Calculate Gain and RON from pairs of light and bias images')
#     parser.add_argument('light1', type=str, help="name of the first light file")
#     parser.add_argument('light2', type=str, help="name of the second light file")
#     parser.add_argument('--superbias', type=str, default='superbias_default.fits',
#                         help="master bias file, if not set, we take bias1")
#     parser.add_argument('--ron_adu', type=float, default=2.21, help='input RON in ADU')
#     parser.add_argument(
#         '--win',
#         type=lambda s: tuple(map(int, s.split(','))),
#         default=(1200, 1700, 1600, 2100),
#         help='cut out image: x_beg, x_end, y_beg, y_end'
#     )
#     args = parser.parse_args()
#     calc_gain(args.light1, args.light2, args.superbias, args.ron_adu, args.win)

win_ccd1 = (1200, 1700, 1600, 2100)
win_ccd2 = (2052, 2552, 2417, 2917)
win_ccd3 = (2417, 2917, 2052, 2552)

ron_ccd1 = 2.21
ron_ccd2 = 2.00

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('The first argument must be the name of file containing a sequential list of light fits-files, '
              'taken quasi-simultaneously')
        sys.exit(1)
    input_file = sys.argv[1]
    if len(sys.argv) > 2:
        superbias_filename = sys.argv[2]
    else:
        superbias_filename = 'superbias_default.fits'
    if len(sys.argv) > 3:
        ron_in_adu = float(sys.argv[3])
    else:
        ron_in_adu = ron_ccd1
    win = win_ccd1
    with open(input_file, 'r') as f:
        fits_files = [line.strip() for line in f if line.strip()]

    gain_list = []
    for i in range(len(fits_files) - 1):
        file1 = fits_files[i]
        file2 = fits_files[i + 1]
        gain_list.append(calc_gain(file1, file2, superbias_filename, ron_in_adu, win))

    print(f'median gain={np.median(gain_list):7.3f} mean gain={np.mean(gain_list):5.3f}')
