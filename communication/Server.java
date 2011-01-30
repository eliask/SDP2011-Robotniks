import java.io.*;
import java.net.*;

/* Send command -1 to cleanly shutdown server, closing bluetooth connection */

public class Server {

    public static void main(String[] args){
	int port = 6879;
        boolean loopback = false;
        if (args.length > 0)
            loopback = true;

        PCBluetooth pcb = new PCBluetooth();
        if (!loopback)
            pcb.openConnection();
        try{
            ServerSocket ss = new ServerSocket(port);
	    System.out.println("Server started on port " + port + ", waiting for connection.");
serverloop:
            while(true){
                Socket socket = ss.accept();
                try{
		    System.out.println("Connection opened from " + socket.getInetAddress().toString());
                    InputStream is = socket.getInputStream();
                    String num = "";
                    int i;
                    char c;
                    while((i = is.read()) != -1){
                        c = (char) i;
                        if (c == '\n') {
                            int z = Integer.parseInt(num);
			    if(z == -1){
				break serverloop;
			    }
                            if (!loopback){
                                try{
                                    pcb.sendMessage(z);
                                }catch(IOException e){
                                    System.err.println("failed to send message. ignoring...");
                                }
                            }
                            // Make the output align with PCBluetooth
                            System.out.println("Server:      " + z);
                            num = "";
                        } else {
                            num += new Character(c).toString();
                        }
                    }
                    is.close();
                }catch(IOException e){
                    System.err.println("Client connection lost... waiting for new connection.");
                }

            }
        }catch(IOException e){
            System.err.println("Could not open ServerSocket, or was interrupted.");
        }
	if(!loopback){
		try{
			pcb.closeConnection();
			System.out.println("Connection to robot closed.");
		}catch(IOException e){
			System.err.println("Could not close connection to robot.");
		}
	}
    }

}
