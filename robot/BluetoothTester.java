import java.io.DataInputStream;
import java.io.IOException;

// Lejos imports
import lejos.nxt.*;
import lejos.nxt.comm.*;

// Collect commands, write to screen
public class BluetoothTester {

	private static BTConnection connection;
	private static DataInputStream inputStream;
	private static boolean keepConnOpen;

	public static void main(String[] args) throws InterruptedException{
		keepConnOpen = true;
		connect();
		collectMessage();
		close();
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
		while(keepConnOpen){
			try {
				// Parse if there are any messages
				if(inputStream.available()>0){
					writeToScreen("Got message");
					int message = inputStream.readInt();
					// Do specific action
					if (message == 0){
						keepConnOpen = false;
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
	
	// Closes connection
	public static void close(){
		try {
			inputStream.close();
			writeToScreen("Closing");
		} catch (IOException e) {
			writeToScreen("Could not close");
		}
		connection.close();
	}
	
}