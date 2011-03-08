import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

// Lejos imports
import lejos.nxt.*;
import lejos.nxt.comm.*;


// Collect commands, write to screen
public class SynchroCtrl {

    //Defines the buttons
    private static final Button button_left = Button.LEFT;
    private static final Button button_right = Button.RIGHT;
    private static final Button button_enter = Button.ENTER;

    public static Communicator mainCommunicator;
    public static KickThread kickThread;
    public static DriveThread driveThread;
    public static SteeringThread steeringThread;
    public static SteeringMotorThread steeringLeftThread;
    public static SteeringMotorThread steeringRightThread;
    public static CounterThread counterThread;
    public static CommandHandler commandHandler;

    public static void main(String[] args) throws InterruptedException{
        mainCommunicator = new Communicator();
        kickThread = new KickThread();
        driveThread = new DriveThread();
        steeringThread = new SteeringThread();
        steeringLeftThread = new SteeringLeftThread();
        steeringRightThread = new SteeringRightThread();
        counterThread = new CounterThread();
        commandHandler = new CommandHandler();

        mainCommunicator.start();
        kickThread.start();
        driveThread.start();
        steeringThread.start();
        steeringLeftThread.start();
        steeringRightThread.start();
        commandHandler.start();
        //counterThread.start();
    }
}

class Movement {

    //Defines the motors used for steering the right and left wheels
    public static final Motor motor_left = Motor.A;
    public static final Motor motor_right = Motor.B;

    //Defines the motor used for the kicker
    public static final Motor motor_kick = Motor.C;

    //Defines the number of motor turns to wheel turns
    public static final double rotConstant = 56.0 / 24.0;

    //Defines the sensor port used to power the communication light
    public static final SensorPort port_comlight = SensorPort.S1;
}


class CommandHandler extends Thread {

    public static boolean kick;
    public static int drive_left;
    public static int drive_right;
    public static int steer_angle;
    public static int command_id;

    public static void setKickState(boolean Val){
        SynchroCtrl.kickThread.setKickState(Val);
        synchronized (SynchroCtrl.kickThread) {
            SynchroCtrl.kickThread.notify();
        }
    }

    public static void setTargetDriveVal(int left, int right){
        SynchroCtrl.driveThread.setTargetDriveLeftVal(left);
        SynchroCtrl.driveThread.setTargetDriveRightVal(right);
        synchronized (SynchroCtrl.driveThread) {
            SynchroCtrl.driveThread.notify();
        }
    }

    public static void setTargetSteeringAngle(int Angle){
        SynchroCtrl.steeringThread.setTargetSteeringAngle(Angle);
        synchronized (SynchroCtrl.steeringThread) {
            SynchroCtrl.steeringThread.notify();
        }
    }

    public void run(){
        while (true){
            synchronized (this) {
                try{
                    wait();
                }catch(InterruptedException e){
                }
            }
            executeCommand();
        }
    }

    private void executeCommand() {
        switch (command_id) {
        case 1:
            moveTo(steer_angle, drive_left);
            break;

        case 2:
            orientTo(steer_angle);
            break;

        default:
            /* By default, just execute the raw commands: */
            int dir = SynchroCtrl.steeringThread.getDirection(steer_angle);
            setTargetDriveVal(dir*drive_left, dir*drive_right);
            setTargetSteeringAngle(steer_angle);
            break;
        }

        setKickState(kick);
    }

    /* Wait until steering has finished. */
    private void waitForSteering() {
        synchronized (SynchroCtrl.steeringLeftThread) {
            try{
                wait();
            }catch(InterruptedException e){
            }
        }
        synchronized (SynchroCtrl.steeringRightThread) {
            try{
                wait();
            }catch(InterruptedException e){
            }
        }
    }

    /* Move towards some bearing at positive integer speed */
    private void moveTo(int angle, int speed) {

        setTargetDriveVal(0, 0);
        setTargetSteeringAngle(angle);
        waitForSteering();

        speed *= SynchroCtrl.steeringThread.getDirection(angle);
        setTargetDriveVal(speed, speed);
    }

    private void orientTo(int angle) {
        setTargetDriveVal(0, 0);
        setTargetSteeringAngle(45);
        waitForSteering();

        // TODO: There should be a way to estimate how to orient the
        // robot accurately, and ideally we would find the nearest
        // <=180 to turn towards.
        setTargetDriveVal(2, 2);
        try{
            Thread.sleep(4 * angle);
        } catch (InterruptedException e){
        }
        setTargetDriveVal(0, 0);
    }
}

class Communicator extends Thread {
    // Defines variables used for the managing bluetooth connection
    private static BTConnection connection;
    private static DataInputStream inputStream;
    private static DataOutputStream outputStream;

    public void run(){
        connect();
        try{
            collectMessage();
        } catch (InterruptedException e){
            LCD.drawString("Msg Col Interrupt", 7,0);
        }
    }

