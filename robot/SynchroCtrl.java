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

    public static Thread mainCommunicator;
    public static KickThread kickThread;
    public static DriveThread driveThread;
    public static SteeringThread steeringThread;
    public static SteeringThread steeringLeftThread;
    public static SteeringThread steeringRightThread;
    public static Thread counterThread;

    public static void main(String[] args) throws InterruptedException{
        mainCommunicator = new Communicator();
        kickThread = new KickThread();
        driveThread = new DriveThread();
        steeringThread = new SteeringThread();
        steeringLeftThread = new SteeringLeftThread();
        steeringRightThread = new SteeringRightThread();
        counterThread = new CounterThread();

        mainCommunicator.start();
        kickThread.start();
        driveThread.start();
        steeringThread.start();
        steeringLeftThread.start();
        steeringRightThread.start();
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


class ControlCentre{

    public static synchronized void setTargetSteeringAngle(int Angle){
        SynchroCtrl.steeringThread.setTargetSteeringAngle(Angle);
        synchronized (SynchroCtrl.steeringThread) {
            SynchroCtrl.steeringThread.notify();
        }
    }

    public static synchronized void setTargetDriveLeftVal(int Val){
        SynchroCtrl.driveThread.setTargetDriveLeftVal(Val);
        synchronized (SynchroCtrl.driveThread) {
            SynchroCtrl.driveThread.notify();
        }
    }

    public static synchronized void setTargetDriveRightVal(int Val){
        SynchroCtrl.driveThread.setTargetDriveRightVal(Val);
        synchronized (SynchroCtrl.driveThread) {
            SynchroCtrl.driveThread.notify();
        }
    }

    public static synchronized void setKickState(boolean Val){
        SynchroCtrl.kickThread.setKickState(Val);
        synchronized (SynchroCtrl.kickThread) {
            SynchroCtrl.kickThread.notify();
        }
    }
}

class Communicator extends Thread {
    // Defines variables used for the managing bluetooth connection
    private static BTConnection connection;
    private static DataInputStream inputStream;
    private static DataOutputStream outputStream;

    public Communicator(){
    }
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

    private static void collectMessage() throws InterruptedException{
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
    private static void parseMessage(int message){
        int reset = message & 1;
        int kick = (message >>> 1) & 1;
        int motor_dleft = (message >>> 2) & 7;
        int motor_dright = (message >>> 5) & 7;
        int motor_sleft = (message >>> 8) & 511;
        int motor_sright = (message >>> 17) & 511;

        ControlCentre.setKickState(( kick != 0));
        ControlCentre.setTargetSteeringAngle(motor_sleft);
        ControlCentre.setTargetDriveLeftVal(motor_dleft);
        ControlCentre.setTargetDriveRightVal(motor_dright);
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

    public KickThread(){
    }

    public void run(){
        while (true){
            try{
                wait();
            }catch(InterruptedException e){
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

    private static int targetDriveLeftVal = 0;
    private static int targetDriveRightVal =0;

    public void setTargetDriveLeftVal(int val) {
        targetDriveLeftVal = val;
    }
    public void setTargetDriveRightVal(int val) {
        targetDriveRightVal = val;
    }

    public DriveThread(){
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
    private static final double C = Movement.rotConstant;

    private static int currentSteeringAngle = 0;
    private static int targetSteeringAngle = 0;
    private static int toAngle;

    public void setTargetSteeringAngle(int val) {
        targetSteeringAngle = val;
    }

    public SteeringThread(){
    }

    public void run(){
        while(true){
            synchronized (this) {
                try{
                    wait();
                }catch(InterruptedException e){
                }
            }

            if (targetSteeringAngle < 10)
                LCD.drawString("  ", 8 ,2);
            else if (targetSteeringAngle < 100)
                LCD.drawString(" ", 9 ,2);
            LCD.drawString(Integer.toString(targetSteeringAngle), 7 ,1);

            int cur_angle = getCurrentSteeringAngle();
            double delta = targetSteeringAngle - cur_angle;
            double turn_angle = 0;

            if (Math.abs(delta) < thresholdAngle/2.0) {
                continue;
            }
            else if (Math.abs(delta) >= thresholdAngle/2.0 &&
                     Math.abs(delta) < thresholdAngle) {
                delta = thresholdAngle*delta/Math.abs(delta);
            }
            setCurrentSteeringAngle( (int)(cur_angle+delta)%360 );

            if (delta != 0 && Math.abs(delta) < 180) {
                turn_angle = C * delta;
            }
            else if (delta >= 180 && delta < 360) {
                turn_angle = -C * (360 - delta);
            }
            else if (delta <= -180) {
                turn_angle = C * (360 + delta);
            }
            else { /* No turning needed */
                continue;
            }

            int rounded_angle = (int)Math.round(turn_angle);
            SynchroCtrl.steeringLeftThread.setToAngle( rounded_angle );
            SynchroCtrl.steeringRightThread.setToAngle( rounded_angle );

            synchronized (SynchroCtrl.steeringLeftThread) {
                SynchroCtrl.steeringLeftThread.notify();
            }
            synchronized (SynchroCtrl.steeringRightThread) {
                SynchroCtrl.steeringRightThread.notify();
            }
        }
    }

    private synchronized int getCurrentSteeringAngle(){
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

class SteeringLeftThread extends SteeringThread{
    public SteeringLeftThread(){
    }

    public void run(){
        Movement.motor_left.resetTachoCount();
        Movement.motor_left.regulateSpeed(true);
        Movement.motor_left.smoothAcceleration(true);

        while(true){
            try{
                wait();
            }catch(InterruptedException e){
            }

            int angle = getToAngle();

            if (false) {
                if (angle < 10)
                    LCD.drawString("  ", 8 ,1);
                else if (angle < 100)
                    LCD.drawString(" ", 9 ,1);
                LCD.drawString(Integer.toString(angle), 7 ,1);
                LCD.drawString("R", 11 ,1);
            }

            Movement.motor_left.rotate(angle);
        }
    }
}

class SteeringRightThread extends SteeringThread{
    public SteeringRightThread(){
    }

    public void run(){
        Movement.motor_right.resetTachoCount();
        Movement.motor_right.regulateSpeed(true);
        Movement.motor_right.smoothAcceleration(true);

        while(true){
            try{
                wait();
            }catch(InterruptedException e){
            }

            int angle = getToAngle();

            if (false) {
                if (angle < 10)
                    LCD.drawString("  ", 13 ,1);
                else if (angle < 100)
                    LCD.drawString(" ", 14 ,1);
                LCD.drawString(Integer.toString(angle), 12 ,1);
            }

            Movement.motor_right.rotate(angle);
        }
    }
}


