
/**
 * PURPOSE:
 * Simulates an Invoice Service that receives
 * customer orders from the Order Service and turns them into invoices.
 *
 * SECURITY CONTEXT:
 * Mitigates CWE-502: Deserialisation of Untrusted Data.
 * Uses an ObjectInputFilter to restrict which Java classes can
 * be reconstructed from incoming serialised data.
 *
 * MITIGATION:
 * Only Order objects are permitted. Unexpected classes are
 * rejected during deserialisation, before their object state
 * can be fully reconstructed.
 *
 * NOTE:
 * This demonstrates class filtering as a security control.
 * Production systems should also authenticate incoming messages
 * and validate the contents of accepted orders.
 */

import java.io.InputStream;
import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.io.ObjectInputFilter;
import java.io.IOException;

public class SafeInvoiceService {

    /**
     * PURPOSE: Reconstructs an Order using restricted deserialisation.
     * INPUTS: A stream containing serialised Java data.
     * RETURNS: The validated Order object.
     * SECURITY: Applies class filtering before reconstructing objects.
     */
    public static Order readOrder(InputStream source)
            throws IOException, ClassNotFoundException {

        try (ObjectInputStream input = new ObjectInputStream(source)) {

            // MITIGATION: Restrict accepted classes and object graph size.
            ObjectInputFilter filter = ObjectInputFilter.Config.createFilter(
                "maxdepth=10;maxrefs=100;maxbytes=65536;maxarray=100;Order;!*"
            );

            input.setObjectInputFilter(filter);

            Object receivedObject = input.readObject();

            // SECURITY: Verify the returned object has the expected type.
            if (!(receivedObject instanceof Order)) {
                throw new IOException("Received object is not an Order.");
            }

            return (Order) receivedObject;
        }
    }

    /**
     * PURPOSE: Processes an incoming order using the secure implementation.
     */
    public static void main(String[] args) {

        try {
            Order order = readOrder(
                new FileInputStream("incoming-order.ser")
            );

            System.out.println("Order successfully received.");
            System.out.println(order);

        } catch (IOException | ClassNotFoundException e) {
            System.err.println("Order rejected: " + e.getMessage());
        }
    }
}
