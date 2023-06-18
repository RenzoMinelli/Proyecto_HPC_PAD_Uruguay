from keras.models import Sequential
from keras.layers import ConvLSTM2D, BatchNormalization, Flatten, Dense
from keras.optimizers import Adam

def create_model(input_shape=(None, 3, 3, 1)):
    model = Sequential()

    model.add(ConvLSTM2D(filters=40, kernel_size=(3, 3),
               input_shape=input_shape,
               padding='same', return_sequences=True))
    model.add(BatchNormalization())

    model.add(ConvLSTM2D(filters=80, kernel_size=(3, 3),
               padding='same', return_sequences=True))
    model.add(BatchNormalization())

    # Añade una capa Flatten para convertir la salida multidimensional de las capas ConvLSTM2D en un vector 1D.
    model.add(Flatten())

    # Añade una capa Dense con 1 neurona y función de activación lineal para predecir un solo valor flotante.
    model.add(Dense(1, activation='linear'))

    model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))

    return model
