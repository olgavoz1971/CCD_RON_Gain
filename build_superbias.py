import os
import sys
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
import numpy as np


def build_superbias(fits_files, output_file='superbias.fits'):
    data_list = []
    for file in fits_files:
        with fits.open(file) as hdul:
            data_list.append(hdul[0].data)
    stack = np.array(data_list)
    sigma = 3
    maxiters = 5
    mean_image, _, _ = sigma_clipped_stats(stack, sigma=sigma, maxiters=maxiters, axis=0)
    hdu = fits.PrimaryHDU(mean_image)
    hdu.writeto(output_file, overwrite=True)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('The first argument must be the name of file containing a list of fits-files')
        sys.exit(1)

    input_file = sys.argv[1]
    master_bias = os.path.splitext(input_file)[0] + '.fits'
    with open(input_file, 'r') as f:
        files = [line.strip() for line in f if line.strip()]

    build_superbias(files, output_file=master_bias)

