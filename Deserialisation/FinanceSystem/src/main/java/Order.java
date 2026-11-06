/**
 * PURPOSE:
 * Represents a customer order that can be transferred between
 * the Order Service and Warehouse Service.
 *
 * SECURITY CONTEXT:
 * Implements Java's native serialisation mechanism.
 * This class is not vulnerable itself, but its objects will be
 * used to demonstrate the risks of unsafe deserialisation.
 */

import java.io.Serializable;

public class Order implements Serializable {

    // SECURITY: Identifies the serialised class version for compatibility.
    // This does not provide authentication or protect against malicious data.
    private static final long serialVersionUID = 1L;

    private int orderId;
    private String customerName;
    private double total;

    /**
     * PURPOSE: Creates a new customer order.
     * INPUTS: Order ID, customer name and total order value.
     */
    public Order(int orderId, String customerName, double total) {
        this.orderId = orderId;
        this.customerName = customerName;
        this.total = total;
    }

    /**
     * PURPOSE: Returns a readable summary of the order.
     * RETURNS: A string containing the order details.
     */
    @Override
    public String toString() {
        return "Order ID: " + orderId +
               ", Customer: " + customerName +
               ", Total: £" + total;
    }
}