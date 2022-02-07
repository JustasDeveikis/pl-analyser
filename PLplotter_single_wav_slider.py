import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from matplotlib.widgets import Button, Slider
import matplotlib as mpl
from pylab import cm

mpl.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 16
plt.rcParams['axes.linewidth'] = 2
colors = cm.get_cmap('tab10', 2)
plt.rcParams["figure.figsize"] = (9,9)#(18,6)

colormap = 'afmhot'
name = 'test2.sdm'  # name of the data file

class PLmap():
    def __init__(self):
        # Reading a file (every line is a separate string)
        with open(name, 'r') as file:
            self.first_line = file.readline()
            self.data = file.readlines()
        print(f'Finished reading {name}.')

        # Converting each line of data into numpy float array
        for i, line in enumerate(self.data):
            self.data[i] = np.float_(self.data[i].strip('\n').split('\t'))

        self.data.pop()  # remove the last line because it had (0,0,0) cordinates
        self.data = np.array(self.data)

        self.clickedmap = False
        self.clickedspectrum = False
        
        self.png_no = 1

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
        if self.clickedmap and self.clickedspectrum:
            ind0 = self.newind0
            ind = self.newind
        else:
            ind0 = self.wind0
            ind = self.wind
        
        global map_data
        
        map_data = np.zeros((len(self.y), len(self.x)))
        ind_arr = np.arange(ind0, ind)
        for ind in ind_arr:
            md = np.reshape(self.data[:, ind], (len(self.y), len(self.x)))
            map_data = map_data + md
        
        
        # map_data = np.reshape(self.data[:, ind], (len(self.y), len(self.x)))
        cf = self.ax.pcolormesh(self.X, self.Y, map_data, cmap=colormap, shading='auto')
        self.cbar = self.fig.colorbar(cf, cax=self.cax)
        self.map_labels()
        self.ax.set_title(f'Map int from {self.wav[ind0]} to {self.wav[ind]} nm.')

        self.hbar, = self.ax.plot((self.x[0], self.x[-1]), [max(self.y), max(self.y)], 'k--')
        self.vbar, = self.ax.plot([max(self.x), max(self.x)], (self.y[0], self.y[-1]), 'k--')

    def plot_map(self, lambda0, lambda1):
        self.x, self.y = self.extract_coordinates()
        self.wav = self.extract_wavelengths()
        self.X, self.Y = np.meshgrid(self.x, self.y)
        
        self.wind0 = self.find_wav(lambda0)  # wavelength index
        self.wind = self.find_wav(lambda1)  # wavelength index
        
        self.fig = plt.figure('PL data analyser')
        
        self.ax = plt.subplot2grid((5, 5), (0, 2), colspan=3, rowspan=4)
        self.cax = make_axes_locatable(self.ax).append_axes("right", size="5%", pad="2%")
        self.ax2 = plt.subplot2grid((5, 5), (1, 0), colspan=2, rowspan=2)
        
        self.generate_map()
        
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        plt.tight_layout()
        plt.show()
    
    def create_sliders(self):
        axslider1 = plt.axes([0.08, 0.3, 0.25, 0.02])
        self.spectrum_slider0 = Slider(ax=axslider1, label='start (nm)', 
                                       valmin=np.amin(self.wav), valmax=np.amax(self.wav), 
                                       valinit=self.wav[self.wind0],
                                       color='red')
        self.spectrum_slider0.on_changed(self.update_sliders)
        
        axslider2 = plt.axes([0.08, 0.25, 0.25, 0.02])
        self.spectrum_slider1 = Slider(ax=axslider2, label='end (nm)',
                                       valmin=np.amin(self.wav), valmax=np.amax(self.wav), 
                                       valinit=self.wav[self.wind],
                                       color='blue')
        self.spectrum_slider1.on_changed(self.update_sliders)

    
    
    def update_sliders(self, val):
        self.clickedspectrum = True
        
        self.lam0 = self.spectrum_slider0.val
        self.lam = self.spectrum_slider1.val
        
        self.newind0 = self.find_wav(self.lam0)
        self.newind = self.find_wav(self.lam)
        
        if self.wav[self.newind0] >= self.wav[self.newind]:
            print('Bad choice of wavelengths!')
        else:
            print(f'Integrate PL map from {self.wav[self.newind0]} to {self.wav[self.newind]}.')
        
        
        self.svbar0.set_xdata([self.wav[self.newind0], self.wav[self.newind0]])
        self.svbar.set_xdata([self.wav[self.newind], self.wav[self.newind]])
       
        # self.svbar2.set_xdata([self.newwav2, self.newwav2])

        self.ax.clear()
        # self.spectrum_slider.set_val(self.wav[self.newind])

        self.generate_map()
        self.update_map_marker()



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

            if self.clickedmap and self.clickedspectrum:
                self.newwav0 = self.wav[self.newind0]
                self.newwav = self.wav[self.newind]
            else:
                self.newwav0 = self.wav[self.wind0]
                self.newwav = self.wav[self.wind]
            
            self.svbar0, = self.ax2.plot([self.newwav0, self.newwav0], (np.amin(self.data), 1.1*np.amax(self.data)), 'r--')
            self.svbar, = self.ax2.plot([self.newwav, self.newwav], (np.amin(self.data), 1.1*np.amax(self.data)), 'b--')
            
            ### 2nd marker
            # self.wind2 = self.find_wav(740)
            # self.newwav2 = self.wav[self.wind2]
            # self.svbar2, = self.ax2.plot([self.newwav2, self.newwav2], (np.amin(self.data), 1.1*np.amax(self.data)), 'k--')
            
            self.spectrum_labels()
            self.fig.canvas.draw()
            
            if self.clickedmap == False:
                self.create_sliders()
            self.clickedmap = True
    


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
        self.ax2.grid(True)

    def clear_all_axes(self):
        self.ax.clear()
        self.ax2.clear()
        self.cax.clear()
    
    def save_png(self, event):
        fig, ax = plt.subplots()
        ax.pcolormesh(map_data, cmap=colormap, shading='auto')
        extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        
        wav0 = format(self.wav[self.newind0], '.2f')
        wav = format(self.wav[self.newind], '.2f')

        png_name = 'figure' + str(self.png_no) + '_' + str(wav0) + '-' + str(wav) + '.png'
        
        
        fig.savefig(png_name, bbox_inches=extent)
        
        plt.close()
        print(f'Data saved as {png_name}')
        self.png_no = self.png_no + 1


if __name__ == '__main__':
    plotter = PLmap()
    plotter.plot_map(740, 780)
    
    # Create a button for saving png image
    saving = plt.axes([0.7, 0.05, 0.2, 0.075])
    bsaving = Button(saving, 'Save .png')
    bsaving.on_clicked(plotter.save_png)
