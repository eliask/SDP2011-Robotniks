import lejos.nxt.I2CPort;
import lejos.nxt.I2CSensor;

public class Multiplexor extends I2CSensor{

	public Multiplexor(I2CPort port){
		super(port);
		setAddress(0x5A);
	}

	public static void main(String[] args){	
	}

	public void setMotors(int directionIndex, int speedIndex, int wheelIndex){
		// sets up possible values 
		byte[] directionValues = new byte [3];
		directionValues[0] = (byte)1;
		directionValues[1] = (byte)0;
		directionValues[2] = (byte)2;
		byte[] speedValues = new byte [3];
		speedValues[0] = (byte)0;
		speedValues[1] = (byte)130;
		speedValues[2] = (byte)255;

		// sets specific values
		byte direction = directionValues[directionIndex];
		byte speed = speedValues[speedIndex];

		switch (wheelIndex){
		// right wheel
		case 0:		 
			sendData((byte)0x01,direction); 
			sendData((byte)0x02,speed);
			break;
		// left wheel
		case 1:
			sendData((byte)0x03,direction); 
			sendData((byte)0x04,speed);
			break;
		}
	}
}
