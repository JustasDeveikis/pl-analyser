import numpy as np

name = 'randomData.csv'

class Generator():
    def __init__(self, name):
        self.name = name

        # Initialise coordinates and wavelengths
        self.x = np.arange(1, 10.1, 0.1)
        self.y = np.arange(1, 5.1, 0.1)
        self.z = 3.1415
        self.wav = np.arange(300, 800.1, 20)
        print('Coordinates and wavelengths initialised.')


    def create_header(self):
        file = open(name, 'w')
        file.write('{},{},{},'.format('x', 'y', 'z'))
        for w in self.wav:
            file.write('{}(nm),'.format(w))
        file.write('\n')
        file.close()

        print('Headers created.')


    def write_data(self):
        file = open(name, 'a')
        for indy, y in enumerate(self.y):
            for x in self.x:
                file.write('{},{},{},'.format(x, self.y[indy], self.z))

                for w in self.wav:
                    file.write('{},'.format(np.random.randn()))

                file.write('\n')
        file.close()

        print('Data written.')


if __name__ == '__main__':
    randomgen = Generator(name)
    randomgen.create_header()
    randomgen.write_data()