
//Lejos libraries
import lejos.nxt.*;

// Tests motors in both directions
public class SensorMotor {

	public static void main(String[] args) throws InterruptedException{
		 SensorPort port = SensorPort.S1;     
	     port.setPowerType(port.POWER_RCX);
		int sleeptime = 2000;
		 while (sleeptime > 0) {
			 port.activate();                   // Turns motor on
			 Thread.sleep(sleeptime);
			 port.passivate();                  // Turns motor off
			 sleeptime = sleeptime - 100;
		 }
	     
	}
	
}

