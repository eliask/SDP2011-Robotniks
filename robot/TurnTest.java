// Lejos libraries
import lejos.nxt.*;

//Test turning the wheels through given degrees.
public class TurnTest {
	
	private static int steeringangle = 0;
	private static Motor motor_a = Motor.A;
	private static Motor motor_b = Motor.B;
	private static Motor motor_c = Motor.C;
	
	private static final double rotConstant = 2.375;
	
	public static void main(String[] args) throws InterruptedException{
		
		//Resets the Tachometer and sets the motor speed
		motor_a.resetTachoCount();
		
		motor_a.setSpeed(400);
		motor_b.setSpeed(400);
		
		//Turn to 45 Degrees
		SetRobotDirection(45);
		LCD.drawString("Turned 45Deg", 0 , 1);
		Button.waitForPress();
		
		//Turn to 215 Degrees
		SetRobotDirection(215);
		LCD.drawString("Turned 215Deg", 0 , 1);
		Button.waitForPress();
		
		//Turn to 90 Degrees
		SetRobotDirection(90);
		LCD.drawString("Turned 90Deg", 0 , 1);
		Button.waitForPress();
		
		//Turn to 0 Degrees
		SetRobotDirection(0);
		LCD.drawString("Turned 0Deg", 0 , 1);
		Button.waitForPress();
	
	}
	
	//Sets the robot's direction to the input direction in degrees
	public static void SetRobotDirection(int DirectionDEGs){
		if (DirectionDEGs > steeringangle){
			motor_a.rotate((int)(rotConstant * (DirectionDEGs - steeringangle)),false);
			motor_b.rotate((int)(rotConstant * (DirectionDEGs - steeringangle)),false);
			steeringangle = DirectionDEGs;
		} else if (DirectionDEGs < steeringangle){
			motor_a.rotate((int)(-1*(steeringangle - DirectionDEGs)*rotConstant),false);
			motor_b.rotate((int)(-1*(steeringangle - DirectionDEGs)*rotConstant),false);
			steeringangle = DirectionDEGs;
		}
	}
}
