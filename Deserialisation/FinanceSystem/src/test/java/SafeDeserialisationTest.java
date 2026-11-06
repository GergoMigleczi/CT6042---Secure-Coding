
/**
 * PURPOSE:
 * Verifies that the mitigated Invoice Service securely processes
 * legitimate orders and rejects unexpected or invalid input.
 *
 * SECURITY CONTEXT:
 * Tests the effectiveness of the ObjectInputFilter mitigation
 * against CWE-502: Deserialisation of Untrusted Data.
 *
 * NOTE:
 * All test data remains in memory. No invoice files or
 * incoming-order.ser files are modified.
 */

import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;
import java.io.StreamCorruptedException;
import java.io.InvalidClassException;

import java.util.HashMap;
import java.util.Map;

import org.apache.commons.collections.FactoryUtils;
import org.apache.commons.collections.map.LazyMap;

import static org.junit.jupiter.api.Assertions.*;

public class SafeDeserialisationTest {

    /**
     * PURPOSE: Converts a Java object into serialised test data.
     * INPUTS: The object to serialise.
     * RETURNS: A byte array containing the serialised object.
     */
    private byte[] serialise(Object object) throws IOException {

        ByteArrayOutputStream bytes = new ByteArrayOutputStream();

        try (ObjectOutputStream output = new ObjectOutputStream(bytes)) {
            output.writeObject(object);
        }

        return bytes.toByteArray();
    }

    /**
     * PURPOSE: Confirms the security filter permits legitimate orders.
     */
    @Test
    void safeServiceAcceptsValidOrder() throws Exception {

        Order order = new Order(1234, "John Smith", 250.00);
        byte[] data = serialise(order);

        Order result = SafeInvoiceService.readOrder(
            new ByteArrayInputStream(data)
        );

        // TEST: Verify that the mitigation preserves intended functionality.
        assertEquals(order.toString(), result.toString());
    }

    /**
     * PURPOSE: Confirms the filter rejects unexpected Java classes.
     *
     * SECURITY: Rejection must occur during deserialisation rather
     * than after object reconstruction.
     */
    @Test
    void safeServiceRejectsUnexpectedObject() throws Exception {

        Map unexpectedObject = LazyMap.decorate(
            new HashMap(),
            FactoryUtils.constantFactory("Test value")
        );

        byte[] data = serialise(unexpectedObject);

        // TEST: Verify that the ObjectInputFilter rejects the object.
        IOException exception = assertThrows(
            IOException.class,
            () -> SafeInvoiceService.readOrder(
                new ByteArrayInputStream(data)
            )
        );

        assertTrue(exception.getMessage().contains("REJECTED"));
    }

    /**
     * PURPOSE: Confirms malformed serialised data is rejected.
     */
    @Test
    void safeServiceRejectsMalformedData() {

        byte[] invalidData = "Not a serialised object".getBytes();

        // TEST: Verify that malformed input produces a controlled exception.
        assertThrows(
            StreamCorruptedException.class,
            () -> SafeInvoiceService.readOrder(
                new ByteArrayInputStream(invalidData)
            )
        );
    }

    /**
     * PURPOSE: Verifies the maximum permitted array length.
     *
     * SECURITY CONTEXT:
     * Tests the maxarray=100 restriction configured in the
     * secure deserialisation filter.
     */
    @Test
    void safeServiceRejectsOversizedArray() throws Exception {

        // TEST: Create an array exceeding the configured limit.
        Order[] orders = new Order[101];

        byte[] data = serialise(orders);

        // TEST: Verify that the resource restriction rejects the array.
        InvalidClassException exception = assertThrows(
            InvalidClassException.class,
            () -> SafeInvoiceService.readOrder(
                new ByteArrayInputStream(data)
            )
        );

        assertTrue(exception.getMessage().contains("REJECTED"));
    }
}
