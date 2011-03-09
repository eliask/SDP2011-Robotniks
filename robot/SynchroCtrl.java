import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

// Lejos imports
import lejos.nxt.*;
import lejos.nxt.comm.*;


// Collect commands, write to screen
public class SynchroCtrl {
	
	//Defines the buttons
	private static final Button button_left = Button.LEFT;
	private static final Button button_right = Button.RIGHT;
	private static final Button button_enter = Button.ENTER;
	
	public static Communicator mainCommunicator;
	public static KickThread kickThread;
	public static DriveThread driveThread;
	public static SteeringThread steeringThread;
	public static SteeringMotorThread steeringLeftThread;
	public static SteeringMotorThread steeringRightThread;
	public static CounterThread counterThread;
	public static CommandHandler commandHandler;
	public static SensorChecker sensorCheck;
	
	public static void main(String[] args) throws InterruptedException{
		commandHandler = new CommandHandler();
		mainCommunicator = new Communicator();
		kickThread = new KickThread();
		driveThread = new DriveThread();
		steeringThread = new SteeringThread();
		steeringLeftThread = new SteeringLeftThread();
		steeringRightThread = new SteeringRightThread();
		sensorCheck = new SensorChecker();
		//counterThread = new CounterThread();
		
		commandHandler.start();
		mainCommunicator.start();
		kickThread.start();
		driveThread.start();
		steeringThread.start();
		steeringLeftThread.start();
		steeringRightThread.start();
		sensorCheck.start();
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
}


class CommandHandler extends Thread {
	
	public static boolean kick;
	public static int drive_left;
	public static int drive_right;
	public static int steer_angle;
	public static int command_id;
	
	public void setKickState(boolean Val){
		SynchroCtrl.kickThread.setKickState(Val);
		synchronized (SynchroCtrl.kickThread) {
			SynchroCtrl.kickThread.notify();
		}
	}
	
	public void setTargetDriveVal(int left, int right){
		SynchroCtrl.driveThread.setTargetDriveVal(left, right);
		synchronized (SynchroCtrl.driveThread) {
			SynchroCtrl.driveThread.notify();
		}
	}
	
	public void setTargetSteeringAngle(int Angle){
		SynchroCtrl.steeringThread.setTargetSteeringAngle(Angle);
		synchronized (SynchroCtrl.steeringThread) {
			SynchroCtrl.steeringThread.notify();
		}
	}
	
	public void run(){
		while(true) {
			RConsole.println("handler pre-wait");
			synchronized (this) {
				try{
					wait();
				}catch(InterruptedException e){
				}
			}
			
			RConsole.println("handler post-wait");
			executeCommand();
		}
	}
	
	private void executeCommand() {
		switch (command_id) {
			case 1:
				moveTo(steer_angle, drive_left);
				break;
				
			case 2:
				orientTo(steer_angle);
				break;
				
			default:
				/* By default, just execute the raw commands: */
				int speedL = drive_left *
				SynchroCtrl.steeringLeftThread.getDirection(steer_angle);
				int speedR = drive_right *
				SynchroCtrl.steeringRightThread.getDirection(steer_angle);
				
				setTargetDriveVal(speedL, speedR);
				setTargetSteeringAngle(steer_angle);
				break;
		}
		
		setKickState(kick);
	}
	
	/* Wait until steering has finished. */
	private void waitForSteering() {
		while(true) {
			
			synchronized (this) {
				try{
					wait();
				}catch(InterruptedException e){
				}
				
				if (SynchroCtrl.steeringLeftThread.Ready() &&
					SynchroCtrl.steeringRightThread.Ready()) {
					break;
				}
			}
			
		}
	}
	
	/* Move towards some bearing at positive integer speed */
	private void moveTo(int angle, int speed) {
		setTargetDriveVal(0, 0);
		setTargetSteeringAngle(angle);
		waitForSteering();
		
		int speedL = speed*SynchroCtrl.steeringLeftThread.getDirection(angle);
		int speedR = speed*SynchroCtrl.steeringRightThread.getDirection(angle);
		setTargetDriveVal(speedL, speedR);
	}
	
	private void orientTo(int angle) {
		setTargetDriveVal(0, 0);
		setTargetSteeringAngle(135);
		waitForSteering();
		
		// TODO: There should be a way to estimate how to orient the
		// robot accurately, and ideally we would find the nearest
		// <=180 to turn towards.
		setTargetDriveVal(2, -2);
		try{
			Thread.sleep(4*angle);
		} catch (InterruptedException e){
		}
		setTargetDriveVal(0, 0);
	}
}

class Communicator extends Thread {
	// Defines variables used for the managing bluetooth connection
	private static BTConnection connection;
	private static DataInputStream inputStream;
	private static DataOutputStream outputStream;
	public static boolean isConnected = false;
	
