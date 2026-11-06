/**
 * PURPOSE:
 * Simulates an Order Service that creates a customer order
 * and serialises it for transfer to the Warehouse Service.
 *
 * SECURITY CONTEXT:
 * Uses Java's native serialisation mechanism to convert an
 * Order object into binary data.
 *
 * NOTE:
 * A local .ser file simulates the HTTP request body.
 * No actual network communication takes place.
 */

import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.IOException;

public class OrderService {

    /**
     * PURPOSE: Creates a customer order and saves it as serialised data.
     * OUTPUT: An incoming-order.ser file containing the binary Order object.
     */
    public static void main(String[] args) {

        Order order = new Order(1234, "John Smith", 250.00);

        // STEP: Convert the Order object into binary data and save it.
        try (ObjectOutputStream output = new ObjectOutputStream(
                new FileOutputStream("incoming-order.ser"))) {

            output.writeObject(order);

            System.out.println("Order successfully serialised.");
            System.out.println(order);
            System.out.println("Saved to: incoming-order.ser");

        } catch (IOException e) {
            System.err.println("Failed to serialise order: " + e.getMessage());
        }
    }
}