import java.io.DataInputStream;
import java.io.IOException;

// Lejos imports
import lejos.nxt.*;
import lejos.nxt.comm.*;

// Collect commands, write to screen
public class MainCtrl {

        //Defines the execution mode variable used for turning relivant test functions on/off
        private static int execMode = 0;

        //Deifines a boolean to determine wheather the movement motors are currently running
        private static boolean moving = false;

        //Defines the variables used for determining the position of each wheel
        private static int steeringangle_left = 0;
	private static int steeringangle_right = 0;
    
        //Defines the motors used for steering the right and left wheels
	private static final Motor motor_left = Motor.A;
	private static final Motor motor_right = Motor.B;
	
        //Defines the motor used for the kicker
	private static final Motor motor_kick = Motor.C;
	
	//Defines the number of motor turns to wheel turns
	private static final double rotConstant = 2.375;

        //Defines the sensor port used to power the communication light
        private static final SensorPort port_comlight = SensorPort.S1;

        //Defines the buttons
        private static final Button button_left = Button.LEFT;
        private static final Button button_right = Button.RIGHT;
        private static final Button button_enter = Button.ENTER;

        // Defines variables used for the managing bluetooth connection
	private static BTConnection connection;
	private static DataInputStream inputStream;

	public static void main(String[] args) throws InterruptedException{
	    executionMenu();
	}
	
        //Aims to establish a conection over Bluetooth
        public static void connect(){
	        writeToScreen("Trying to connect", 7);
		// Wait until connected
		connection = Bluetooth.waitForConnection();
		writeToScreen("Connected", 7); 
		inputStream = connection.openDataInputStream();
		writeToScreen("Connection Opened", 7); 
	}

        //Handles collecting the messages from the server over Bluetooth
	private static void collectMessage() throws InterruptedException{
	    int atend = false;
	    while(atend = false){
			try {
				// Parse if there are any messages
				if(inputStream.available()>0){
				        writeToScreen("Got message",7);
					int message = inputStream.readInt();
					// Do specific action
					if (message != 10000){
					    parseMessage(message);
					} else {
					    //if the message is 10000 close connection
					    atend = true;
					}
					writeToScreen("Done",7);	
				}
			} catch (IOException e) {
			    writeToScreen("Error",7);
			}
		}
	}

    //Parses integer messages
    public static void parseMessage(int message){
	switch(message){
	case 0:
	    reset();
	    break;
	case 1:
	    drive();
	    break;
	case 2:
	    stop();
	    break;
	case 3:
	    startSpinRight();
	    break;
	case 5:
	    startSpinLeft();
	    break;
	case 366:
	    kick();
	    break;
	case 367:
	    spinRightShort();
	    break;
	case 368:
	    spinLeftShort();
	    break;
	default:
	     if ((message >= 6)&&(message <=365)){
		 setRobotDirection(message - 6);
	     }
	}
    }

	// Writes a message to the brick's screen on a particular line if valid
        public static void writeToScreen(String message, int line){	
	    if ((line >= 0)&&(line <=7)){
	        LCD.drawString("                ", 0, line);
		LCD.drawString(message, 0, line);
		LCD.refresh();
	    }
	}

        // Defines the function to provide the menu for choosing execution mode of the program
        public static void executionMenu(){
	   int selectedchoice = 0;
	   int numchoices = 3;
	   boolean enterselected = false;
	   boolean haschanged = false;
	   
	   writeToScreen("Select Execution Mode",0);

	   switch (selectedchoice){
	   case 0:
	       writeToScreen("1. Standard Exc.", 1);
       	       break;
       	   case 1:
	       writeToScreen("2. Test +BT", 1);
       	       break;
	   case 2:
       	       writeToScreen("3. Test -BT", 1);
       	       break;
	   }
	   
	   while (enterselected == false){
	       //enumerates the list item when the right button is pressed
	       if (button_right.isPressed()){
		   if(selectedchoice < (numchoices -1)){
		       ++selectedchoice;
		   } else {
		       selectedchoice = 0;
		   }
		   haschanged = true;
	       }
	       
	       //denumerates the list item when the left button is pressed
	       if (button_left.isPressed()){
		   if(selectedchoice > 0){
		       --selectedchoice;
		   } else {
		       selectedchoice = (numchoices - 1);
		   }
		   haschanged = true;
	       }

	       //deals with the enter key being pressed
	       if (button_enter.isPressed()){
		   enterselected = true;
	       }

	       //if the menu item has been changed this updates the screen
	       if (haschanged == true){
		   switch (selectedchoice){
		   case 0:
		       writeToScreen("1. Standard Exc.", 1);
		       break;
		   case 1:
		       writeToScreen("2. Test +BT", 1);
		       break;
		   case 2:
		       writeToScreen("3. Test -BT", 1);
		       break;
		   }
	       }
	       
	       haschanged = false;
	   }

	   //executes the relevant routines based on selection
	   switch (selectedchoice){
	   case 0:
	       writeToScreen("1. Standard Exc.", 0);
	       writeToScreen("",1);
	       execMode = 0;
	       executeStandard();
	       break;
	   case 1:
	       writeToScreen("2. Test +BT", 0);
	       writeToScreen("",1);
	       execMode = 1;
	       executeTestPlusBT();
	       break;
	   case 2:
	       writeToScreen("3. Test -BT", 1);
	       writeToScreen("",1);
	       execMode = 2;
	       executeTestMinBT();
	       break;
	   }
       }
	