	public void run(){
		connect();
		try{
			collectMessage();
		} catch (InterruptedException e){
			LCD.drawString("Msg Col Interrupt", 0,7);
		}
	}
	
	//Aims to establish a conection over Bluetooth
	private void connect(){
		LCD.drawString("Trying to connect", 0,7);
		
		// Wait until connected
		connection = Bluetooth.waitForConnection();
		LCD.drawString("Connected", 0,7);
		isConnected = true;
		inputStream = connection.openDataInputStream();
		outputStream = connection.openDataOutputStream();
		LCD.drawString("Connection opened", 0,7);
	}
	
	private void collectMessage() throws InterruptedException{
		RConsole.openUSB(5);
		RConsole.println("Start comm. loop");
		for (int N = 0 ;; ++N) {
			try{
				//Bluetooth.getConnectionStatus();
				LCD.drawString("Recv:"+Integer.toString(N), 8, 2);
				int message = inputStream.readInt();
				LCD.drawString("Rcvd:"+Integer.toString(N), 8, 3);
				//LCD.drawString("display"+Integer.toString(N), 6, 0);
				LCD.drawString("        ", 6, 6);
				LCD.drawString("Msg: "+Integer.toString(message), 0, 6);
				//LCD.drawString("decode:"+Integer.toString(N), 6, 1);
				parseMessage(message);
				//LCD.drawString("decoded:"+Integer.toString(N), 6, 0);
			} catch (IOException e) {
				isConnected = false;
				LCD.drawString("Error: connect back up", 0,7);
				connection = Bluetooth.waitForConnection();
				LCD.drawString("Connection opened", 0,7);
			}
			
		}
	}
	
	//Parses integer messages
	private void parseMessage(int message){
		int reset        = message & 1;
		int kick         = (message >>> 1)  & 1;
		int motor_dleft  = (message >>> 2)  & 7;
		int motor_dright = (message >>> 5)  & 7;
		int steer_angle  = (message >>> 8)  & 511;
		int command_id   = (message >>> 17) & 511;
		
		int dleft_dir    = (motor_dleft & 4) > 0 ? -1 : 1;
		int drive_left   = dleft_dir * (motor_dleft & 3);
		
		int dright_dir   = (motor_dright & 4) > 0 ? -1 : 1;
		int drive_right   = dright_dir * (motor_dright & 3);
		
		RConsole.println("parseMessage");
		CommandHandler handler = SynchroCtrl.commandHandler;
		synchronized (handler) {
			handler.kick        = kick != 0;
			handler.drive_left  = drive_left;
			handler.drive_right = drive_right;
			handler.steer_angle = steer_angle;
			handler.command_id  = command_id;
			
			RConsole.println("notify handler");
			handler.notify();
		}
	}
	
	// send sensor data back
	public static void sendBackMessage(int messageBack) throws IOException{
		outputStream.writeInt(messageBack);
		outputStream.flush();
	}
}

class CounterThread extends Thread{
	public void run(){
		int count = 0;
		while (true){
			LCD.drawString(Integer.toString(count++), 12,0);
			count %= 1000;
			try{
				Thread.sleep(100);
			}catch(InterruptedException e){
			}
		}
	}
}

class KickThread extends Thread{
	private static boolean targetKickState = false;
	
	public void setKickState(boolean val) {
		targetKickState = val;
	}
	
	public void run(){
		while (true){
			RConsole.println("kick thread pre-wait");
			synchronized (this) {
				try{
					wait();
				}catch(InterruptedException e){
				}
			}
			RConsole.println("kick thread post-wait");
			
			if (targetKickState == true) {
				LCD.drawString("KICK!",11,1);
				Movement.motor_kick.setSpeed(900);
				Movement.motor_kick.rotate((-120*(5/3)));
				Movement.motor_kick.rotate((120*(5/3)));
			} else {
				LCD.drawString("     ",10,1);
			}
		}
	}
}

class DriveThread extends Thread{
	
	private static int targetDriveLeftVal  = 0;
	private static int targetDriveRightVal = 0;
	private int counter = 0;
	boolean ready;
	
	private int current_command = 0;
	public boolean Ready() {
		return current_command == counter && ready;
	}
	
	public void setTargetDriveVal(int left, int right) {
		targetDriveLeftVal  = left;
		targetDriveRightVal = right;
		++counter;
	}
	