    //Aims to establish a conection over Bluetooth
    private static void connect(){
        LCD.drawString("Trying to connect", 7,0);

        // Wait until connected
        connection = Bluetooth.waitForConnection();
        LCD.drawString("Connected", 7,0);

        inputStream = connection.openDataInputStream();
        outputStream = connection.openDataOutputStream();
        LCD.drawString("Connection opened", 7,0);
    }

    private void collectMessage() throws InterruptedException{
        for (int N = 0 ;; ++N) {
            try{
                //Bluetooth.getConnectionStatus();
                LCD.drawString("Recv:"+Integer.toString(N), 2, 2);
                int message = inputStream.readInt();
                LCD.drawString("Rcvd:"+Integer.toString(N), 2, 3);
                //LCD.drawString("display"+Integer.toString(N), 6, 0);
                LCD.drawString("        ", 6, 6);
                LCD.drawString("Msg: "+Integer.toString(message), 0, 6);
                //LCD.drawString("decode:"+Integer.toString(N), 6, 1);
                parseMessage(message);
                //LCD.drawString("decoded:"+Integer.toString(N), 6, 0);
            } catch (IOException e) {
                LCD.drawString("Error: connect back up", 7,0);
                connection = Bluetooth.waitForConnection();
                LCD.drawString("Connection opened", 7,0);
            }

        }
    }

    //Parses integer messages
    private void parseMessage(int message){
        int reset        = message & 1;
        int kick         = (message >>> 1)  & 1;
        int motor_dleft  = (message >>> 2)  & 7;
        int motor_dright = (message >>> 5)  & 7;
        int steer_angle  = (message >>> 8)  & 511;
        int command_id   = (message >>> 17) & 511;

        CommandHandler handler = SynchroCtrl.commandHandler;
        synchronized (handler) {
            handler.kick        = kick != 0;
            handler.drive_left  = motor_dleft;
            handler.drive_right = motor_dright;
            handler.steer_angle = steer_angle;
            handler.command_id  = command_id;

            notify();
        }
    }

    // send sensor data back?
    public static void sendBackMessage(int messageBack) throws IOException{
        outputStream.writeInt(messageBack);
        outputStream.flush();
    }
}

class CounterThread extends Thread{
    public void run(){
        int count = 0;
        while (true){
            LCD.drawString(Integer.toString(count++), 12,0);
            count %= 1000;
            try{
                Thread.sleep(100);
            }catch(InterruptedException e){
            }
        }
    }
}

class KickThread extends Thread{
    private static boolean targetKickState = false;

    public void setKickState(boolean val) {
        targetKickState = val;
    }

    public void run(){
        while (true){
            synchronized (this) {
                try{
                    wait();
                }catch(InterruptedException e){
                }
            }

            if (targetKickState == true) {
                LCD.drawString("KICK!",10,1);
                Movement.motor_kick.setSpeed(900);
                Movement.motor_kick.rotate((-120*(5/3)));
                Movement.motor_kick.rotate((120*(5/3)));
            } else {
                LCD.drawString("     ",10,1);
            }
        }
    }
}

class DriveThread extends Thread{

    private static int targetDriveLeftVal  = 0;
    private static int targetDriveRightVal = 0;

    public void setTargetDriveLeftVal(int val) {
        targetDriveLeftVal = val;
    }
    public void setTargetDriveRightVal(int val) {
        targetDriveRightVal = val;
    }

    public void run(){
        Multiplexor chip = new Multiplexor(SensorPort.S4);
        while(true){
            synchronized (this) {
                try{
                    wait();
                }catch(InterruptedException e){
                }
            }

            LCD.drawString(Integer.toString(targetDriveLeftVal)+",",2,1);
            switch(targetDriveLeftVal){
            case 0:
            case 4:
                chip.setMotors(0,0,0);
                break;
            case 1:
                chip.setMotors(1,1,0);
                break;
            case 2:
                chip.setMotors(1,2,0);
                break;
            case 3:
                chip.setMotors(1,3,0);
                break;
            case 5:
                chip.setMotors(-1,1,0);
                break;
            case 6:
                chip.setMotors(-1,2,0);
                break;
            case 7:
                chip.setMotors(-1,3,0);
                break;
            }

            LCD.drawString(Integer.toString(targetDriveRightVal)+" L",4,1);
            switch(targetDriveRightVal){
            case 0:
            case 4:
                chip.setMotors(0,0,1);
                break;
            case 1:
                chip.setMotors(1,1,1);
                break;
            case 2:
                chip.setMotors(1,2,1);
                break;
            case 3:
                chip.setMotors(1,3,1);
                break;
            case 5:
                chip.setMotors(-1,1,1);
                break;
            case 6:
                chip.setMotors(-1,2,1);
                break;
            case 7:
                chip.setMotors(-1,3,1);
                break;
            }

        }
    }
}

class SteeringThread extends Thread{
    private static final double thresholdAngle = 30.0;
    private static final double thresholdAngleR = Math.toRadians(thresholdAngle);
    private static final double C = Movement.rotConstant;

