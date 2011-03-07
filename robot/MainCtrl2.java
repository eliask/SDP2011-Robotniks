import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

// Lejos imports
import lejos.nxt.*;
import lejos.nxt.comm.*;


// Collect commands, write to screen
public class MainCtrl2 {

	//Defines the buttons
	private static final Button button_left = Button.LEFT;
	private static final Button button_right = Button.RIGHT;
	private static final Button button_enter = Button.ENTER;


	public static void main(String[] args) throws InterruptedException{
		Thread mainCommunicator = new Communicator();
		Thread kickThread = new KickThread();
		Thread driveThread = new DriveThread();
		Thread steeringLeftThread = new SteeringLeftThread();
		Thread steeringRightThread = new SteeringRightThread();
		Thread counterThread = new CounterThread();

		mainCommunicator.start();
		kickThread.start();
		driveThread.start();
		steeringLeftThread.start();
		steeringRightThread.start();
		counterThread.start();
	}
}

class Movement {

	//Defines the motors used for steering the right and left wheels
	public static final Motor motor_left = Motor.A;
	public static final Motor motor_right = Motor.B;

	//Defines the motor used for the kicker
	public static final Motor motor_kick = Motor.C;

	//Defines the number of motor turns to wheel turns
	public static final double rotConstant = 56.0 / 24.0;

	//Defines the sensor port used to power the communication light
	public static final SensorPort port_comlight = SensorPort.S1;

	// Defines the variable used to make sure no two movement command combinations are executed at once
	private static int commandCounter = 0;

	public static int getCommandCount(){
	    return commandCounter;
	}

	public synchronized static void setCommandCount(int CommandCount){
	    commandCounter = CommandCount;
	}

}


class ControlCentre{
	private static int targetSteeringAngleRight = 0;
	private static int targetSteeringAngleLeft = 0;
	private static int targetDriveLeftVal = 0;
	private static int targetDriveRightVal =0;
	private static boolean targetKickState = false;

	public static synchronized int getTargetSteeringAngleRight(){
		return targetSteeringAngleRight;
	}

	public static synchronized int getTargetSteeringAngleLeft(){
		return targetSteeringAngleLeft;
	}

	public static synchronized int getTargetDriveLeftVal(){
		return targetDriveLeftVal;
	}

	public static synchronized int getTargetDriveRightVal(){
		return targetDriveRightVal;
	}

	public static synchronized boolean getKickState(){
		return targetKickState;
	}

	public static synchronized void setTargetSteeringAngleRight(int Angle){
		targetSteeringAngleRight = Angle;
	}

	public static synchronized void setTargetSteeringAngleLeft(int Angle){
		targetSteeringAngleLeft = Angle;
	}

	public static synchronized void setTargetDriveLeftVal(int Val){
		targetDriveLeftVal = Val;
	}

	public static synchronized void setTargetDriveRightVal(int Val){
		targetDriveRightVal = Val;
	}

	public static synchronized void setKickState(boolean Val){
		targetKickState = Val;
	}
}

class Communicator extends Thread {
	// Defines variables used for the managing bluetooth connection
	private static BTConnection connection;
	private static DataInputStream inputStream;
	private static DataOutputStream outputStream;

	public Communicator(){
	}
	public void run(){
		connect();
		try{
			collectMessage();
		} catch (InterruptedException e){
			Thread msgInterruptDisplay = new ScreenWriter("Msg Col Interupt",7);
			msgInterruptDisplay.start();
		}
		try{
			Thread.sleep(100);
		}catch(InterruptedException e){
		}
	}

	//Aims to establish a conection over Bluetooth
	private static void connect(){
		Thread tryingDisplay = new ScreenWriter("Trying to connect", 7);
		tryingDisplay.start();
		// Wait until connected
		connection = Bluetooth.waitForConnection();
		Thread connectedDisplay = new ScreenWriter("Connected", 7);
		connectedDisplay.start();
		inputStream = connection.openDataInputStream();
		outputStream = connection.openDataOutputStream();
		Thread openConnDisplay = new ScreenWriter("Connection Opened", 7);
		openConnDisplay.start();
	}

