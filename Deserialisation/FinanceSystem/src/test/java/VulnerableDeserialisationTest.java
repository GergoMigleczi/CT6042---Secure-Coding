
/**
 * PURPOSE:
 * Tests the vulnerable Invoice Service using legitimate and
 * unexpected serialised Java objects.
 *
 * SECURITY CONTEXT:
 * Demonstrates CWE-502: Deserialisation of Untrusted Data.
 * The tests establish that the service accepts legitimate orders
 * but reconstructs unexpected objects before validating their type.
 *
 * NOTE:
 * Test data remains in memory. No invoice files are modified.
 */

import org.junit.jupiter.api.Test;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.ObjectOutputStream;

import java.util.HashMap;
import java.util.Map;

import org.apache.commons.collections.FactoryUtils;
import org.apache.commons.collections.map.LazyMap;

import static org.junit.jupiter.api.Assertions.*;

public class VulnerableDeserialisationTest {

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
     * PURPOSE: Confirms the vulnerable service processes legitimate orders.
     */
    @Test
    void vulnerableServiceAcceptsValidOrder() throws Exception {

        Order order = new Order(1234, "John Smith", 250.00);
        byte[] data = serialise(order);

        Order result = InvoiceService.readOrder(
            new ByteArrayInputStream(data)
        );

        // TEST: Confirm that legitimate orders remain functional.
        assertEquals(order.toString(), result.toString());
    }

    /**
     * PURPOSE: Demonstrates that the vulnerable service reconstructs
     * an unexpected object before checking its type.
     *
     * SECURITY: The expected ClassCastException occurs after
     * unrestricted deserialisation.
     */
    @Test
    void vulnerableServiceDeserialisesUnexpectedObject() throws Exception {

        Map unexpectedObject = LazyMap.decorate(
            new HashMap(),
            FactoryUtils.constantFactory("Test value")
        );

        byte[] data = serialise(unexpectedObject);

        // TEST: Verify that object reconstruction is followed by
        // a failed type cast rather than an input-filter rejection.
        assertThrows(
            ClassCastException.class,
            () -> InvoiceService.readOrder(
                new ByteArrayInputStream(data)
            )
        );
    }
}
