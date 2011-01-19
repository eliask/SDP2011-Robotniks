
//Lejos libraries
import lejos.nxt.*;

// Tests motors in both directions
public class SensorMotor {

	public static void main(String[] args) throws InterruptedException{
		 SensorPort port = SensorPort.S1;     
	     port.setPowerType(port.POWER_STD);
	       
	     port.activate();                   // Turns motor on
	     Thread.sleep(2000);
	     port.passivate();                  // Turns motor off 
	     
	}
	
}