	public void run(){
		Multiplexor chip = new Multiplexor(SensorPort.S4);
		
		int prev = -1;
		while(true){
			current_command = counter;
			if(current_command == prev) {
				try{
					Thread.sleep(10);
				}catch(InterruptedException e){
				}
				continue;
			}
			
			ready = false;
			
			int left = targetDriveLeftVal;
			LCD.drawString("L"+Integer.toString(left),0,1);
			if (left >= 0)
				LCD.drawString(" ",2,1);
			
			if (left == 0)
				chip.setMotors(0,0,0);
			else
				chip.setMotors(left/Math.abs(left), Math.abs(left), 0);
			
			int right = targetDriveRightVal;
			LCD.drawString("R"+Integer.toString(right),3,1);
			if (right >= 0)
				LCD.drawString(" ",5,1);
			
			if (right == 0)
				chip.setMotors(0,0,1);
			else
				chip.setMotors(right/Math.abs(right), Math.abs(right), 1);
			
			ready = true;
			prev = current_command;
		}
	}
}

class SteeringThread extends Thread{
	private static final double thresholdAngle = 30.0;
	private static final double thresholdAngleR = Math.toRadians(thresholdAngle);
	public static final double countModulo = Math.round(360 * Movement.rotConstant);
	
	private int currentSteeringCount = 0;
	private int toCount;
	protected int targetSteeringAngle = 0;
	
	private void drawLCD(int angle) {
		if (angle < 10)
			LCD.drawString("  ", 8 ,1);
		else if (angle < 100)
			LCD.drawString(" ", 9, 1);
		
		LCD.drawString(Integer.toString(angle), 7 ,1);
	}
	
	/* Return the difference in target angle and the current wheel
	 * orientation(s) in radians.
	 */
	private double getDeltaAngleR(int angle) {
		int cur_angle = getCurrentSteeringAngle();
		double delta = angle - cur_angle;
		
		// deltaR is in range [-pi,pi]
		double rad = Math.toRadians(delta);
		double deltaR = Math.atan2( Math.sin(rad), Math.cos(rad) );
		return deltaR;
	}
	
	/* Return -1 if the motor direction should be reversed for a given
	 * target angle, and 1 otherwise.
	 */
	public int getDirection(int angle) {
		double deltaR = getDeltaAngleR(angle);
		double angle2 = Math.abs(deltaR) % (2*Math.PI);
		
		if (angle2 > Math.PI)
			angle2 = Math.PI - angle2;
		
		if (Math.abs(angle2) <= Math.PI/2.0) {
			return 1;
		} else {
			return -1;
		}
	}
	
	/* Return an angle in [-90°, 90°].
	 * Use with getDirection to move the robot correctly.
	 */
	public double getClosestAngle(int angle) {
		double deltaR = getDeltaAngleR(angle);
		double sign   = deltaR / Math.abs(deltaR);
		
		// We only need to turn max 90° since we can move backwards
		// just as easily.
		if (Math.abs(deltaR) > Math.PI/2.0) {
			deltaR -= sign*Math.PI;
		}
		
		if (Math.abs(deltaR) < thresholdAngleR/2.0) {
			deltaR = 0;
		}
		else if (Math.abs(deltaR) >= thresholdAngleR/2.0 &&
				 Math.abs(deltaR) < thresholdAngleR) {
			deltaR = sign * thresholdAngleR;
		}
		
		return Math.toDegrees(deltaR);
	}
	
	public void run(){
		while(true){
			RConsole.println("steer thread pre-wait");
			synchronized (this) {
				try{
					wait();
				}catch(InterruptedException e){
				}
			}
			RConsole.println("steer thread post-wait");
			
			int target = targetSteeringAngle;
			drawLCD(target);
			SynchroCtrl.steeringLeftThread.setTargetSteeringAngle( target );
			SynchroCtrl.steeringRightThread.setTargetSteeringAngle( target );
		}
	}
	
	protected void setCurrentSteeringCount(int count){
		currentSteeringCount = count;
	}
	public int getCurrentSteeringAngle() {
		return (int)(Math.round(getCurrentSteeringCount() / Movement.rotConstant));
	}
	public int getCurrentSteeringCount() {
		return currentSteeringCount;
	}
	
	public int getToCount(){
		return toCount;
	}
	
	public void setToCount(int count){
		toCount = count;
	}
	public void setToAngle(int angle){
		setToCount((int)Math.round(angle * Movement.rotConstant));
	}
	public int getToAngle() {
		return (int)Math.round(getToCount() / Movement.rotConstant);
	}
	
