import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable


name = 'test2.sdm'  # name of the data file

mpl.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 14
plt.rcParams['axes.linewidth'] = 1
plt.rcParams["figure.figsize"] = (10,7)

class PLmap():
    def __init__(self, name):
        self.name = name

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
        self.wav = np.float_(self.first_line.strip('\n').split('\t'))  # transform the first line into numpy array

        first = [0, 1, 2]  # indices of elements to be removed
        end = len(self.wav) - len(self.data[0])

        self.wav = np.delete(self.wav, first)
        for i in range(end):
            self.wav = self.wav[:-1]

    def find_wav(self, lambda0):
        difference = np.abs(self.wav - lambda0)
        minimum_ind = np.where(difference == np.amin(difference))[0][0]
        return minimum_ind

    def find_spectrum(self, xs, ys):
        xycoords = self.data[:, :2]

        xdifference = np.abs(xycoords[:,0]-xs)
        ydifference = np.abs(xycoords[:,1]-ys)

        xminimum = np.where(xdifference == np.amin(xdifference))
        yminimum = np.where(ydifference == np.amin(ydifference))

        xymin = np.intersect1d(xminimum, yminimum)

        return xymin

    def map(self, lambda0):
        self.x, self.y = self.extract_coordinates()
        X, Y = np.meshgrid(self.x, self.y)

        ind = self.find_wav(lambda0)
        self.wv = self.wav[ind]

        self.fig = plt.figure()
        map_data = np.reshape(self.data[:,ind], (len(self.y), len(self.x)))

        self.ax = plt.subplot2grid((5, 5), (0, 2), colspan=3, rowspan=4)

        self.cax = make_axes_locatable(self.ax).append_axes("right", size="5%", pad="2%")
        cf = self.ax.contourf(X, Y, map_data, cmap='Blues', levels=50)
        self.cbar = self.fig.colorbar(cf, cax=self.cax)
        self.map_labels()
        self.ax.set_title(f'Map @ {self.wav[ind]} nm')

        self.ax2 = plt.subplot2grid((5, 5), (1, 0), colspan=2, rowspan=2)

        self.fig.canvas.mpl_connect('button_press_event', self.onclick)

        self.hbar, = self.ax.plot((self.x[0], self.x[-1]), [max(self.y), max(self.y)], 'r--')
        self.vbar, = self.ax.plot([max(self.x), max(self.x)], (self.y[0], self.y[-1]), 'r--')

        plt.tight_layout()
        plt.show()

    def onclick(self, event):
        if event.inaxes==self.ax:
            self.ix, self.iy = event.xdata, event.ydata
            print(f'x = {self.ix}, y = {self.iy}.')

            self.xindex = np.where(self.x < event.xdata)[0][-1]
            self.yindex = np.where(self.y < event.ydata)[0][-1]
            self.hbar.set_ydata([self.y[self.yindex], self.y[self.yindex]])
            self.vbar.set_xdata([self.x[self.xindex], self.x[self.xindex]])

            spectrumind = self.find_spectrum(self.ix, self.iy)
            spectrum = self.data[spectrumind,:][0,2:-1]
            self.ax2.clear()
            self.ax2.plot(self.wav, spectrum)

            if self.madeplot and self.clickedspectrum:
                newwav = self.wav[self.newind]
            else:
                newwav = self.wv

            self.svbar, = self.ax2.plot([newwav, newwav], (np.amin(self.data), 1.1*np.amax(self.data)), 'k--')
            self.spectrum_labels()

            self.fig.canvas.draw()
            self.madeplot = True

        if event.inaxes==self.ax2 and self.madeplot:
            self.clickedspectrum = True
            self.lam, self.int = event.xdata, event.ydata
            print(f'lambda = {self.lam}, int = {self.int}.')

            self.newind = self.find_wav(self.lam)
            self.svbar.set_xdata([self.wav[self.newind], self.wav[self.newind]])

            self.ax.clear()
            self.ax2.clear()
            self.cax.clear()

            self.hbar, = self.ax.plot((self.x[0], self.x[-1]), [max(self.y), max(self.y)], 'r--')
            self.vbar, = self.ax.plot([max(self.x), max(self.x)], (self.y[0], self.y[-1]), 'r--')
            self.hbar.set_ydata([self.y[self.yindex], self.y[self.yindex]])
            self.vbar.set_xdata([self.x[self.xindex], self.x[self.xindex]])

            X, Y = np.meshgrid(self.x, self.y)
            map_data = np.reshape(self.data[:,self.newind], (len(self.y), len(self.x)))
            cf = self.ax.contourf(X, Y, map_data, cmap='Blues', levels=50)
            self.cbar = self.fig.colorbar(cf, cax=self.cax)

            self.map_labels()
            self.ax.set_title(f'Map @ {self.wav[self.newind]} nm')

            spectrumind = self.find_spectrum(self.ix, self.iy)
            spectrum = self.data[spectrumind, :][0, 2:-1]
            self.ax2.plot(self.wav, spectrum)
            self.svbar, = self.ax2.plot([self.wav[self.newind], self.wav[self.newind]], (np.amin(self.data), 1.1 * np.amax(self.data)), 'k--')
            self.svbar.set_xdata([self.wav[self.newind], self.wav[self.newind]])
            self.spectrum_labels()

            self.fig.canvas.draw()

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
        self.ax2.grid(True)


if __name__ == '__main__':
    plotter = PLmap(name)

    plotter.extract_wavelengths()
    plotter.map(780)