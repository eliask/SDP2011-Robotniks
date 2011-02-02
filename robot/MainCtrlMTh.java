import java.io.DataInputStream;
import java.io.IOException;

// Lejos imports
import lejos.nxt.*;
import lejos.nxt.comm.*;

// Collect commands, write to screen
public class MainCtrlMTh {

        //Defines the buttons
        private static final Button button_left = Button.LEFT;
        private static final Button button_right = Button.RIGHT;
        private static final Button button_enter = Button.ENTER;

        // Defines variables used for the managing bluetooth connection
	private static BTConnection connection;
	private static DataInputStream inputStream;

	public static void main(String[] args) throws InterruptedException{
	    Movement.motor_left.setSpeed(900);
	    Movement.motor_right.setSpeed(900);

	    executionMenu();
	}
	
        //Aims to establish a conection over Bluetooth
        private static void connect(){
	        writeToScreen("Trying to connect", 7);
		// Wait until connected
		connection = Bluetooth.waitForConnection();
		writeToScreen("Connected", 7); 
		inputStream = connection.openDataInputStream();
		writeToScreen("Connection Opened", 7); 
	}

        //Handles collecting the messages from the server over Bluetooth
	private static void collectMessage() throws InterruptedException{
	    boolean atend = false;
	    long numoftwos = 0;
	    long prevval = 0;
	    int messageno = 0;
	    while(atend == false){
			try {
				// Parse if there are any messages
			    long inlen = inputStream.available();
			    if((inlen>=4) && (inlen%4 == 0)){
				writeToScreen("Got message no:"+Integer.toString(messageno),7);
					if (inlen > 4){
					    inputStream.skip( ((int) (inlen / 4)) * 4);
					}
					int message = inputStream.readInt();
					// Do specific action
					if (message == 10000){
					    atend = true;
					    writeToScreen(Integer.toString(message),7);
					} else {
					    if (Movement.getThreadsRunning() == 0){ 
						writeToScreen(Integer.toString(message),6);
						parseMessage(message);
					    }
					}
					inputStream.close();
					inputStream = connection.openDataInputStream();
			    } else {
				writeToScreen("inlen = "+Long.toString(inlen),7);
				
				if (prevval == inlen){
				    numoftwos++;
				} else {
				    numoftwos = 0;
				}
				if (numoftwos > 30){
				    inputStream.close();
				    inputStream = connection.openDataInputStream();
				}
				prevval = inlen;
			    }	
			} catch (IOException e) {
			    writeToScreen("Error",7);
			    atend = true;
			}
		}
	    writeToScreen("Exit While",7);
	}

       //Parses integer messages
       private static void parseMessage(int message){
	   int threadCount = 0;

	   boolean reset = message & 1;
	   boolean kick = message & ( (1<<1)-1 << 1 );
	   byte motor1_dir = message & ( (1<<3)-1 << 2 );
	   byte motor2_dir = message & ( (1<<3)-1 << 5 );
	   int angle1 = ( (1<<9)-1 << 8 );
	   int angle2 = ( (1<<9)-1 << 17 );


       }

	// Writes a message to the brick's screen on a particular line if valid
        private static void writeToScreen(String message, int line){	 
	    if ((line >= 0)&&(line <=7)){
	        LCD.drawString("                ", 0, line);
		LCD.drawString(message, 0, line);
		LCD.refresh();
	    }
	}

        // Defines the function to provide the menu for choosing execution mode of the program
        private static void executionMenu(){
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
	       executeStandard();
	       break;
	   case 1:
	       writeToScreen("2. Test +BT", 0);
	       writeToScreen("",1);
	       executeTestPlusBT();
	       break;
	   case 2:
	       writeToScreen("3. Test -BT", 1);
	       writeToScreen("",1);
	       executeTestMinBT();
	       break;
	   }
       }
	
        // Standard execution path
        private static void executeStandard(){
	    connect();
	    Movement.motor_right.resetTachoCount();
	    Movement.motor_left.resetTachoCount();

	    Movement.motor_right.regulateSpeed(true);
	    Movement.motor_left.regulateSpeed(true);

	    Movement.motor_right.smoothAcceleration(true);
	    Movement.motor_left.smoothAcceleration(true);
	    try{
		collectMessage();
	    } catch (InterruptedException e){
		writeToScreen("Msg Col Interupt",7);
	    }
        }

       // Test execution with Bluetooth
       private static void executeTestPlusBT(){
	   
       }

       // Test execution without Bluetooth
       private static void executeTestMinBT(){

       }        
}

class Movement {
	
        //Defines the variables used for determining the position of each wheel
        private static int steeringAngleLeft = 0;
	private static int steeringAngleRight = 0;
    
        //Defines the motors used for steering the right and left wheels
	public static final Motor motor_left = Motor.A;
	public static final Motor motor_right = Motor.B;
	
        //Defines the motor used for the kicker
	public static final Motor motor_kick = Motor.C;
	
	//Defines the number of motor turns to wheel turns
	public static final double rotConstant = 2.375;

        //Defines the sensor port used to power the communication light
        public static final SensorPort port_comlight = SensorPort.S1;

        // Defines the variable used to make sure no two movement command combinations are executed at once
        private static int threadsRunning = 0;

    public static int getThreadsRunning(){
	return threadsRunning;
    }

    public synchronized static void setThreadsRunning(int totalThreads){
	if (threadsRunning == 0){
	    threadsRunning = totalThreads; 
	}
    }

