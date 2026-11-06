/*
 * PURPOSE:
 * Generates dispatch labels for orders authorised for shipment.
 *
 * SECURITY CONTEXT:
 * This process reads dispatch status from the stored order records.
 * It is shared by both vulnerable and mitigated demonstrations.
 */

#include <stdio.h>
#include <string.h>

/**
 * PURPOSE: Generates dispatch labels for orders marked ready to ship.
 * RETURNS: 0 on success, 1 if a file operation fails.
 * SECURITY: Only orders with ready_to_ship = Y are eligible.
 */
int generate_labels(void)
{
    FILE *database = fopen("orders.csv", "r");

    if (database == NULL) {
        perror("Could not open order database");
        return 1;
    }

    char line[512];
    int labels_created = 0;

    // STEP: Read each order from the order database.
    while (fgets(line, sizeof(line), database) != NULL) {

        char order_id[16];
        char customer_name[256];
        char ready_to_ship[2];

        // STEP: Extract the three fields from the CSV record.
        if (sscanf(line, "%15[^,],%255[^,],%1s",
                   order_id, customer_name, ready_to_ship) != 3) {
            printf("Skipping invalid order record.\n");
            continue;
        }

        // SECURITY: Only orders marked ready to ship can get a label.
        if (strcmp(ready_to_ship, "Y") != 0) {
            continue;
        }

        // SECURITY: Restrict order IDs to digits before using them in filenames.
        if (strspn(order_id, "0123456789") != strlen(order_id)) {
            printf("Skipping order with invalid ID.\n");
            continue;
        }

        char filename[64];
        snprintf(filename, sizeof(filename),
                 "label_%s.txt", order_id);

        // STEP: Avoid generating another label for the same order.
        FILE *existing = fopen(filename, "r");

        if (existing != NULL) {
            fclose(existing);
            continue;
        }

        FILE *label = fopen(filename, "w");

        if (label == NULL) {
            perror("Could not create dispatch label");
            fclose(database);
            return 1;
        }

        int written = fprintf(label,
                              "DISPATCH LABEL\n"
                              "Order ID: %s\n"
                              "Customer: %s\n",
                              order_id, customer_name);

        int closed = fclose(label);

        if (written < 0 || closed != 0) {
            perror("Could not save dispatch label");
            fclose(database);
            return 1;
        }

        printf("Created %s\n", filename);
        labels_created++;
    }

    if (ferror(database)) {
        perror("Could not read order database");
        fclose(database);
        return 1;
    }

    fclose(database);

    printf("Labels created: %d\n", labels_created);

    return 0;
}


/**
 * PURPOSE: Runs the scheduled dispatch label-generation process.
 * RETURNS: 0 on success, 1 on failure.
 */
int main(void)
{
    return generate_labels();
}
