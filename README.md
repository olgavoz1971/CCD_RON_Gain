# CCD Noise and Gain Estimation

This repository contains Python scripts for estimating the Readout Noise (RON) and Gain of a CCD camera using light and bias frames. These methods are commonly used to characterize detector noise and response.

## Scripts

### RON Estimation Script (`estimate_ron.py`)

This script estimates the Readout Noise (RON) of the CCD camera from two consecutive bias frames (with zero exposure time). The method uses the standard deviation of the difference between the two frames, and the resulting RON is expressed in ADU (Analog-to-Digital Units).

**Main Formula:**

\[
\text{RON (in ADU)} = \frac{\sigma}{\sqrt{2}}
\]

where \(\sigma\) is the standard deviation of the pixel differences within a given region of interest.

### Gain Estimation Script (`estimate_gain.py`)

This script estimates the Gain (in e\-/ADU) of the CCD camera using two consecutive light frames with known exposure times. The method assumes that photon noise follows a Poisson distribution.

#### Method 1: Using the Noise-Signal Relationship

The script fits a linear model to the relationship between the squared noise and the signal. The Gain is calculated as the inverse of twice the slope of the fitted line.

**Main Formula:**

\[
\text{Gain (in e\-/ADU)} = \frac{1}{2 \cdot k}
\]

where \(k\) is the slope of the fitted line between \(\sigma^2\) (variance) and the signal (mean count in ADU).

#### Method 2: Using the Noise from Frame Differences

The second method calculates the squared noise (\(\sigma^2\)) from the difference between two consecutive light frames and uses it in a similar fitting approach to estimate the Gain.

## Requirements

- Python 3.x
- `numpy`
- `astropy`
- `scipy`
