from keras.models import Sequential
from keras.layers import ConvLSTM2D, BatchNormalization, Flatten, Dense
from keras.optimizers import Adam

# def create_model(input_shape=(None, 3, 3, 1)):
#     model = Sequential()

#     model.add(ConvLSTM2D(filters=40, kernel_size=(2, 2),
#                input_shape=input_shape,
#                padding='same', return_sequences=False))
    
#     model.add(Dense(1, activation='sigmoid'))

#     model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))

#     return model
def create_model(input_shape=(None, 9)):
    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=(9,)))  # 32 is the number of neurons in the hidden layer, you can change this number
    model.add(Dense(1, activation='sigmoid'))  # Output layer

    # Compile the model
    model.compile(optimizer='adam', loss='mse')

    return model