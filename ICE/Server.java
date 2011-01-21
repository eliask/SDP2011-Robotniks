public class Server {
	public static void main(String[] args){
		int status = 0;
		Ice.Communicator ic = null;
		try{
			ic = Ice.Util.initialize(args);
			Ice.ObjectAdapter adapter = ic.createObjectAdapterWithEndpoints("SimpleCommanderAdapter", "default -p 10000");
			Ice.Object object = new CommanderI();
			adapter.add(object, ic.stringToIdentity("SimpleCommander"));
			adapter.activate();
			ic.waitForShutdown();
		}catch(Ice.LocalException e){
			e.printStackTrace();
			status = 1;
		}catch(Exception e){
			System.err.println(e.getMessage());
			status = 1;
		}
		if(ic != null){
			try{
				ic.destroy();
			}catch(Exception e){
				System.err.println(e.getMessage());
				status = 1;
			}
		}
		System.exit(status);
	}
}

