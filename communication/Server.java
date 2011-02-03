import java.io.*;
import java.net.*;
import java.util.concurrent.*;
import java.util.ArrayList;

/* Send command -1 to cleanly shutdown server, closing bluetooth connection */

public class Server {

	protected boolean loopback = false;
	private PCBluetooth pcb = null;
	private int port = 6879;
	private ServerSocket ss = null;
	private boolean finished = false;
	private ArrayList<Socket> sockets = new ArrayList<Socket>();
	private ExecutorService executor = null;
	private boolean commandSent = false;

	public static void main(String[] args){
		Server server = new Server();
		if (args.length > 0){
			server.loopback = true;
		}
		server.startServer();
	}

	public void startServer(){
		pcb = new PCBluetooth();
		if (!loopback)
			pcb.openConnection();

		try{
			ss = new ServerSocket(port);
			if (loopback)
				System.out.println("=== Loopback mode ===");

			System.out.println( "Server started on port " +
								port + ", waiting for connection." );
			serverLoop();

		}catch(IOException e){
			System.err.println("Could not open ServerSocket, or was interrupted.");
		}

		if(loopback){
			System.out.println("Exiting safely in loopback mode.");
			return;
		}

		try{
			pcb.closeConnection();
			System.out.println("Connection to robot closed.");
		}catch(IOException e){
			System.err.println("Could not close connection to robot.");
		}
	}

	public synchronized void sendMessage(int message){
		commandSent = true;
		if (loopback)
			return;

		try{
			pcb.sendMessage(message);
		}catch(IOException e){
			// Usually this happens when the connection dies.
			// Should we try to reconnect?
			System.err.println("failed to send message. ignoring...");
		}
	}

	public void serverLoop() throws IOException{
		executor = Executors.newCachedThreadPool();
		executor.execute(new ConnectionListener());
		executor.execute(new KeepAlive());

		while(!finished){
			try{
				Thread.sleep(250);
			}catch(InterruptedException e){
				// don't care
			}
		}

		ss.close();
		for(Socket s: sockets){
			s.close();
		}
		executor.shutdownNow();
	}

	class KeepAlive implements Runnable {

		public void run(){
			while(!finished){
				commandSent = false;
				try{
					Thread.sleep(5000);
				}catch(InterruptedException e){
					// nobody cares
				}
				if(!commandSent){
					sendMessage(0);
				}
			}
		}
	}

	class ConnectionListener implements Runnable{
		public void run(){
			try{
				while(true){
					Socket socket = ss.accept();
					sockets.add(socket);
					executor.execute(new ConnectionHandler(socket));
				}
			}catch(IOException e){
				finished = true;
				System.err.println("ServerSocket IO error");
			}
		}
	}

	class ConnectionHandler implements Runnable {

		private Socket socket = null;

		ConnectionHandler(Socket socket){
			this.socket = socket;
		}

		public void run(){
			try{
				System.out.println( "New connection from: " +
									socket.getInetAddress().toString() );
				InputStream is = socket.getInputStream();
				String num = "";
				int i;
				char c;
				while((i = is.read()) != -1){
					c = (char) i;
					if (c == '\n') {
						int z = Integer.parseInt(num);
						if(z == -1){
							finished = true;
							break;
						}
						sendMessage(z);
						System.out.println(socket.getInetAddress().toString()
										   + ":  " + z);
						num = "";
					} else { // c != '\n'
						num += new Character(c).toString();
					}
				}
				is.close();
				socket.close();
				System.out.println( "Connection closed: " +
									socket.getInetAddress().toString() );
			}catch(IOException e){
				System.err.println( "Lost connection to client: " +
									socket.getInetAddress().toString() );
			}
		}
	}

}
