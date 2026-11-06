
/*
 * PURPOSE:
 * Receives and stores customer orders in the fictional Dispatch System.
 * Creates dispatch labels for orders marked ready to ship.
 *
 * SECURITY CONTEXT:
 * This initial version checks input lengths before copying data into
 * fixed-size buffers. The vulnerability will be introduced later.
 */

#include <stdio.h>
#include <string.h>

typedef struct {
    char order_id[16];
    char customer_name[32];
    char ready_to_ship[2];
} Order;


/**
 * PURPOSE: Copies an incoming order field, removing surrounding spaces.
 * INPUTS: Destination buffer and source string.
 * SECURITY: Intentionally vulnerable because destination capacity
 * is not checked during copying.
 */
void copy_order_field(char *destination, const char *source)
{
    // STEP: Skip leading spaces.
    while (*source == ' ') {
        source++;
    }

    size_t i = 0;

    // VULNERABILITY: Copies characters without checking buffer capacity.
    while (source[i] != '\0') {
        destination[i] = source[i];
        i++;
    }

    // STEP: Remove trailing spaces.
    while (i > 0 && destination[i - 1] == ' ') {
        i--;
    }

    destination[i] = '\0';
}

/**
 * PURPOSE: Creates and stores a new order awaiting payment.
 * INPUTS: Order ID and customer name received from the Order System.
 * RETURNS: 0 on success, 1 if validation or file writing fails.
 */
int receive_order(const char *order_id, const char *customer_name)
{
    Order order = {0};

    // STEP: New orders must remain on hold until payment is confirmed.
    strcpy(order.ready_to_ship, "N");

    // SECURITY: Prevent commas and line breaks from corrupting CSV records.
    if (strpbrk(order_id, ",\r\n") != NULL ||
        strpbrk(customer_name, ",\r\n") != NULL) {
        printf("Error: Invalid characters in order details.\n");
        return 1;
    }

    // STEP: Copy incoming order details into the internal order structure.
    // VULNERABILITY: Both fields use the same unchecked copying function.
    copy_order_field(order.order_id, order_id);
    copy_order_field(order.customer_name, customer_name);

    // STEP: Append the order to our fictional orders database.
    FILE *file = fopen("orders.csv", "a");

    if (file == NULL) {
        perror("Could not open order database");
        return 1;
    }

    int written = fprintf(file, "%s,%s,%s\n",
                          order.order_id,
                          order.customer_name,
                          order.ready_to_ship);

    int closed = fclose(file);

    if (written < 0 || closed != 0) {
        perror("Could not save order");
        return 1;
    }

    printf("Order %s saved successfully.\n", order.order_id);
    printf("Ready to ship: %s\n", order.ready_to_ship);

    return 0;
}



/**
 * PURPOSE: Receives an order from command-line arguments.
 * RETURNS: 0 on success, 1 for invalid arguments.
 */
int main(int argc, char *argv[])
{
    if (argc != 3) {
        printf("Usage: ./receive_order <order_id> <customer_name>\n");
        return 1;
    }

    return receive_order(argv[1], argv[2]);
}


