// Lejos libraries
import lejos.nxt.*;

// Tests motors in both directions
public class TestMotor {

	public static void main(String[] args) throws InterruptedException{
		// Creates an area of motors
		Motor [] m = {Motor.A, Motor.B};
		
		// Spins them forward for 3 seconds
		for(int i = 0; i<2; i++){
			m[i].forward();
		}
		LCD.drawString("FORWARD", 0, 0);
		Thread.sleep(3000);
		
		// Spins them backward for 3 seconds
		for(int i = 0; i<2; i++){
			m[i].backward();
		}
		LCD.drawString("BACKWARD", 0, 1);
		Thread.sleep(3000);
		
		// Spins them forward again for 3 seconds
		for(int i = 0; i<2; i++){
			m[i].reverseDirection();
		}
		LCD.drawString("FORWARD", 0, 2);
		Thread.sleep(3000);
		
		// Stops the motors
		for(int i = 0; i<2; i++){
			m[i].stop();
		}
	}
}

