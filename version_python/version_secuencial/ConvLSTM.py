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
               padding='same', return_sequences=False))  
    model.add(BatchNormalization())

    model.add(Flatten())

    model.add(Dense(1, activation='sigmoid'))

    model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))

    return model