    public synchronized static void decrementThreadsRunning(){
	if (threadsRunning > 0){
	    threadsRunning--;
	}
    }
    
    public static int getSteeringAngleLeft(){
        return steeringAngleLeft;
    }

    public static int getSteeringAngleRight(){
	return steeringAngleRight;
    }

    public static void setSteeringAngleLeft(int Degs){
	steeringAngleLeft = Degs;
    }

    public static void setSteeringAngleRight(int Degs){
	steeringAngleRight = Degs;
    }
	
}

// Activate kicker
class KickThread extends Thread {

	public KickThread() {
	}
	public void run() {
      	    Movement.motor_kick.setSpeed(900);
	    Movement.motor_kick.rotate(720);
	    Movement.decrementThreadsRunning();
	}
}

//Communicates with the light sensor on the RCX to start the drive motors
class StartDriveThread extends Thread {

       	public StartDriveThread() {
	}    
        public void run(){
	    Movement.port_comlight.setPowerType(Movement.port_comlight.POWER_RCX9V);
	    Movement.port_comlight.activate();
	    Movement.decrementThreadsRunning();
	}
}


//Communicates with the light sensor on the RCX to stop the drive motors
class StopDriveThread extends Thread {

    public StopDriveThread(){
    }
    public void run(){
	Movement.port_comlight.passivate();
	Movement.decrementThreadsRunning();
    }
}

//Turns the left wheel to a specified angle
class LeftWheelToThread extends Thread{

    private static int TurnDegs = 0;

    public LeftWheelToThread(int TurnDegs){
	this.TurnDegs = TurnDegs;
    }

    public synchronized void run(){
	if ((Movement.getSteeringAngleLeft() % 360) < 180){
		if (TurnDegs < 180){
		    Movement.motor_left.rotate((int)(Movement.rotConstant * (TurnDegs - Movement.getSteeringAngleLeft())));
		} else if (TurnDegs >= 180){
		    if ((TurnDegs - (Movement.getSteeringAngleLeft() % 360)) < 180){
			Movement.motor_left.rotate((int) (Movement.rotConstant * (TurnDegs - Movement.getSteeringAngleLeft())));
		    } else if((TurnDegs - (Movement.getSteeringAngleLeft() % 360)) >= 180 ){
			Movement.motor_left.rotate((int) (Movement.rotConstant * -1 *((360 - (TurnDegs % 360)) + Movement.getSteeringAngleLeft())));
		    }
		}
	} else if ((Movement.getSteeringAngleLeft() % 360) >= 180){
		if ((TurnDegs % 360) >= 180){
		    Movement.motor_left.rotate((int)(Movement.rotConstant * ((TurnDegs % 360) - Movement.getSteeringAngleLeft())));
		}else if (TurnDegs < 180){
		    if(((Movement.getSteeringAngleLeft() % 360) - (TurnDegs % 360)) < 180){
			Movement.motor_left.rotate((int)(Movement.rotConstant * ((TurnDegs % 360) - (Movement.getSteeringAngleLeft() % 360))));
		    } else if(((Movement.getSteeringAngleLeft() % 360) - (TurnDegs % 360)) >= 180){
			Movement.motor_left.rotate((int)(Movement.rotConstant * ((360 - (Movement.getSteeringAngleLeft() % 360))+ TurnDegs)));
		    }
		}
	    }

	    Movement.setSteeringAngleLeft(TurnDegs % 360);
	    Movement.decrementThreadsRunning();
	}
    }



//Turns the right wheel to a specified angle
class RightWheelToThread extends Thread{

    private static int TurnDegs = 0; 

    public RightWheelToThread(int TurnDegs){
	this.TurnDegs = TurnDegs;
    }

    public synchronized void run(){
	    if ((Movement.getSteeringAngleRight() % 360) < 180){
		if (TurnDegs < 180){
		    Movement.motor_right.rotate((int)(Movement.rotConstant * (TurnDegs - Movement.getSteeringAngleRight())));
		} else if (TurnDegs >= 180){
		    if ((TurnDegs - (Movement.getSteeringAngleRight() % 360)) < 180){
			Movement.motor_right.rotate((int) (Movement.rotConstant * (TurnDegs - Movement.getSteeringAngleRight())));
		    } else if((TurnDegs - (Movement.getSteeringAngleRight() % 360)) >= 180){
			Movement.motor_right.rotate((int) ( Movement.rotConstant * -1 *((360 - (TurnDegs % 360)) + Movement.getSteeringAngleRight())));
		    }
		}
	    } else if ((Movement.getSteeringAngleRight() % 360) >= 180){
		if ((TurnDegs % 360) >= 180){
		    Movement.motor_right.rotate((int)(Movement.rotConstant * ((TurnDegs % 360) - Movement.getSteeringAngleRight())));
		}else if (TurnDegs < 180){
		    if(((Movement.getSteeringAngleRight() % 360) - (TurnDegs % 360)) < 180){
			Movement.motor_right.rotate((int)(Movement.rotConstant * ((TurnDegs % 360) - (Movement.getSteeringAngleRight() % 360))));
		    } else if(((Movement.getSteeringAngleRight() % 360) - (TurnDegs % 360)) >= 180){
			Movement.motor_right.rotate((int)(Movement.rotConstant * ((360 - (Movement.getSteeringAngleRight() % 360))+ TurnDegs)));
		    }
		}
	    }
	
	    Movement.setSteeringAngleRight(TurnDegs % 360);
	    Movement.decrementThreadsRunning();
    }
    
}
    