
```
CT6042
├─ Cryptographic Failure
│  ├─ attack.py
│  ├─ invoice_system_mitigated.py
│  ├─ invoice_system_vulnerable.py
│  ├─ requirements.txt
│  └─ test_payment.py
├─ Deserialisation
│  ├─ Attacker
│  │  ├─ pom.xml
│  │  ├─ src
│  │  │  └─ main
│  │  │     └─ java
│  │  │        └─ AttackerReal.java
│  │  └─ target
│  │     ├─ classes
│  │     │  └─ AttackerReal.class
│  │     ├─ generated-sources
│  │     │  └─ annotations
│  │     ├─ maven-status
│  │     │  └─ maven-compiler-plugin
│  │     │     └─ compile
│  │     │        └─ default-compile
│  │     │           ├─ createdFiles.lst
│  │     │           ├─ dependencies.lst
│  │     │           └─ inputFiles.lst
│  │     └─ test-classes
│  └─ FinanceSystem
│     ├─ incoming-order.ser
│     ├─ invoices
│     │  └─ invoice-123.txt
│     ├─ pom.xml
│     ├─ src
│     │  ├─ main
│     │  │  └─ java
│     │  │     ├─ InvoiceService.java
│     │  │     ├─ Order.java
│     │  │     ├─ OrderService.java
│     │  │     └─ SafeInvoiceService.java
│     │  └─ test
│     │     └─ java
│     │        ├─ SafeDeserialisationTest.java
│     │        └─ VulnerableDeserialisationTest.java
│     └─ target
│        ├─ classes
│        │  ├─ InvoiceService.class
│        │  ├─ Order.class
│        │  ├─ OrderService.class
│        │  └─ SafeInvoiceService.class
│        ├─ generated-sources
│        │  └─ annotations
│        ├─ generated-test-sources
│        │  └─ test-annotations
│        ├─ maven-status
│        │  └─ maven-compiler-plugin
│        │     ├─ compile
│        │     │  └─ default-compile
│        │     │     ├─ createdFiles.lst
│        │     │     ├─ dependencies.lst
│        │     │     └─ inputFiles.lst
│        │     └─ testCompile
│        │        └─ default-testCompile
│        │           ├─ createdFiles.lst
│        │           ├─ dependencies.lst
│        │           └─ inputFiles.lst
│        ├─ surefire-reports
│        │  ├─ DeserialisationTest.txt
│        │  ├─ SafeDeserialisationTest.txt
│        │  ├─ TEST-DeserialisationTest.xml
│        │  ├─ TEST-SafeDeserialisationTest.xml
│        │  ├─ TEST-VulnerableDeserialisationTest.xml
│        │  └─ VulnerableDeserialisationTest.txt
│        └─ test-classes
│           ├─ SafeDeserialisationTest.class
│           └─ VulnerableDeserialisationTest.class
├─ Memory Safety
│  ├─ generate_label
│  ├─ generate_label.c
│  ├─ label_1002.txt
│  ├─ orders.csv
│  ├─ receive_order
│  ├─ receive_order.c
│  ├─ receive_order.plist
│  ├─ receive_order_asan
│  ├─ receive_order_safe
│  ├─ receive_order_safe.c
│  ├─ receive_order_safe.plist
│  ├─ test_dispatch.py
│  └─ tests
│     ├─ conftest.py
│     ├─ test_1_vulnerability.py
│     └─ test_2_mitigation.py
├─ SQL-Injection
│  ├─ app.py
│  ├─ database.py
│  ├─ orders.db
│  ├─ templates
│  │  ├─ index.html
│  │  └─ search_results.html
│  └─ tests
│     ├─ test_1_vulnerability.py
│     └─ test_2_mitigation.py
└─ Supply Chain
   ├─ approved_packages
   │  ├─ dispatch_label_generator-1.0.0-py3-none-any.whl
   │  └─ dispatch_label_generator-1.0.1-py3-none-any.whl
   ├─ evidence
   │  └─ sca_v1.0.1.txt
   ├─ order_system
   │  ├─ dispatch_labels
   │  │  ├─ 1.0.0-ORD-1001.txt
   │  │  └─ 1.0.1-ORD-1001.txt
   │  ├─ main.py
   │  └─ requirements-secure.txt
   ├─ packages
   │  ├─ dispatch-label-generator-v1.0.0
   │  │  ├─ build
   │  │  │  ├─ bdist.macosx-10.9-universal2
   │  │  │  └─ lib
   │  │  │     └─ dispatch_labels
   │  │  │        └─ __init__.py
   │  │  ├─ dispatch_label_generator.egg-info
   │  │  │  ├─ PKG-INFO
   │  │  │  ├─ SOURCES.txt
   │  │  │  ├─ dependency_links.txt
   │  │  │  └─ top_level.txt
   │  │  ├─ dispatch_labels
   │  │  │  └─ __init__.py
   │  │  ├─ dist
   │  │  │  └─ dispatch_label_generator-1.0.0-py3-none-any.whl
   │  │  └─ pyproject.toml
   │  └─ dispatch-label-generator-v1.0.1
   │     ├─ build
   │     │  ├─ bdist.macosx-10.9-universal2
   │     │  └─ lib
   │     │     └─ dispatch_labels
   │     │        └─ __init__.py
   │     ├─ dispatch_label_generator.egg-info
   │     │  ├─ PKG-INFO
   │     │  ├─ SOURCES.txt
   │     │  ├─ dependency_links.txt
   │     │  └─ top_level.txt
   │     ├─ dispatch_labels
   │     │  └─ __init__.py
   │     ├─ dist
   │     │  └─ dispatch_label_generator-1.0.1-py3-none-any.whl
   │     └─ pyproject.toml
   ├─ security_rules
   │  └─ dispatch_integrity.yml
   ├─ tampered_packages
   │  └─ dispatch_label_generator-1.0.0-py3-none-any.whl
   ├─ tests
   │  └─ test_dispatch_security.py
   └─ verify_update.py

```