import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
plt.style.use('nature.mplstyle')    # use custom style defined in "nature.mplstyle"

name = 'test2.sdm'  # name of the data file

class PLmap():
    def __init__(self):
        # Reading a file (every line is a separate string)
        with open(name, 'r') as file:
            self.first_line = file.readline()
            self.data = file.readlines()
        print('Finished reading a file.')

        # Converting each line of data into numpy float array
        for i, line in enumerate(self.data):
            self.data[i] = np.float_(self.data[i].strip('\n').split('\t'))

        self.data.pop()  # remove the last line because it had (0,0,0) cordinates
        self.data = np.array(self.data)

        self.madeplot = False
        self.clickedspectrum = False

    def extract_coordinates(self):
        y = np.unique(self.data[:, 1])
        x = self.data[:,0][0:len(y)]
        return x, y

    def extract_wavelengths(self):
        wav = np.float_(self.first_line.strip('\n').split('\t'))  # transform the first line into numpy array

        first = [0, 1, 2]  # indices of elements to be removed
        end = len(wav) - len(self.data[0])

        wav = np.delete(wav, first)
        for i in range(end):
            wav = wav[:-1]

        return wav

    def find_wav(self, lambda0):
        difference = np.abs(self.wav - lambda0)
        minimum_ind = np.where(difference == np.amin(difference))[0][0]
        return minimum_ind

    def find_spectrum(self, xs, ys):
        '''
        Selects the first two columns of data array and finds (x,y) of the point selected in PL map
        :param xs and ys: (x,y) coordinates of the point in PL map
        :return: the index of row where the spectrum of selected point is located
        '''
        xycoords = self.data[:, :2]

        xdifference = np.abs(xycoords[:,0]-xs)
        ydifference = np.abs(xycoords[:,1]-ys)

        xminimum = np.where(xdifference == np.amin(xdifference))
        yminimum = np.where(ydifference == np.amin(ydifference))

        xymin = np.intersect1d(xminimum, yminimum)

        return xymin

    def generate_map(self):
        if self.madeplot and self.clickedspectrum:
            ind = self.newind
        else:
            ind = self.wind

        map_data = np.reshape(self.data[:, ind], (len(self.y), len(self.x)))
        cf = self.ax.pcolormesh(self.X, self.Y, map_data, cmap='afmhot', shading='auto')
        self.cbar = self.fig.colorbar(cf, cax=self.cax)
        self.map_labels()
        self.ax.set_title(f'Map @ {self.wav[ind]} nm')

        self.hbar, = self.ax.plot((self.x[0], self.x[-1]), [max(self.y), max(self.y)], 'r--')
        self.vbar, = self.ax.plot([max(self.x), max(self.x)], (self.y[0], self.y[-1]), 'r--')

    def plot_map(self, lambda0):
        self.x, self.y = self.extract_coordinates()
        self.wav = self.extract_wavelengths()
        self.X, self.Y = np.meshgrid(self.x, self.y)
        self.wind = self.find_wav(lambda0)  # wavelength index

        self.fig = plt.figure()

        self.ax = plt.subplot2grid((5, 5), (0, 2), colspan=3, rowspan=4)
        self.cax = make_axes_locatable(self.ax).append_axes("right", size="5%", pad="2%")
        self.ax2 = plt.subplot2grid((5, 5), (1, 0), colspan=2, rowspan=2)

        self.generate_map()

        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        plt.tight_layout()
        plt.show()

    def onclick(self, event):
        if event.inaxes==self.ax:
            self.ix, self.iy = event.xdata, event.ydata
            print(f'x = {self.ix}, y = {self.iy}.')

            self.xindex = np.where(self.x < event.xdata)[0][-1]
            self.yindex = np.where(self.y < event.ydata)[0][-1]

            self.update_map_marker()

            spectrumind = self.find_spectrum(self.ix, self.iy)
            spectrum = self.data[spectrumind,:][0,2:-1]
            self.ax2.clear()
            self.ax2.plot(self.wav, spectrum)

            if self.madeplot and self.clickedspectrum:
                self.newwav = self.wav[self.newind]
            else:
                self.newwav = self.wav[self.wind]

            self.svbar, = self.ax2.plot([self.newwav, self.newwav], (np.amin(self.data), 1.1*np.amax(self.data)), 'k--')
            self.spectrum_labels()

            self.fig.canvas.draw()
            self.madeplot = True

        if event.inaxes == self.ax2 and self.madeplot:
            self.clickedspectrum = True
            self.lam, self.int = event.xdata, event.ydata
            print(f'lambda = {self.lam}, int = {self.int}.')

            self.newind = self.find_wav(self.lam)
            self.svbar.set_xdata([self.wav[self.newind], self.wav[self.newind]])

            self.clear_all_axes()

            self.generate_map()
            self.update_map_marker()

            spectrumind = self.find_spectrum(self.ix, self.iy)
            spectrum = self.data[spectrumind, :][0, 2:-1]
            self.ax2.plot(self.wav, spectrum)
            self.svbar, = self.ax2.plot([self.wav[self.newind], self.wav[self.newind]], (np.amin(self.data), 1.1 * np.amax(self.data)), 'k--')
            self.svbar.set_xdata([self.wav[self.newind], self.wav[self.newind]])
            self.spectrum_labels()

            self.fig.canvas.draw()

    def update_map_marker(self):
        self.hbar.set_ydata([self.y[self.yindex], self.y[self.yindex]])
        self.vbar.set_xdata([self.x[self.xindex], self.x[self.xindex]])

    def map_labels(self):
        self.ax.set_xlabel('x (mm)')
        self.ax.set_ylabel('y (mm)')
        self.ax.set_aspect(1)

    def spectrum_labels(self):
        self.ax2.set_title('Spectrum')
        self.ax2.set_xlim(np.amin(self.wav), np.amax(self.wav))
        self.ax2.set_ylim(-50, 1.1*np.amax(self.data))

        self.ax2.set_xlabel('$\lambda$ (nm)')
        self.ax2.set_ylabel('Intensity (a.u.)')

    def clear_all_axes(self):
        self.ax.clear()
        self.ax2.clear()
        self.cax.clear()


if __name__ == '__main__':
    plotter = PLmap()
    plotter.plot_map(780)
