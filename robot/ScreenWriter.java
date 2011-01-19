// Lejos libraries
import lejos.nxt.*;
import lejos.nxt.comm.*;

// Simple connection tester
public class ScreenWriter {

	public static void main(String[] args){
		writeToScreen("Trying to connect", 0);
		// Waits until a device connects to it
		Bluetooth.waitForConnection();
		writeToScreen("Connected", 0);
		Button.waitForPress();
	}

	// Writes a message to a specific line on the brick lcd
	public static void writeToScreen(String message, int line){
		LCD.drawString(message, 0, line);
		LCD.refresh();
	}

}
