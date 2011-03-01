import lejos.nxt.SensorPort;

public class MuxTester {
	
	public static void main(String[] args) throws Exception{
		Multiplexor chip = new Multiplexor(SensorPort.S4);
		chip.setMotors(0,2,0);
		Thread.sleep(1000);
		chip.setMotors(0,0,0);
		Thread.sleep(1000);
		chip.setMotors(0,2,0);
		Thread.sleep(1000);
	}
}
