import java.io.DataInputStream;
import java.io.IOException;

// Lejos imports
import lejos.nxt.*;
import lejos.nxt.comm.*;

// Collect commands, write to screen
public class BluetoothTester {

	private static BTConnection connection;
	private static DataInputStream inputStream;

	public static void main(String[] args) throws InterruptedException{
		connect();
		collectMessage();
	}
	
	public static void connect(){
		writeToScreen("Trying to connect");
		// Wait until connected
		connection = Bluetooth.waitForConnection();
		writeToScreen("Connected"); 
		inputStream = connection.openDataInputStream();
		writeToScreen("Connection Opened"); 
	}

	private static void collectMessage() throws InterruptedException{
		while(true){
			try {
				// Parse if there are any messages
				if(inputStream.available()>0){
					writeToScreen("Got message");
					int message = inputStream.readInt();
					// Do specific action
					if (message == 1){
						kicker();
					}
					writeToScreen("Done");	
				}
			} catch (IOException e) {
				writeToScreen("Error");
			}
		}
	}

	// Writes a message to the brick's screen
	public static void writeToScreen(String message){
		LCD.clearDisplay();
		LCD.drawString(message, 0, 0);
		LCD.refresh();
	}
	
	// Activate kicker
	public static void kicker() throws InterruptedException{
		writeToScreen("Kick");
		Motor.A.forward();
		Motor.A.setSpeed(800);
		Thread.sleep(417);
		Motor.A.stop();
		Button.waitForPress();
	}
}
