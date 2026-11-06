/**
 * PURPOSE:
 * Simulates an Invoice Service that receives
 * customer orders from the Order Service and turns them into invoices.
 *
 * SECURITY CONTEXT:
 * This is the intentionally vulnerable implementation.
 * It deserialises incoming Java objects without validating
 * which classes are permitted.
 *
 * VULNERABILITY:
 * CWE-502 - Deserialisation of Untrusted Data.
 * Crafted serialised objects may trigger unexpected methods
 * during reconstruction, before the object type is checked.
 *
 * NOTE:
 * The incoming-order.ser file simulates an HTTP request body.
 * This code is for a controlled security demonstration only.
 */

import java.io.InputStream;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.io.IOException;

public class InvoiceService {

    /**
     * PURPOSE: Reconstructs an Order from an input stream.
    * INPUTS: A stream containing serialised Java data.
    * RETURNS: The reconstructed Order.
    * SECURITY: Intentionally deserialises untrusted objects without filtering.
    */
    public static Order readOrder(InputStream source)
            throws IOException, ClassNotFoundException {

        try (ObjectInputStream input = new ObjectInputStream(source)) {

            // VULNERABILITY: Java reconstructs the object before its
            // type is checked, potentially invoking unexpected methods.
            Object receivedObject = input.readObject();

            return (Order) receivedObject;
        }
    }

    /**
     * PURPOSE: Processes an incoming serialised order from a local file.
     */
    public static void main(String[] args) {

        try {
            Order order = readOrder(
                new FileInputStream("incoming-order.ser")
            );

            System.out.println("Order successfully received.");
            System.out.println(order);

        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Failed to process order: " + e.getMessage());

        } catch (ClassCastException e) {
            System.err.println("Received data is not a valid Order.");
        }
    }
}