from keras.models import Sequential
from keras.layers import Dense

def create_model(input_shape=(None, 9)):
    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=(9,)))  # 32 is the number of neurons in the hidden layer
    model.add(Dense(1, activation='sigmoid'))  # Output layer

    # Compile the model
    model.compile(optimizer='adam', loss='mse')

    return model