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

	   int reset = message & 1;
	   int kick = (message & 2)/2;
	   int motor_sleft = ((message & 3)/3)+(((message & 4)/4)*2)+(((message & 5)/5)*3);
	   int motor_sright = ((message & 6)/6)+(((message & 7)/7)*2)+(((message & 8)/8)*3);
	   int motor_dleft = ((message & 9)/9)+(((message & 10)/10)*2)+(((message & 11)/11)*3);
	   int motor_dright = ((message & 12)/12)+(((message & 13)/13)*2)+(((message & 14)/14)*3);

	   Movement.setThreadsRunning(5);
	   Thread thread1 = new KickThread(kick);
	   Thread thread2 = new SteeringLeftThread(motor_sleft);
	   Thread thread3 = new SteeringRightThread(motor_sright);
	   Thread thread4 = new DriveLeftThread(motor_dleft);
	   Thread thread5 = new DriveRightThread(motor_dright);

	   thread1.start();
	   thread2.start();
	   thread3.start();
	   thread4.start();
	   thread5.start();

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
	    
	    Movement.motor_left.resetTachoCount();
	    Movement.motor_right.resetTachoCount();

	    Movement.motor_right.smoothAcceleration(true);
	    Movement.motor_left.smoothAcceleration(true);

	    Movement.port_comlight.setPowerType(Movement.port_comlight.POWER_RCX9V);

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
	
}

// Activate kicker
class KickThread extends Thread {
    int control = 0;

	public KickThread(int control) {
	    this.control = control;
	}
	public void run() {
      	    if (control == 1){
		Movement.motor_kick.setSpeed(900);
		Movement.motor_kick.rotate(720);
		Movement.decrementThreadsRunning();
	    }
	}
}

class SteeringLeftThread extends Thread{
    private int control = 0;

    public SteeringLeftThread(int control){
	this.control = control;
    }

    public void run(){
	switch(control){
	case 0:
	    Movement.motor_left.stop();
	    break;
	case 4:
	    Movement.motor_left.stop();
	    break;
	case 1:
	    Movement.motor_left.setSpeed(300);
	    Movement.motor_left.backward();
	    break;
	case 2:
	    Movement.motor_left.setSpeed(600);
	    Movement.motor_left.backward();
	    break;
	case 3:
	    Movement.motor_left.setSpeed(900);
	    Movement.motor_left.backward();
	    break;
	case 5:
	    Movement.motor_left.setSpeed(300);
	    Movement.motor_left.forward();
	    break;
	case 6:
	    Movement.motor_left.setSpeed(600);
	    Movement.motor_left.forward();
	    break;
        case 7:
	    Movement.motor_left.setSpeed(900);
	    Movement.motor_left.forward();
	    break;
	}
	
	Movement.decrementThreadsRunning();
    }
}

class SteeringRightThread extends Thread{
    private int control = 0;

    public SteeringRightThread(int control){
	this.control = control;
    }

    public void run(){
	switch (control){
        case 0:
	    Movement.motor_right.stop();
	    break;
	case 4:
	    Movement.motor_right.stop();
	    break;
	case 1:
	    Movement.motor_right.setSpeed(300);
	    Movement.motor_right.backward();
	    break;
	case 2:
	    Movement.motor_right.setSpeed(600);
	    Movement.motor_right.backward();
	    break;
	case 3:
	    Movement.motor_right.setSpeed(900);
	    Movement.motor_right.backward();
	    break;
	case 5:
	    Movement.motor_right.setSpeed(300);
	    Movement.motor_right.forward();
	    break;
	case 6:
	    Movement.motor_right.setSpeed(600);
	    Movement.motor_right.forward();
	    break;
        case 7:
	    Movement.motor_right.setSpeed(900);
	    Movement.motor_right.forward();
	    break;
	}
	
	Movement.decrementThreadsRunning();
    }
}

class DriveLeftThread extends Thread {
    private int control = 0;
    
       	public DriveLeftThread(int control) {
	    this.control = control;
	}    
        public void run(){
	    switch(control){
	    case 0:
		Movement.port_comlight.passivate();
		break;
	    case 4:
		Movement.port_comlight.passivate();
		break;
	    case 1:
		Movement.port_comlight.activate();
		break;
	    case 2:
		Movement.port_comlight.activate();
		break;
	    case 3:
		Movement.port_comlight.activate();
		break;
	    case 5:
		Movement.port_comlight.activate();
		break;
	    case 6:
		Movement.port_comlight.activate();
		break;
	    case 7:
		Movement.port_comlight.activate();
		break;
	    }

	    Movement.decrementThreadsRunning();

	}
}

class DriveRightThread extends Thread {
    private int control = 0;
    
    public DriveRightThread(int control) {
	this.control = control;
    }    
    public void run(){
	   
	switch(control){
	    case 0:
		Movement.port_comlight.passivate();
		break;
	    case 4:
		Movement.port_comlight.passivate();
		break;
	    case 1:
		Movement.port_comlight.activate();
		break;
	    case 2:
		Movement.port_comlight.activate();
		break;
	    case 3:
		Movement.port_comlight.activate();
		break;
	    case 5:
		Movement.port_comlight.activate();
		break;
	    case 6:
		Movement.port_comlight.activate();
		break;
	    case 7:
		Movement.port_comlight.activate();
		break;
	 }

	    Movement.decrementThreadsRunning();
    }
}





    