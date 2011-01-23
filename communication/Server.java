import java.io.*;
import java.net.*;

public class Server {

	public static void main(String[] args){
		PCBluetooth pcb = new PCBluetooth();
		pcb.openConnection();
		try{
			ServerSocket ss = new ServerSocket(6879);
			while(true){
				Socket s = ss.accept();
				InputStream is = s.getInputStream();
				int x;
				char z;
				while((x = is.read()) != -1){
					z = (char) x;
					System.out.println(z);
					pcb.sendMessage(Integer.parseInt(new String(z)));
				}
				is.close();
			}
		}catch(IOException e){
			System.err.println("random io error");
		}catch(Exception e){
			System.err.println("something went wrong");
		}
	}

}
