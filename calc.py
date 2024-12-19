from os.path import basename
from astropy.io import fits
import numpy as np
import argparse


def preprocess_light(filename, superbias_data):
    with fits.open(filename) as hdu:
        header = hdu[0].header
        exptime = header['EXPTIME']
        print(f'{filename=} {exptime=}')
        data = np.array((hdu[0].data - superbias_data), dtype='float')
        return data


def calc_ron(filename_bias1, filename_bias2, window):
    x0, x1, y0, y1 = window
    with fits.open(filename_bias1) as hdu1:
        data1 = np.array(hdu1[0].data, dtype='float')
    with fits.open(filename_bias2) as hdu2:
        data2 = np.array(hdu2[0].data, dtype='float')
    data_diff = data1 - data2
    fits.writeto(f'bias_diff_{basename(filename_bias1).replace(".fit", "")}_'
                 f'{basename(filename_bias2).replace(".fit", "")}',
                 data_diff, overwrite=True)
    sigma = np.std(data_diff[y0:y1, x0:x1], ddof=1)
    median = np.median(data_diff[y0:y1, x0:x1])
    mean = np.mean(data_diff[y0:y1, x0:x1])
    ron_adu = sigma / np.sqrt(2)
    print(f'Bias {median=:5.3f} {mean=:5.3f}')
    return ron_adu


def calc_gain(filename1, filename2, filename_superbias, ron_adu, window):
    x0, x1, y0, y1 = window
    with fits.open(filename_superbias) as hdu:
        superbias_data = hdu[0].data
    data1 = preprocess_light(filename1, superbias_data)
    data2 = preprocess_light(filename2, superbias_data)

    count1 = np.median(data1[y0:y1, x0:x1])
    count2 = np.median(data2[y0:y1, x0:x1])
    count = (count1 + count2) / 2.0

    data_diff = data1 - data2 / count2 * count1
    fits.writeto(f'light_diff_{basename(filename1).replace(".fit", "")}_'
                 f'{basename(filename2).replace(".fit", "")}',
                 data_diff, overwrite=True)
    fits.writeto('light_diff.fits', data_diff, overwrite=True)

    sigma = np.std(data_diff[y0:y1, x0:x1], ddof=1)
    median = np.median(data_diff[y0:y1, x0:x1])
    gain = count / (sigma ** 2 / 2 - ron_adu ** 2)
    ron_e = ron_adu * gain
    print(f'light {median=:5.2f} ADU {gain=:5.2f}, {ron_adu=:5.2f} {ron_e=:5.2f}')

    return gain


def main(args):
    ron_adu = calc_ron(args.bias1, args.bias2, args.win)
    gain = calc_gain(args.light1, args.light2, args.superbias, ron_adu, args.win)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate Gain and RON from pairs of light and bias images')
    parser.add_argument('bias1', type=str, help="name of the first bias file")
    parser.add_argument('bias2', type=str, help="name of the second bias file")
    parser.add_argument('light1', type=str, help="name of the first light file")
    parser.add_argument('light2', type=str, help="name of the second light file")
    parser.add_argument('--superbias', type=str, help="master bias file, if not set, we take bias1")
    parser.add_argument(
        '--win',
        type=lambda s: tuple(map(int, s.split(','))),
        default=(1200, 1700, 1600, 2100),
        help='cut out image: x_beg, x_end, y_beg, y_end'
    )
    arguments = parser.parse_args()

    arguments.superbias = arguments.superbias if arguments.superbias is not None else arguments.bias1
    main(arguments)
