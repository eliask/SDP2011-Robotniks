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
                InputStream is = socket.getInputStream();
                String num = "";
                int i;
                char c;
                while((i = is.read()) != -1){
                    c = (char) i;
                    if (c == '\n') {
                        int z = Integer.parseInt(num);
                        if (!loopback)
                            pcb.sendMessage(z);
                        System.out.println(z);
                        num = "";
                    } else {
                        num += new Character(c).toString();
                    }
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