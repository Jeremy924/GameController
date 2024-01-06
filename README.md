# Game Controller
User inputs are inputted into the arduino from two joysticks and four buttons. The arduino then sends the data to the computer through the serial port. 
The computer can also send a command to the arduino to set the color of an RGB LED. 

## Files
### GameController.py
The GameController class represents the game controller. The game controller class contains a
generator called start_input() that yields ControllerInput objects. The ControllerInput class represents the current
state of the controller inputs. The inputs are stored in a dictionary. The ControllerInput class
also has a dictionary containing only the inputs that have changed since last input. 

### KeyMapper.py
The KeyMapper class is used to simulate keyboard strokes based on user input from the game
controller. The KeyMapper class uses a dictionary from a json file to store the key
bindings. 
