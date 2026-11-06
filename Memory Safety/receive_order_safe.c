
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
#include <ctype.h>

typedef struct {
    char order_id[16];
    char customer_name[32];
    char ready_to_ship[2];
} Order;


/**
 * PURPOSE: Removes leading and trailing whitespace from a string.
 * INPUTS: A modifiable, null-terminated string.
 * RETURNS: The same string with leading and trailing whitespace removed.
 */
char *remove_whitespace(char *str)
{
    char *start = str;
    char *end;

    // STEP: Find the first non-whitespace character.
    while (isspace((unsigned char)*start))
    {
        start++;
    }

    // STEP: Shift the remaining string to the beginning.
    memmove(str, start, strlen(start) + 1);

    // STEP: Remove trailing whitespace.
    end = str + strlen(str);

    while (end > str && isspace((unsigned char)*(end - 1)))
    {
        end--;
    }

    *end = '\0';

    return str;
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

    // STEP: Remove whitespace from the order ID and customer name.
    remove_whitespace((char *)order_id);
    remove_whitespace((char *)customer_name);
    
    // MITIGATION: Check that each value fits, including its null terminator.
    if (strlen(order_id) >= sizeof(order.order_id) ||
        strlen(customer_name) >= sizeof(order.customer_name)) {
        printf("Error: Order ID or customer name is too long.\n");
        return 1;
    }

    // SECURITY: Prevent commas and line breaks from corrupting CSV records.
    if (strpbrk(order_id, ",\r\n") != NULL ||
        strpbrk(customer_name, ",\r\n") != NULL) {
        printf("Error: Invalid characters in order details.\n");
        return 1;
    }

    strcpy(order.order_id, order_id);
    strcpy(order.customer_name, customer_name);

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


