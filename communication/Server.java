import java.io.*;
import java.net.*;

public class Server {

    public static void main(String[] args){
        boolean loopback = false;
        if (args.length > 0)
            loopback = true;

        PCBluetooth pcb = new PCBluetooth();
        if (!loopback)
            pcb.openConnection();
        try{
            ServerSocket ss = new ServerSocket(6879);
            while(true){
                Socket socket = ss.accept();
                try{
                    InputStream is = socket.getInputStream();
                    String num = "";
                    int i;
                    char c;
                    while((i = is.read()) != -1){
                        c = (char) i;
                        if (c == '\n') {
                            int z = Integer.parseInt(num);
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
	try{
		pcb.closeConnection();
	}catch(IOException e){
		System.err.println("Could not close connection to robot.");
	}
    }

}
