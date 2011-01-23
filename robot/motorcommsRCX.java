            import josx.platform.rcx.*;

            //////////////////////////////////////
            /**
            * Represents a simple sample application.
            *
            * @author The leJOS Tutorial
            * @version 1.0 
            */
            public class motorcommsRCX {        

                ////////////////////////////////////////////
                // public methods
                ////////////////////////////////////////////

                ////////////////////////////////////////////
                /**
                 * main method 
                 * @throws InterruptedException
                 */
                public static void main(String[] args) 
                    throws InterruptedException {

                    // message
                    TextLCD.print("DRIVE");

                    // drive forward
		    Motor.A.setPower(7);
		    Motor.C.setPower(7);

		    Sensor.S1.setTypeAndMode(3,0x80);
		    Sensor.S2.setTypeAndMode(1,0x40);
		    
		    int calibvalue = 81;
		    int loopctl = 1;
		    boolean flag1 = false;
		    while (loopctl > 0){
			LCD.showNumber(Sensor.S1.readValue());
			if(Sensor.S1.readValue() < calibvalue){
			    Motor.A.stop();
			    Motor.C.stop();
			    if (flag1 == true){
				flag1 = false;
			    }
			} else if (Sensor.S1.readValue() >= calibvalue){
			    if (flag1 == false){
				Motor.A.forward();
				Motor.C.forward();
				flag1 = true;
			    }
			}
			
			if(Sensor.S2.readBooleanValue()){
			    calibvalue = Sensor.S1.readValue();
			}
		    }		  

                    // just run until RUN button is pressed again
                    Button.RUN.waitForPressAndRelease();

                } // main()

            } // class SimpleSample