    private static int currentSteeringAngle = 0;
    private static int targetSteeringAngle = 0;
    private static int toAngle;

    public void setTargetSteeringAngle(int val) {
        targetSteeringAngle = val;
    }

    public SteeringThread(){
    }

    private void drawLCD(int angle) {
        if (angle < 10)
            LCD.drawString("  ", 8 ,2);
        else if (angle < 100)
            LCD.drawString(" ", 9 ,2);

        LCD.drawString(Integer.toString(angle), 7 ,1);
    }

    /* Return the difference in target angle and the current wheel
     * orientation(s) in radians.
     */
    private double getDeltaAngleR(int angle) {
        int cur_angle = getCurrentSteeringAngle();
        double delta = angle - cur_angle;

        // deltaR is in range [-pi,pi]
        double rad = Math.toRadians(delta);
        double deltaR = Math.atan2( Math.sin(rad), Math.cos(rad) );
        return deltaR;
    }

    /* Return -1 if the motor direction should be reversed for a given
     * target angle, and 1 otherwise.
     */
    public int getDirection(int angle) {
        double deltaR = getDeltaAngleR(angle);
        if (Math.abs(deltaR) <= Math.PI/2.0) {
            return 1;
        } else {
            return -1;
        }
    }

    /* Return an angle in [-90°, 90°].
     * Use with getDirection to move the robot correctly.
    */
    private double getClosestAngle(int angle) {
        double deltaR = getDeltaAngleR(angle);
        double sign   = deltaR / Math.abs(deltaR);

        // We only need to turn max 90° since we can move backwards
        // just as easily.
        if (Math.abs(deltaR) > Math.PI/2.0) {
            deltaR -= sign*Math.PI;
        }

        if (Math.abs(deltaR) < thresholdAngleR/2.0) {
            deltaR = 0;
        }
        else if (Math.abs(deltaR) >= thresholdAngleR/2.0 &&
                 Math.abs(deltaR) < thresholdAngleR) {
            deltaR = sign * thresholdAngleR;
        }

        return Math.toDegrees(deltaR);
    }

    public void run(){
        while(true){
            synchronized (this) {
                try{
                    wait();
                }catch(InterruptedException e){
                }
            }
            drawLCD(targetSteeringAngle);

            double deltaD = getClosestAngle(targetSteeringAngle);
            int cur_angle = getCurrentSteeringAngle();
            int new_angle = (cur_angle + (int)Math.round(deltaD)) % 360;
            setCurrentSteeringAngle(new_angle);

            int turn_angle = (int)Math.round(C * deltaD);
            SynchroCtrl.steeringLeftThread.setToAngle( turn_angle );
            SynchroCtrl.steeringRightThread.setToAngle( turn_angle );

            synchronized (SynchroCtrl.steeringLeftThread) {
                SynchroCtrl.steeringLeftThread.notify();
            }
            synchronized (SynchroCtrl.steeringRightThread) {
                SynchroCtrl.steeringRightThread.notify();
            }
        }
    }

    public synchronized int getCurrentSteeringAngle(){
        return currentSteeringAngle;
    }

    private synchronized void setCurrentSteeringAngle(int Angle){
        currentSteeringAngle = Angle;
    }

    public synchronized int getToAngle(){
        return toAngle;
    }

    public synchronized void setToAngle(int Angle){
        toAngle = Angle;
    }
}

abstract class SteeringMotorThread extends SteeringThread {
    private final Motor motor;
    public SteeringMotorThread(Motor motor){
        this.motor = motor;
    }

    public abstract void drawLCD(int angle);

    public void run(){
        motor.resetTachoCount();
        motor.regulateSpeed(true);
        motor.smoothAcceleration(true);

        while(true){
            synchronized (this) {
                try{
                    wait();
                }catch(InterruptedException e){
                }
            }
            int angle = getToAngle();
            if (false)
                drawLCD(angle);

            if (angle != 0)
                motor.rotate(angle);

            synchronized (this) {
                notifyAll();
            }
        }
    }
}

class SteeringLeftThread extends SteeringMotorThread{
    public SteeringLeftThread(){
        super(Movement.motor_left);
    }

    public void drawLCD(int angle) {
        if (angle < 10)
            LCD.drawString("  ", 8 ,1);
        else if (angle < 100)
            LCD.drawString(" ", 9 ,1);

        LCD.drawString(Integer.toString(angle), 7 ,1);
        LCD.drawString("R", 11 ,1);
    }
}

class SteeringRightThread extends SteeringMotorThread{
    public SteeringRightThread(){
        super(Movement.motor_right);
    }

    public void drawLCD(int angle) {
        if (angle < 10)
            LCD.drawString("  ", 13 ,1);
        else if (angle < 100)
            LCD.drawString(" ", 14 ,1);

        LCD.drawString(Integer.toString(angle), 12 ,1);
    }
}

