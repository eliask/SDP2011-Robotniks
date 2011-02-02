// Lejos libraries
import lejos.nxt.*;


// Tests motors in both directions
public class TestThreads {

    public static Motor ma = Motor.A;
    public static Motor mb = Motor.B;

	public static void main(String[] args) throws InterruptedException{
	    Thread thread1 = new RMotorAThread();
		Thread thread2 = new RMotorBThread();

		thread1.start();
		thread2.start();
		Thread.sleep(3000);
	
	}
}

class RMotorAThread extends Thread {

	Thread runner;
	public RMotorAThread() {
	}
	public void run() {
	    LCD.drawString("ma", 0, 0);
	    TestThreads.ma.rotate(720);
	}
}

class RMotorBThread extends Thread {

	Thread runner;
	public RMotorBThread() {
	}
	public void run() {
	    LCD.drawString("mb", 1, 0);
	    TestThreads.mb.rotate(720);
	}
}

