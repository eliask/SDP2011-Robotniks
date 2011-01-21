// Lejos libraries
import lejos.nxt.*;

//Test turning the wheels through given degrees.
public class TurnTest {
	
	private static int steeringangle_left = 0;
	private static int steeringangle_right = 0;
	private static Motor motor_left = Motor.A;
	private static Motor motor_right = Motor.B;
	
	private static Motor motor_c = Motor.C;
	
	//Defines the number of motor turns to wheel turns
	private static final double rotConstant = 2.375;
	
	//Defines the speed of the motors for driving the robot (time for a degree of central turn)
	private static final double motorConstant = 1;
	
	public static void main(String[] args) throws InterruptedException{
		
		//Resets the Tachometer and sets the motor speed
		motor_left.resetTachoCount();
		motor_right.resetTachoCount();
		
		motor_left.setSpeed(400);
		motor_right.setSpeed(400);
		
		//Test Set Direction
		
			//LCD.drawString("Set Direction Tests", 0 , 1);
			//Button.waitForPress();
		
			//Turn to 45 Degrees
				//SetRobotDirection(45);
				//LCD.drawString("Turned 45Deg", 0 , 1);
				//Button.waitForPress();
			
			//Turn to 215 Degrees
				//SetRobotDirection(215);
				//LCD.drawString("Turned 215Deg", 0 , 1);
				//Button.waitForPress();
			
			//Turn to 90 Degrees
				//SetRobotDirection(90);
				//LCD.drawString("Turned 90Deg", 0 , 1);
				//Button.waitForPress();
			
			//Turn to 0 Degrees
				//SetRobotDirection(0);
				//LCD.drawString("Turned 0Deg", 0 , 1);
				//Button.waitForPress();
		
		//Test Central Spin
			
			LCD.drawString("Central Spin Tests", 0 , 1);
			Button.waitForPress();
			
			//Turn to 20 Degrees
			SetRobotDirection(20);
			LCD.drawString("Turned 20Deg", 0 , 1);
			Button.waitForPress();
			
			//Spin 40 Degrees
			CentralSpin(40);
			LCD.drawString("Spun 40Deg", 0 , 1);
			Button.waitForPress();
			
			//Turn to 180Degrees
			SetRobotDirection(180);
			LCD.drawString("Turned 90Deg", 0 , 1);
			Button.waitForPress();
			
			//Spin 40 Degrees
			CentralSpin(40);
			LCD.drawString("Spun 40Deg", 0 , 1);
			Button.waitForPress();
			
			//Turn to 340 Degrees
			SetRobotDirection(340);
			LCD.drawString("Turned 340Deg", 0 , 1);
			Button.waitForPress();
			
			//Spin 40 Degrees
			CentralSpin(40);
			LCD.drawString("Spun 40Deg", 0 , 1);
			Button.waitForPress();
	
	}
	
	//Sets the robot's direction to the input direction in degrees
	public static void SetRobotDirection(int DirectionDEGs){
		// For the left motor
		if (DirectionDEGs > steeringangle_left){
			motor_left.rotate((int)(rotConstant * (DirectionDEGs - steeringangle_left)),false);
			steeringangle_left = DirectionDEGs;
		} else if (DirectionDEGs < steeringangle_left){
			motor_left.rotate((int)(-1*(steeringangle_left - DirectionDEGs)*rotConstant),false);
			steeringangle_left = DirectionDEGs;
		}
		
		// For the right motor
		if (DirectionDEGs > steeringangle_right){
			motor_right.rotate((int)(rotConstant * (DirectionDEGs - steeringangle_right)),false);
			steeringangle_right = DirectionDEGs;
		} else if (DirectionDEGs < steeringangle_right){
			motor_right.rotate((int)(-1*(steeringangle_right - DirectionDEGs)*rotConstant),false);
			steeringangle_right = DirectionDEGs;
		}
	}
	
	public static void CentralSpin(int ByDegrees){
		
		LCD.clearDisplay();
		LCD.drawInt(steeringangle_right, 0 , 1);
		Button.waitForPress();
		
		//For the left (rotate wheels to 135Deg)
		if ((steeringangle_left % 360) > 315){
			motor_left.rotate((int) (rotConstant * (135 + (360 - (steeringangle_left % 360)))));
		} else if((steeringangle_left % 360) < 135){
			motor_left.rotate((int) (rotConstant * (135 - (steeringangle_left % 360))));
		} else if ((steeringangle_left % 360) >= 135 && ((steeringangle_left % 360) <= 315)) {
			motor_left.rotate((int) (rotConstant * -1 * ((steeringangle_left %360) - 135)));
		}
		
		LCD.clearDisplay();
		LCD.drawInt(steeringangle_right, 0 , 1);
		Button.waitForPress();
		
		//For the right (rotate wheels to 315Deg)
		if ((steeringangle_right % 360) > 315){
			motor_right.rotate((int) (rotConstant * -1 *((steeringangle_right % 360)-315)));
			LCD.clearDisplay();
			LCD.drawInt(((int) -1 *((steeringangle_right % 360)-315)), 0 , 1);
			Button.waitForPress();
		} else if((steeringangle_right % 360) < 135){
			motor_right.rotate((int) (rotConstant * -1 *(45 +( steeringangle_right % 360))));
			LCD.clearDisplay();
			LCD.drawInt(((int) (rotConstant * -1 *(45 +( steeringangle_right % 360)))), 0 , 1);
			Button.waitForPress();
		} else if ((steeringangle_right % 360) >= 135 && ((steeringangle_right % 360) <= 315)) {
			motor_right.rotate((int) (rotConstant * (180 - ((steeringangle_right % 360) - 45))));
			LCD.clearDisplay();
			LCD.drawInt(((int)  (180 - ((steeringangle_right % 360) - 45))), 0 , 1);
			Button.waitForPress();
		}
		
		// ** insert drive code **
		
		LCD.drawString("Spun angle", 0 , 1);
		Button.waitForPress();
		
		//Reset steering to 0Deg on both wheels
		motor_left.rotate((int)(rotConstant * -135));
		motor_right.rotate((int) (rotConstant * 45));
	}
}
