###### pl-analyser

Code to visualise PL maps.

`PLplotter_single_wav.py` - code used to analyse at PL maps at single wavelength.

`PLplotter_int_wavs.py` - code used to analyse integrated PL maps of the chosen wavelength range.

How to use the code:
1. Run the code and wait for figure to open.
2. PL map is displayed on the right-hand side of the screen and the spectrum is on the left-hand side (spectrum subplot is empty until a point in PL map is clicked).
3. Click anywhere on the PL map and the marker will appear highlighting the position of the point just clicked. Spectrum of that point is displayed in spectrum subplot.
4. Click on the slider (sliders) below spectrum subplot to change the wavelength of PL map displayed on the right-hand side of the window (adjust wavelength range for integration).
5. Adjust limits of colorbars (yellow) by using yellow sliders (min and max).

To change file name for plotting data, edit the line at the top of the code (name = 'test2.sdm').

`pl-analyser-environment.yml` - conda environment file.
