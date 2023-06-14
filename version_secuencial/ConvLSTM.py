from keras.models import Sequential
from keras.layers import Conv3D
from keras.layers import ConvLSTM2D, BatchNormalization
from keras.optimizers import Adam
from keras.layers import Flatten

def create_model(input_shape=(None, 3, 3, 1)):
    model = Sequential()

    model.add(ConvLSTM2D(filters=40, kernel_size=(3, 3),
               input_shape=input_shape,
               padding='same', return_sequences=True))
    model.add(BatchNormalization())

    model.add(ConvLSTM2D(filters=80, kernel_size=(3, 3),
               padding='same', return_sequences=True))
    model.add(BatchNormalization())

    model.add(Conv3D(filters=3, kernel_size=(3, 3, 3),
               activation='relu',
               padding='same', data_format='channels_last'))

    # Añadir una capa Flatten
    model.add(Flatten())

    model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))
    
    return model
