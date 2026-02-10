
import json
import pathlib
import datetime
import os

class AuditLogger:
    def __init__(self, log_filepath: str = 'logs/audit_trail.log'):
        self.log_filepath = pathlib.Path(log_filepath)
        # Ensure the directory for the log file exists
        self.log_filepath.parent.mkdir(parents=True, exist_ok=True)
        print(f"AuditLogger initialized, logging to: {self.log_filepath}")

    def log_event(self, event_type: str, raw_data: dict, semantic_labels: dict):
        """
        Logs an event, converting transient system noise into semantic labels,
        and writes it as a JSON line to the audit trail.

        Args:
            event_type (str): The type of event (e.g., 'SYSTEM_NOISE', 'SECURITY_ALERT').
            raw_data (dict): Raw event data (e.g., {'port': 22, 'ip': '192.168.1.1'}).
            semantic_labels (dict): Pre-defined semantic labels for raw_data elements.
                                   (e.g., {'port': 'SECURE_TRANSIT_INTERFACE'}).
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # Apply semantic mappings
        processed_data = raw_data.copy()
        transformed_labels = {}
        for key, value in raw_data.items():
            if key in semantic_labels:
                transformed_labels[key] = semantic_labels[key]
            # Example of dynamic semantic mapping based on value
            if key == 'port' and value == 22:
                transformed_labels['port_designation'] = 'SSH_CONTROL_PORT'
            elif key == 'port' and value == 80:
                transformed_labels['port_designation'] = 'HTTP_ACCESS_PORT'
            elif key == 'ip' and value.startswith('192.168.'):
                transformed_labels['ip_type'] = 'INTERNAL_NETWORK_ADDRESS'

        log_entry = {
            'timestamp': timestamp,
            'event_type': event_type,
            'raw_data': raw_data,
            'semantic_labels': transformed_labels,
            'metadata': {
                'source_module': 'AuditLogger',
                'log_version': '1.0'
            }
        }

        with open(self.log_filepath, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        print(f"Logged event '{event_type}' to {self.log_filepath.name}.")

if __name__ == '__main__':
    # Setup for testing
    test_log_file = pathlib.Path('logs/test_audit_trail.log')
    if test_log_file.exists():
        os.remove(test_log_file)

    logger = AuditLogger(log_filepath=str(test_log_file))

    # --- Test Case 1: System Noise with Port ID ---
    print("\n--- Test Case 1: System Noise with Port ID ---")
    raw_event_1 = {'component': 'firewall', 'message': 'Port 22 traffic detected', 'port': 22, 'source_ip': '10.0.0.5'}
    semantic_map_1 = {'port': 'SECURE_TRANSIT_INTERFACE'}
    logger.log_event('SYSTEM_NOISE', raw_event_1, semantic_map_1)

    # Verify log entry
    with open(test_log_file, 'r') as f:
        line = f.readline()
        entry = json.loads(line)
        assert entry['event_type'] == 'SYSTEM_NOISE', "Test 1 Failed: Event type mismatch."
        assert entry['raw_data'] == raw_event_1, "Test 1 Failed: Raw data mismatch."
        assert entry['semantic_labels']['port'] == 'SECURE_TRANSIT_INTERFACE', "Test 1 Failed: Semantic label port mismatch."
        assert entry['semantic_labels']['port_designation'] == 'SSH_CONTROL_PORT', "Test 1 Failed: Dynamic semantic label mismatch."
    print("Test Case 1 Passed.")

    # --- Test Case 2: Security Alert with IP ---
    print("\n--- Test Case 2: Security Alert with IP ---")
    raw_event_2 = {'alert_id': 'SEC-001', 'severity': 'HIGH', 'ip': '192.168.1.100', 'action': 'BLOCK'}
    semantic_map_2 = {'ip': 'OBSERVED_IP_ADDRESS'}
    logger.log_event('SECURITY_ALERT', raw_event_2, semantic_map_2)

    # Verify second log entry
    with open(test_log_file, 'r') as f:
        f.readline() # Skip first line
        line = f.readline()
        entry = json.loads(line)
        assert entry['event_type'] == 'SECURITY_ALERT', "Test 2 Failed: Event type mismatch."
        assert entry['semantic_labels']['ip_type'] == 'INTERNAL_NETWORK_ADDRESS', "Test 2 Failed: Dynamic IP type mismatch."
    print("Test Case 2 Passed.")

    # --- Test Case 3: Operational Event with HTTP Port ---
    print("\n--- Test Case 3: Operational Event with HTTP Port ---")
    raw_event_3 = {'service': 'webserver', 'status': '200 OK', 'port': 80}
    semantic_map_3 = {'port': 'SERVICE_ENDPOINT_PORT'}
    logger.log_event('OPERATIONAL_EVENT', raw_event_3, semantic_map_3)

    # Verify third log entry
    with open(test_log_file, 'r') as f:
        f.readline(); f.readline() # Skip first two lines
        line = f.readline()
        entry = json.loads(line)
        assert entry['event_type'] == 'OPERATIONAL_EVENT', "Test 3 Failed: Event type mismatch."
        assert entry['semantic_labels']['port_designation'] == 'HTTP_ACCESS_PORT', "Test 3 Failed: Dynamic HTTP port mismatch."
    print("Test Case 3 Passed.")

    print("\nAll AuditLogger tests completed successfully!")

    # Clean up the test log file
    os.remove(test_log_file)
