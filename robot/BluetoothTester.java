import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

// Lejos imports
import lejos.nxt.*;
import lejos.nxt.comm.*;

// Collect commands, write to screen
public class BluetoothTester {

	private static BTConnection connection;
	private static DataInputStream inputStream;
	private static DataOutputStream outputStream;
	private static boolean keepConnOpen = true;

	public static void main(String[] args) throws InterruptedException, IOException{
		connect();
		collectMessage();
		close();
	}

	public static void connect() throws IOException{
		writeToScreen("Trying to connect");
		// Wait until connected
		connection = Bluetooth.waitForConnection();
		writeToScreen("Connected"); 
		inputStream = connection.openDataInputStream();
		outputStream = connection.openDataOutputStream();
		writeToScreen("Connection Opened"); 
	}

	private static void collectMessage() throws InterruptedException{
		while(keepConnOpen){
			try {
				int message = inputStream.readInt();
				writeToScreen("Got message");
				// Do specific action
				if (message == 0){
					keepConnOpen = false;
				} else {
					kick();
					sendMessage();
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

	// Writes a message to the brick's screen
	public static void writeIntToScreen(int message){
		LCD.clearDisplay();
		LCD.drawInt(message, 0, 0);
		LCD.refresh();
	}

	public static void kick() throws InterruptedException, IOException{
		writeToScreen("Kick");
		Motor.C.setSpeed(900);
		Motor.C.forward();
		Thread.sleep(200);
		Motor.C.stop();
	}
	
	public static void sendMessage() throws InterruptedException, IOException{
		int numb = outputStream.size();
		writeIntToScreen(numb);
		outputStream.writeInt(numb);
		outputStream.flush();
		Thread.sleep(200);
		numb = outputStream.size();
		writeIntToScreen(numb);
	}

	// Closes connection
	public static void close() throws IOException{
		inputStream.close();
		outputStream.close();
		writeToScreen("Closing");
		connection.close();
	}
}