	private static void collectMessage() throws InterruptedException{
		boolean atend = false;
		int N = 0;
		while(atend == false){
			N = N+1; //% 100;
			Movement.setCommandCount(N);
			LCD.drawString("Recv:"+Integer.toString(N), 2, 2);
			try{
				//Bluetooth.getConnectionStatus();
			        int message = inputStream.readInt();
				LCD.drawString("Rcvd:"+Integer.toString(N), 2, 3);
				if (message >= (1<<26)){
				    LCD.drawString("end"+Integer.toString(N), 12, 2);
					atend = true;
					//Thread atendDisplay = new ScreenWriter(Integer.toString(message),7);
					LCD.drawString(Integer.toString(message),0,7);
					//atendDisplay.start();
					//System.exit();
					LCD.drawString("stopped" + message, 0, 2);
				} else if (message < (1<<26)){
				    //Thread newMessageDisplay = new ScreenWriter(Integer.toString(message),6);
				    //LCD.drawString("display"+Integer.toString(N), 6, 0);
					//newMessageDisplay.start();
					LCD.drawString("        ", 5, 6);
					LCD.drawString("Msg:"+Integer.toString(message), 0, 6);
					//LCD.drawString("decode:"+Integer.toString(N), 6, 1);
					parseMessage(message);
					//LCD.drawString("decoded:"+Integer.toString(N), 6, 0);
				}
				//inputStream.close();
				//inputStream = connection.openDataInputStream();
			} catch (IOException e) {
				Thread errorConnection = new ScreenWriter("Error - connect back up", 7);
				errorConnection.start();
				//connection = Bluetooth.waitForConnection();
				Thread connectedDisplay = new ScreenWriter("Connection Opened", 7);
				connectedDisplay.start();
			}

		}
	}

	//Parses integer messages
	private static void parseMessage(int message){
		int reset = message & 1;
		int kick = (message >>> 1) & 1;
		int motor_dleft = (message >>> 2) & 7;
		int motor_dright = (message >>> 5) & 7;
		int motor_sleft = (message >>> 8) & 511;
		int motor_sright = (message >>> 17) & 511;

		ControlCentre.setKickState(( kick != 0));
		ControlCentre.setTargetSteeringAngleLeft(motor_sleft);
		ControlCentre.setTargetSteeringAngleRight(motor_sright);
		ControlCentre.setTargetDriveLeftVal(motor_dleft);
		ControlCentre.setTargetDriveRightVal(motor_dright);

	}

	// send sensor data back?
	public static void sendBackMessage(int messageBack) throws IOException{
		outputStream.writeInt(messageBack);
		outputStream.flush();
	}
}

class ScreenWriter extends Thread{
	private String astring = "";
	private int line = 0;

	public ScreenWriter(String instring, int inline){
		setAString(instring);
		setLine(inline);
	}

	public synchronized void run(){
		if ((line >= 0)&&(line <=7)){
			LCD.drawString("                ", 0, getLine());
			LCD.drawString(getAString(), 0, getLine());
			LCD.refresh();
		}
	}

	private synchronized String getAString(){
		return this.astring;
	}

	private synchronized int getLine(){
		return this.line;
	}

	private synchronized void setAString(String instring){
		this.astring = instring;
	}

	private synchronized void setLine(int inline){
		this.line = inline;
	}
}

class CounterThread extends Thread{
    public void run(){
	int count = 0;
	while (true){
	    LCD.drawString("" + Integer.toString(count++), 6,0);
	    count %= 1000;
	    try{
		Thread.sleep(100);
	    }catch(InterruptedException e){
	    }
	}
    }
}

class KickThread extends Thread{

	public KickThread(){
	}

	public void run(){
		while (true){
			boolean kick = ControlCentre.getKickState();
			if (kick) {
				LCD.drawString("K,",0,1);
				Movement.motor_kick.setSpeed(900);
				Movement.motor_kick.rotate((-120*(5/3)));
				Movement.motor_kick.rotate((120*(5/3)));
			} else {
				LCD.drawString("_,",0,1);
			}
		try{
			Thread.sleep(100);
		}catch(InterruptedException e){
		}
		}
	}
}

class DriveThread extends Thread{
	public DriveThread(){
	}

	public void run(){
		Multiplexor chip = new Multiplexor(SensorPort.S4);
		while(true){

			int targetLeft = ControlCentre.getTargetDriveLeftVal();
			LCD.drawString(Integer.toString(targetLeft)+",",2,1);

			switch(targetLeft){
			case 0:
			    chip.setMotors(0,0,0);
			    break;
			case 4:
			    chip.setMotors(0,0,0);
			    break;
			case 1:
			    chip.setMotors(1,1,0);
			    break;
			case 2:
			    chip.setMotors(1,2,0);
			    break;
			case 3:
			    chip.setMotors(1,3,0);
			    break;
			case 5:
			    chip.setMotors(-1,1,0);
			    break;
			case 6:
			    chip.setMotors(-1,2,0);
			    break;
			case 7:
			    chip.setMotors(-1,3,0);
			    break;
			}

			int targetRight = ControlCentre.getTargetDriveRightVal();
			LCD.drawString(Integer.toString(targetRight)+" L",4,1);
			switch(targetRight){
			case 0:
			    chip.setMotors(0,0,1);
			    break;
			case 4:
			    chip.setMotors(0,0,1);
			    break;
			case 1:
			    chip.setMotors(1,1,1);
			    break;
			case 2:
			    chip.setMotors(1,2,1);
			    break;
			case 3:
			    chip.setMotors(1,3,1);
			    break;
			case 5:
			    chip.setMotors(-1,1,1);
			    break;
			case 6:
			    chip.setMotors(-1,2,1);
			    break;
			case 7:
			    chip.setMotors(-1,3,1);
			    break;
			}

		try{
			Thread.sleep(10);
		}catch(InterruptedException e){
		}
		}
	}
}

