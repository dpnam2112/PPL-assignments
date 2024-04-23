import java.io.*;
import java.io.IOException;

public class io {
    //private static final DataInputStream input = new DataInputStream(System.in);
    public static BufferedReader input = new BufferedReader(new InputStreamReader(System.in));
    public static Writer writer = new BufferedWriter(new OutputStreamWriter(System.out));
          
    /** return a floating-point value read from the standard input
     *	@return float the floating-point value
     */
    public static float readNumber()  {   
    	String tmp ="";
        try {
            tmp = input.readLine();
		      return Float.parseFloat(tmp);
	    } 
    	catch (IOException e) {
			e.printStackTrace();;
		}
        catch (NumberFormatException e) {
            e.printStackTrace();;
        }
        return 0.0F;
	}
	
    /** print out the value of the float f to the standard output
     *	@param f the floating-point value is printed out
     */
    public static void writeNumber(float f)  {
    	System.out.print(f+"");
    }
    
    /** reads and returns a boolean value from the standard input
     *	@return int a boolean value read from standard input
     */
    public static boolean readBool() {
    String tmp = "";
	    try {
	tmp = input.readLine();
		    if (tmp.equalsIgnoreCase("true"))
	    return true;
	else //if (tmp.equalsIgnoreCase("false"))
	    return false;
       // else throw new IllegalRuntimeException(tmp);
	    } catch (IOException e) {
		    e.printStackTrace();
	    }
	    return false;
    }

    /** print out the value of the boolean b to the standard output
     *	@param b the boolean value is printed out
     */
    public static void writeBool(boolean b)  {
    	System.out.print(b);
    }
    
    /** prints the value of the string to the standard output
     *	@param a the string is printed out
     */
     public static String readString() {
    	 String tmp ="";
        try {
            tmp = input.readLine();
            return tmp;
        } 
        catch (IOException e) {
            e.printStackTrace();;
        }
        catch (NumberFormatException e) {
            e.printStackTrace();;
        }
        return tmp;
    }
    
    /** same as putString except that it also prints a new line
     *	@param a the string is printed out
     */
    public static void writeString(String a)  {
    	System.out.print(a);
    }

    public static void close() {
    	try {
    		writer.close();
    	} catch (IOException e) {
		 e.printStackTrace();
	}
    }
}

