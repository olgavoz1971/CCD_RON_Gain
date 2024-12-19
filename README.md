# CCD Noise and Gain Estimation

This repository contains Python scripts for estimating the Readout Noise (RON) and Gain of a CCD camera using light and bias frames. These methods are commonly used to characterize detector noise and response.

## Scripts

### RON Estimation Script (`estimate_ron.py`)

This script estimates the Readout Noise (RON) of the CCD camera from two consecutive bias frames (with zero exposure time). The method uses the standard deviation of the difference between the two frames, and the resulting RON is expressed in ADU (Analog-to-Digital Units).

**Main Formula:**
Main Formula:

$$
\text{RON (in ADU)} = \frac{\sigma}{\sqrt{2}}
$$

where $\sigma\$ is the standard deviation of the pixel differences within a given region of interest.

### Gain Estimation Script (`estimate_gain.py`)

This script estimates the Gain (in e-/ADU) of the CCD camera.
The photon noise follows a Poisson distribution, and the readout noise is assumed to be constant.


#### Method 1: Using the Noise-Signal Relationship

This method involves fitting a linear model to the relationship
between the squared noise $\sigma^2$ and the average signal (count) for light frames.
The noise is dominated by photon noise and the relationship between noise and signal
is assumed to be linear.

The Gain is calculated as the inverse of twice the slope of the fitted line.

**Main Formula:**

$$
\text{Gain (in e-/ADU)} = \frac{1}{2 \cdot k}
$$

where k is the slope of the fitted line between σ² (variance) and the signal (mean count in ADU).

This method can also help identify non-linearity in the detector response, as deviations
from a straight-line relationship may indicate non-linear behaviour.


#### Method 2: Using the Noise from Frame Differences

By subtracting these frames, we isolate the photon noise and the readout noise (RON).
This method assumes the light frames are equally exposed, the photon noise follows a Poisson distribution and the readout noise is constant.

The gain is calculated using the formula:

$$
\text{Gain (e-/ADU)} = \frac{\text{count}}{\sigma^2}
$$

Where:
  - $count$ = median signal value of the light frames.
  - $\sigma$ = standard deviation of the difference between the two frames (photon noise).
  - $RON$ = readout noise in ADU

$$
\sigma^2 = \frac{\sigma^2_{\text{difference between two light frames}}}{2} - \text{RON}^2
$$


## Requirements

- Python 3.x
- `numpy`
- `astropy`
- `scipy`

## Usage

To estimate RON from two consecutive bias frames, run the following command:

```bash
python estimate_ron.py bias_frame1.fits bias_frame2.fits
```
To estimate Gain from two consecutive light frames, run the following command:
```bash
python estimate_gain.py light_frame1.fits light_frame2.fits superbias_frame.fits
```
Where superbias_frame.fits is the master bias frame used for preprocessing.
