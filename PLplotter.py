import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.widgets import RadioButtons

# Scan coordinates and spectrum wavelength - same as in randomDataGeneration.py
x = np.arange(1, 10.1, 0.1)
y = np.arange(1, 5.1, 0.1)
z = 3.1415
X, Y = np.meshgrid(x, y)
wav = np.arange(300, 800.1, 20)

name = 'randomData.csv'  # name of the data file

mpl.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 20
plt.rcParams['axes.linewidth'] = 2
plt.rcParams["figure.figsize"] = (10,7)

class PLmap():
    def __init__(self, name):
        self.name = name

        # Reading a file (every line is a separate string)
        with open(name, 'r') as file:
            self.first_line = file.readline()
            raw_data = file.readlines()
        print('Finished reading a file.')

        # Extracting data (wavelengths!) from the first line in the data file
        self.first_line = self.first_line.strip('\n').split(',')
        self.first_line.pop()

        # Converting lines of strings to numpy array
        self.data = np.zeros((len(raw_data), len(self.first_line)-3))
        for i, line in enumerate(raw_data):
            line = line.strip('\n').split(',')[3:-1]
            self.data[i,:] = (np.float_(line))


    def map(self, wavelength):
        '''
        :param wavelength: select the wavelength of interest to plot a PL map
        '''
        fig, ax = plt.subplots()
        ind = np.where(wav==wavelength)[0][0]
        map_data = np.reshape(self.data[:,ind], (len(y), len(x)))
        ax.contourf(X, Y, map_data)
        adding_labels(ax)

        plt.show()


    def map_and_buttons(self, *args):
        '''
        :param args: a list of wavelengths to plot a PL map
        '''

        ind = np.where(wav == args[0])[0][0]  # initial map is plot at the first wavelength of the list
        np.reshape(self.data[:, ind], (len(y), len(x)))

        fig, ax = plt.subplots()
        ax.contourf(X, Y, np.reshape(self.data[:, ind], (len(y), len(x))))
        adding_labels(ax)
        plt.subplots_adjust(left=0.3)

        axcolor = 'lightgoldenrodyellow'
        rax = plt.axes([0.02, 0.7, 0.18, 0.18], facecolor=axcolor)
        label = [str(el)+'(nm)' for el in args]
        radio = RadioButtons(rax, label)

        indices = [np.where(wav == el)[0][0] for el in args]
        wavdict = dict(zip(label, indices))

        def wavfunc(label):
            '''
            Function which is used each time a button is pressed to renew axes
            :param label: list of wavelengths stored as strings
            '''
            ax.clear()
            new_ind = wavdict[label]
            ax.contourf(np.reshape(self.data[:, new_ind], (len(y), len(x))))
            adding_labels(ax)
            plt.draw()

        radio.on_clicked(wavfunc)
        plt.show()

def adding_labels(ax):
    ax.set_xlabel('x (mm)')
    ax.set_ylabel('y (mm)')

if __name__ == '__main__':
    plotter = PLmap(name)
    # plotter.map(600)
    plotter.map_and_buttons(400, 500, 700)