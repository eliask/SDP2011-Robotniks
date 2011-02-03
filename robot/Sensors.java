// Prints and sends sensor data
// Add to MainCtr when needed

public static void sensors(){
	// Define sensor ports
	public static final SensorPort frontTouch = SensorPort.S2;
	public static final SensorPort leftTouch = SensorPort.S3;
	public static final SensorPort rightTouch = SensorPort.S4;

	// Set sensor ports to touch
	TouchSensor front = new TouchSensor(frontTouch);
	TouchSensor left = new TouchSensor(leftTouch);
	TouchSensor right = new TouchSensor(rightTouch);

	// Screen messages
	String fsensorstate;
	String lsensorstate;
	String rsensorstate;

	// Back message - made up of primes
	// Mod on other side to check which sensors are on
	int fsensorMessage;
	int lsensorMessage;
	int rsensorMessage;

	if(front.isPressed()){
		fsensorstate = "PRESSED";
		fsensorMessage = 2;
	} else {
		fsensorstate = "FINE";
		fsensorMessage = 1;
	}
	writeToScreen("Front Sensor:" + fsensorstate, 4);

	if(left.isPressed()){
		lsensorstate = "PRESSED";
		lsensorMessage = 3;
	} else {
		lsensorstate = "FINE";
		lsensorMessage = 1;
	}
	writeToScreen("Left Sensor" + lsensorstate, 5);

	if(right.isPressed()){
		rsensorstate = "PRESSED";
		lsensorMessage = 5;
	} else {
		rsensorstate = "FINE";
		lsensorMessage = 1;
	}
	writeToScreen("Right Sensor" + rsensorstate, 6);
	sendBackMessage(fsensorMessage*lsensorMessage*rsensorMessage);
}

public static void sendBackMessage(int messageBack) throws InterruptedException, IOException{
	outputStream.writeInt(messageBack);
	outputStream.flush();
}