	public void setTargetSteeringAngle(int val) {
		targetSteeringAngle = val;
	}
	
}

abstract class SteeringMotorThread extends SteeringThread {
	private final Motor motor;
	protected int counter = 0;
	boolean ready;
	
	private int current_command = 0;
	public boolean Ready() {
		return current_command == counter && ready;
	}
	
	public void setTargetSteeringAngle(int val) {
		super.setTargetSteeringAngle(val);
		++counter;
	}
	
	public SteeringMotorThread(Motor motor){
		this.motor = motor;
	}
	
	public abstract void drawLCD(int count);
	
	public void run(){
		motor.resetTachoCount();
		motor.regulateSpeed(true);
		motor.smoothAcceleration(true);
		
		int prev = -1;
		while(true){
			current_command = counter;
			if(current_command == prev) {
				try{
					Thread.sleep(10);
				}catch(InterruptedException e){
				}
				continue;
			}
			
			ready = false;
			int target = targetSteeringAngle;
			double deltaD = getClosestAngle(target);
			int cur_count = getCurrentSteeringCount();
			int turn_count = (int)Math.round(Movement.rotConstant * deltaD);
			int new_count = cur_count + (int)Math.round(turn_count);
			new_count %= countModulo;
			setCurrentSteeringCount(new_count);
			
			//LCD.drawString(Integer.toString(target)+" "+Integer.toString((int)deltaD), 1, 5);
			if (true)
				drawLCD((int)deltaD);
			
			if (turn_count != 0) {
				motor.rotate(turn_count);
			}
			
			ready = true;
			prev = current_command;
			
			synchronized (SynchroCtrl.commandHandler) {
				SynchroCtrl.commandHandler.notify();
			}
		}
	}
	
	public int getClosestDirection(int target, int cur) {
		int delta = target - cur;
		int mod = (int)countModulo;
		return (delta + mod/2) % mod - mod/2;
	}
	
}


class SteeringLeftThread extends SteeringMotorThread{
	public SteeringLeftThread(){
		super(Movement.motor_left);
	}
	
	public void drawLCD(int count) {
		if (count < 10)
			LCD.drawString("  ", 1 ,2);
		else if (count < 100)
			LCD.drawString(" ", 2 ,2);
		
		LCD.drawString(Integer.toString(count), 0 ,2);
	}
}

class SteeringRightThread extends SteeringMotorThread{
	public SteeringRightThread(){
		super(Movement.motor_right);
	}
	
	public void drawLCD(int count) {
		if (count < 10)
			LCD.drawString("  ", 5 ,2);
		else if (count < 100)
			LCD.drawString(" ", 6 ,2);
		
		LCD.drawString(Integer.toString(count), 4 ,2);
	}
}

class SensorChecker extends Thread{
	// Define sensor ports
	public static final SensorPort leftTouch = SensorPort.S3;
	public static final SensorPort rightTouch = SensorPort.S2;
	public static final SensorPort frontTouch = SensorPort.S1;
	
	public void run(){
		// Set sensor ports to touch
		TouchSensor front = new TouchSensor(frontTouch);
		TouchSensor left = new TouchSensor(leftTouch);
		TouchSensor right = new TouchSensor(rightTouch);
		
		// Screen messages
		String fsensorstate;
		String lsensorstate;
		String rsensorstate;
		int[] sensorMessage = new int[3];
		
		while (true) {
			// Back message - made up of primes
			// Mod on other side to check which sensors are on
			if(front.isPressed()){
				fsensorstate = "PRESSED";
				sensorMessage[0] = 2;
			} else {
				fsensorstate = "FINE";
				sensorMessage[0] = 1;
			}
			LCD.drawString("Front: " + fsensorstate, 0,4);
			
			if(left.isPressed()){
				lsensorstate = "PRESSED";
				sensorMessage[1] = 3;
			} else {
				lsensorstate = "FINE";
				sensorMessage[1] = 1;
			}
			LCD.drawString("Left: " + lsensorstate, 0,5);
			
			if(right.isPressed()){
				rsensorstate = "PRESSED";
				sensorMessage[2] = 5;
			} else {
				rsensorstate = "FINE";
				sensorMessage[2] = 1;
			}
			LCD.drawString("Right: " + rsensorstate, 0,6);
			
			try {
				if(Communicator.isConnected){
					Communicator.sendBackMessage(sensorMessage[0]*sensorMessage[1]*sensorMessage[2]);
				}
			} catch (IOException e1) {
			}
			try{
				Thread.sleep(100);
			}catch(InterruptedException e){
			}
			
		}
	}
}