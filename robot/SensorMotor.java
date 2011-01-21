
//Lejos libraries
import lejos.nxt.*;

// Tests motors in both directions
public class SensorMotor {

	public static void main(String[] args) throws InterruptedException{
		 SensorPort port1 = SensorPort.S1;     
		 port1.setPowerType(port1.POWER_9V); 
		 int sleeptime = 10000;
		 while (sleeptime > 0) {
			 port1.activate();                   // Turns motor on
			 Thread.sleep(sleeptime);
			 port1.passivate();                  // Turns motor off
			 LCD.clearDisplay();
			 LCD.drawInt(sleeptime,0,1);
			 Thread.sleep(sleeptime);
			 sleeptime = sleeptime - 10000;
		 }
	     
	}
	
}