        // Standard execution path
        public static void executeStandard(){
	    connect();
	    try{
		collectMessage();
	    } catch (InterruptedException e){
		writeToScreen("Msg Col Interupt",7);
	    }
        }

       // Test execution with Bluetooth
       public static void executeTestPlusBT(){
	   
       }

       // Test execution without Bluetooth
       public static void executeTestMinBT(){
	   //Tests the drive and stop commands
	     
	     //Drive forward for ten seconds then stop
	     writeToScreen("Drive Test 1.",1);
	     writeToScreen("Fwd10,Stp",2);
	     button_enter.waitForPress();
	     drive();
	     try {
		 Thread.sleep(10000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //Drive forward 5sec, stop 2sec, forward 5sec, stop
	     writeToScreen("Drive Test 2.",1);
	     writeToScreen("Fwd5,Stp,Fwd5,Stp",2);
	     button_enter.waitForPress();
	     drive();
	     try{
		 Thread.sleep(5000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     try{
		 Thread.sleep(2000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     drive();
	     try {
		 Thread.sleep(2000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //Drive forwards 2sec, drive forwards 2sec, stop
	     writeToScreen("Drive Test 3.",1);
	     writeToScreen("Fwd2,Fwd2,Stp",2);
	     button_enter.waitForPress();
	     drive();
	     try {
		 Thread.sleep(2000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     drive();
	     try{
		 Thread.sleep(2000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //Drive forwards 2sec, stop, stop
	     writeToScreen("Drive Test 4.",1);
	     writeToScreen("Fwd2,Stp,Stp",2);
	     button_enter.waitForPress();
	     drive();
	     try{
		 Thread.sleep(2000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     stop();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	  //Tests startSpin and stopSpin

	     //startSpin, drive 5s, stop, stopSpin
	     writeToScreen("Spin Test 1.", 1);
	     writeToScreen("StasR,Fwd5,Stp,Stps",2); 
	     button_enter.waitForPress();
	     startSpinRight();
	     drive();
	     try{
		 Thread.sleep(5000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     stopSpin();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //startSpin, drive 5s, stop, stopSpin
	     writeToScreen("Spin Test 2.", 1);
	     writeToScreen("StasL,Fwd5,Stp,Stps",2); 
	     button_enter.waitForPress();
	     startSpinLeft();
	     drive();
	     try{
		 Thread.sleep(5000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     stopSpin();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();


	     //startSpin, stopSpin
	     writeToScreen("Spin Test 3.",1);
	     writeToScreen("StasR,Stps",2);
	     button_enter.waitForPress();
	     startSpinRight();
	     try{
		 Thread.sleep(1000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stopSpin();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //startSpin, stopSpin
	     writeToScreen("Spin Test 4.",1);
	     writeToScreen("StasL,Stps",2);
	     button_enter.waitForPress();
	     startSpinLeft();
	     try{
		 Thread.sleep(1000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stopSpin();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //spinLeftShort
	     writeToScreen("Spin Test 5.",1);
	     writeToScreen("spinLeftShort",2);
	     button_enter.waitForPress();
	     spinLeftShort();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //spinRightShort
	     writeToScreen("Spin Test 5.",1);
	     writeToScreen("spinRightShort",2);
	     button_enter.waitForPress();
	     spinRightShort();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();
	     
	  //Tests setRobotDirection

	     //The Square test: setRobotDirection 90Deg, forward 3s, stop, setRobotDirection 180Deg,forward 3s, stop, setRobotDirection 270Deg, forward 3s, stop, setRobotDirection 0Deg, forward3s, stop  

	     writeToScreen("SRDir Test 1.",1);
	     writeToScreen("The 3s Sqr Tst",2);
	     button_enter.waitForPress();
	     setRobotDirection(90);
	     drive();
	     try{
		 Thread.sleep(3000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     setRobotDirection(180);
	     drive();
	     try{
		 Thread.sleep(3000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     setRobotDirection(270);
	     drive();
	     try{
		 Thread.sleep(3000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     setRobotDirection(0);
	     drive();
	     try{
		 Thread.sleep(3000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //The Diamond Test: setRobotDirection 315Deg, forward 3sec, stop, setRobotDirection 45Deg, forward 3sec, stop, setRobotDirection 135Deg, forward 3sec, stop, setRobotDirection 225, forward 3, stop, reset
	     writeToScreen("SDir Test 2.",1);
	     writeToScreen("The Diamd Tst",2);
	     button_enter.waitForPress();
	     setRobotDirection(315);
	     drive();
	     try{
		 Thread.sleep(3000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     setRobotDirection(45);
	     drive();
	     try{
		 Thread.sleep(3000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     setRobotDirection(135);
	     drive();
	     try{
		 Thread.sleep(3000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     setRobotDirection(225);
	     drive();
	     try{
		 Thread.sleep(3000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     reset();
	     writeToScreen("Done",2);
	     button_enter.waitForPress();

	   //Tests the Kicker
	     //Standard kick
	     writeToScreen("Kick Test 1.",1);
	     writeToScreen("Std Kick",2);
	     button_enter.waitForPress();
	     kick();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();

	     //Moving Kick: reset(), forward 2s + kick()
	     writeToScreen("Kick Test 2.",1);
	     writeToScreen("Mving Kick",2);
	     button_enter.waitForPress();
	     reset();
	     drive();
	     kick();
	     try{
		 Thread.sleep(2000);
	     } catch (InterruptedException e){
		 writeToScreen("Interrupted!",7);
	     }
	     stop();
	     writeToScreen("Done!",2);
	     button_enter.waitForPress();
	     
       }

	// Activate kicker
	public static void kick(){
	        writeToScreen("Kick", 7);
		motor_kick.setSpeed(800);
		motor_kick.forward();
		try{
		    Thread.sleep(417);
		} catch (InterruptedException e){
		    writeToScreen("Interrupted!",7);
		}
		motor_kick.stop();
		//Button.waitForPress();
	}

       //Sets the robot's direction to the input direction in degrees
	public static void setRobotDirection(int DirectionDEGs){
		
	       boolean hasmoved = false;

	        //Halts the movement motors if they are already running
	        if (moving == true){
	            stop();
		    hasmoved = true;
	        }

	       // For the left motor
		if (DirectionDEGs > steeringangle_left){
			motor_left.rotate((int)(rotConstant * (DirectionDEGs - steeringangle_left)),false);
			steeringangle_left = DirectionDEGs;
		} else if (DirectionDEGs < steeringangle_left){
			motor_left.rotate((int)(-1*(steeringangle_left - DirectionDEGs)*rotConstant),false);
			steeringangle_left = DirectionDEGs;
		}
		
		// For the right motor
		if (DirectionDEGs > steeringangle_right){
			motor_right.rotate((int)(rotConstant * (DirectionDEGs - steeringangle_right)),false);
			steeringangle_right = DirectionDEGs;
		} else if (DirectionDEGs < steeringangle_right){
			motor_right.rotate((int)(-1*(steeringangle_right - DirectionDEGs)*rotConstant),false);
			steeringangle_right = DirectionDEGs;
		}

		//Restarts the movement motors if the robot was moving prior to executing the command
		if (hasmoved == true){
		    drive();
		}
	}

    //Defines the function to set the robot to spin around it's own centre in the right direction
    public static void startSpinRight(){
		
	        boolean hasmoved = false;

	        //Halts the movement motors if they are already running
	        if (moving == true){
	            stop();
		    hasmoved = true;
	        }

		//For the left (rotate wheels to 135Deg)
		if ((steeringangle_left % 360) > 315){
			motor_left.rotate((int) (rotConstant * (135 + (360 - (steeringangle_left % 360)))));
		} else if((steeringangle_left % 360) < 135){
			motor_left.rotate((int) (rotConstant * (135 - (steeringangle_left % 360))));
		} else if ((steeringangle_left % 360) >= 135 && ((steeringangle_left % 360) <= 315)) {
			motor_left.rotate((int) (rotConstant * -1 * ((steeringangle_left %360) - 135)));
		}
		
		steeringangle_left = 135;
		
		//For the right (rotate wheels to 315Deg)
		if ((steeringangle_right % 360) > 315){
			motor_right.rotate((int) (rotConstant * -1 *((steeringangle_right % 360)-315)));
		} else if((steeringangle_right % 360) < 135){
			motor_right.rotate((int) (rotConstant * -1 *(45 +( steeringangle_right % 360))));
		} else if ((steeringangle_right % 360) >= 135 && ((steeringangle_right % 360) <= 315)) {
			motor_right.rotate((int) (rotConstant * (180 - ((steeringangle_right % 360) - 45))));
		}
		
		steeringangle_right = 315;

		//Restarts the movement motors if the robot was moving prior to executing the command
		if (hasmoved == true){
		    drive();
		}

	}

    //Defines the function to set the robot to spin around it's own centre in the right direction
    public static void startSpinLeft(){
		
	        boolean hasmoved = false;

	        //Halts the movement motors if they are already running
	        if (moving == true){
	            stop();
		    hasmoved = true;
	        }

		//For the left (rotate wheels to 315Deg)
		if ((steeringangle_left % 360) > 315){
			motor_left.rotate((int) (rotConstant * -1 *((steeringangle_left % 360)-315)));
		} else if((steeringangle_left % 360) < 135){
			motor_left.rotate((int) (rotConstant * -1 *(45 +( steeringangle_left % 360))));
		} else if ((steeringangle_left % 360) >= 135 && ((steeringangle_left % 360) <= 315)) {
			motor_left.rotate((int) (rotConstant * (180 - ((steeringangle_left % 360) - 45))));
		}
		
		steeringangle_left = 315;

     		//For the right (rotate wheels to 135Deg)
		if ((steeringangle_right % 360) > 315){
			motor_right.rotate((int) (rotConstant * (135 + (360 - (steeringangle_right % 360)))));
		} else if((steeringangle_right % 360) < 135){
			motor_right.rotate((int) (rotConstant * (135 - (steeringangle_right % 360))));
		} else if ((steeringangle_right % 360) >= 135 && ((steeringangle_right % 360) <= 315)) {
			motor_right.rotate((int) (rotConstant * -1 * ((steeringangle_right %360) - 135)));
		}
		
		steeringangle_right = 135;

		//Restarts the movement motors if the robot was moving prior to executing the command
		if (hasmoved == true){
		    drive();
		}

	}

    //Defines the function used to stop the robot spinning round it's own centre
    public static void stopSpin(){
	
	 boolean hasmoved = false;

	 //Halts the movement motors if they are already running
         if (moving == true){
            stop();
       	    hasmoved = true;
         }
	
	//Puts the wheels back to 0Deg
	reset();

	//Restarts the movement motors if the robot was moving prior to executing the command
	if (hasmoved == true){
       	    drive();
	}
    }

    //Communicates with the light sensor on the RCX to start the drive motors
    public static void drive(){
	port_comlight.setPowerType(port_comlight.POWER_RCX9V);
	port_comlight.activate();
	moving = true;
    }

    //Communicates with the light sensor on the RCX to stop the drive motors
    public static void stop(){
	port_comlight.passivate();
	moving = false;
    }

    //Resets both wheels to 0 deg
    public static void reset(){
	
	//rotates the left wheels back to 0 deg
	if ((steeringangle_left % 360) > 180){
	    motor_left.rotate((int)(rotConstant * (180 - ((steeringangle_left % 360) - 180))));
	} else if ((steeringangle_left % 360) <= 180) {
	    motor_left.rotate((int)(rotConstant * -1 * (steeringangle_left % 360)));
	}

	steeringangle_left = 0;

	//rotates the right wheels back to 0 deg
	if ((steeringangle_right % 360) > 180){
	    motor_right.rotate((int)(rotConstant * (180 - ((steeringangle_right % 360) - 180))));
	} else if ((steeringangle_right % 360) <= 180){
	    motor_right.rotate((int)(rotConstant * -1 * (steeringangle_right % 360)));
	}

	steeringangle_right = 0;

    }

    //Makes the robot make a slight spin right
    public static void spinRightShort(){
	startSpinRight();
	drive();
	try{
	    Thread.sleep(800);
	} catch (InterruptedException e){
	    writeToScreen("Msg Col Interupt",7);
	}
	stop();
	stopSpin();
    }

    //Makes the robot make a slight spin left
    public static void spinLeftShort(){
	startSpinLeft();
	drive();
	try{
	    Thread.sleep(800);
	} catch (InterruptedException e){
	    writeToScreen("Msg Col Interupt",7);
	}
	stop();
	stopSpin();
    }
}