class SteeringLeftThread extends Thread{
	public static final Motor motor_left = Motor.A;
	private static int currentSteeringAngle = 0;
	private static int toAngle = 0;
	public final double thresholdAngle = 30.0;

	public SteeringLeftThread(){
	}

	public void run(){
		motor_left.resetTachoCount();
		motor_left.regulateSpeed(true);
		Movement.motor_left.smoothAcceleration(true);
		int previousCommandCount = -1;

		while(true){
			if(Movement.getCommandCount() == previousCommandCount) {
			    try{
				Thread.sleep(10);
			    }catch(InterruptedException e){
			    }
			    continue;
			}

			previousCommandCount = Movement.getCommandCount();
			setToAngle(ControlCentre.getTargetSteeringAngleLeft());
			int new_angle = getToAngle();
			if (new_angle < 10)
				LCD.drawString("  ", 8 ,1);
			else if (new_angle < 100)
				LCD.drawString(" ", 9 ,1);
			LCD.drawString(Integer.toString(new_angle), 7 ,1);
			LCD.drawString("R", 11 ,1);

			int cur_angle = getCurrentSteeringAngle();
			double delta = new_angle - cur_angle;
			final double C = Movement.rotConstant;
			double turn_angle = 0;

			if (Math.abs(delta) < thresholdAngle/2.0) {
				continue;
			}
			else if (Math.abs(delta) >= thresholdAngle/2.0 &&
				 Math.abs(delta) < thresholdAngle) {
			    delta = thresholdAngle*delta/Math.abs(delta);
			}
			setCurrentSteeringAngle((int)(cur_angle+delta)%360);

			if (delta != 0 && Math.abs(delta) < 180) {
				turn_angle = C * delta;
			}
			else if (delta >= 180 && delta < 360) {
				turn_angle = -C * (360 - delta);
			}
			else if (delta <= -180) {
				turn_angle = C * (360 + delta);
			}
			else { /* No turning needed */
				continue;
			}

			motor_left.rotate( (int)Math.round(turn_angle) );
		}
	}

	private synchronized int getCurrentSteeringAngle(){
		return currentSteeringAngle;
	}

	private synchronized int getToAngle(){
		return toAngle;
	}

	private synchronized void setCurrentSteeringAngle(int Angle){
		currentSteeringAngle = Angle;
	}

	private synchronized void setToAngle(int Angle){
		toAngle = Angle;
	}
}

class SteeringRightThread extends Thread{
	public static final Motor motor_right = Motor.B;
	private static int currentSteeringAngle = 0;
	private static int toAngle = 0;
	public final double thresholdAngle = 30.0;

	public SteeringRightThread(){
	}

	public void run(){
		motor_right.resetTachoCount();
		motor_right.regulateSpeed(true);
		Movement.motor_right.smoothAcceleration(true);
		int previousCommandCount = -1;

		while(true){
			if(Movement.getCommandCount() == previousCommandCount) {
			    try{
				Thread.sleep(10);
			    }catch(InterruptedException e){
			    }
			    continue;
			}

			previousCommandCount = Movement.getCommandCount();
			setToAngle(ControlCentre.getTargetSteeringAngleRight());
			int new_angle = getToAngle();
			if (new_angle < 10)
			    LCD.drawString("  ", 13 ,1);
			else if (new_angle < 100)
			    LCD.drawString(" ", 14 ,1);
			LCD.drawString(Integer.toString(new_angle), 12 ,1);

			int cur_angle = getCurrentSteeringAngle();
			double delta = new_angle - cur_angle;
			final double C = Movement.rotConstant;
			double turn_angle = 0;

			if (Math.abs(delta) < thresholdAngle/2.0) {
				continue;
			}
			else if (Math.abs(delta) >= thresholdAngle/2.0 &&
				 Math.abs(delta) < thresholdAngle) {
			    delta = thresholdAngle*delta/Math.abs(delta);
			}
			setCurrentSteeringAngle((int)(cur_angle+delta)%360);

			if (delta != 0 && Math.abs(delta) < 180) {
				turn_angle = C * delta;
			}
			else if (delta >= 180 && delta < 360) {
				turn_angle = -C * (360 - delta);
			}
			else if (delta <= -180) {
				turn_angle = C * (360 + delta);
			}
			else { /* No turning needed */
				continue;
			}
			motor_right.rotate( (int)Math.round(turn_angle) );
		}
	}

	private synchronized int getCurrentSteeringAngle(){
		return currentSteeringAngle;
	}

	private synchronized int getToAngle(){
		return toAngle;
	}

	private synchronized void setCurrentSteeringAngle(int Angle){
		currentSteeringAngle = Angle;
	}

	private synchronized void setToAngle(int Angle){
		toAngle = Angle;
	}
}

