// Lejos libraries
import lejos.nxt.*;

// Simple kicker program
public class Kick {

	public static void main(String[] args) throws InterruptedException{
		// Kick, wait 3 seconds then kick again
		kick(500);
		Thread.sleep(3000);
		kick(500);
	}
	
	// Turns the motor forward for a specified amount of time then stops
	public static void kick(int sleeptime) throws InterruptedException{
		Motor.A.forward();
		LCD.drawString("KICKING!!", 0, 0);
		Thread.sleep(sleeptime);
		Motor.A.stop();
		LCD.drawString("waiting", 0, 1);
	}
}




