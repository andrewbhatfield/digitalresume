import numpy as np
import struct

from random import randint


class TrainedModel():
    def __init__(self, ):
        params = np.load('applets/resources/mnistmodelweights.npz')
        self.w1 = params['w1'].astype(np.longdouble)
        self.b1 = params['b1'].astype(np.longdouble)
        self.w2 = params['w2'].astype(np.longdouble)
        self.b2 = params['b2'].astype(np.longdouble)

        images = []
        with open('applets/resources/t10k-images.idx3-ubyte', 'rb') as test_images:
            test_images.read(16) # read headers
            while True:
                nb = test_images.read(1)
                if not nb:
                    break
                images.append(struct.unpack('>B', nb)[0]) 
        self.images = images


    def predict(self, input): # takes 784 row x 1 col input corresponding to user drawn 28x28 image and outputs digit
        z2 = np.dot(self.w1,input) + self.b1 
        a2 = z2 * (z2 > 0)
        z3 = np.dot(self.w2,a2) + self.b2
        a3 = np.exp(z3 - np.max(z3)) / np.exp(z3 - np.max(z3)).sum(axis=0)
        return np.argmax(a3, axis=0).tolist()[0]
    
    def randomImage(self):
        n = randint(0,9999)
        return np.reshape(np.array(self.images[n*784:(n+1)*784]), (28,28)).tolist()

    

        