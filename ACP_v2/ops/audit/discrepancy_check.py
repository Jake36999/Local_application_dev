import json
import pathlib
import hashlib
from typing import Dict, Any

class DiscrepancyChecker:
    def __init__(self):
        pass

    def _build_lookup(self, manifest_data: list) -> dict:
        """
        Builds a lookup dictionary from a manifest for efficient comparison.
        Keys: relative_path, Values: entire file entry.
        """
        lookup = {}
        for entry in manifest_data:
            if 'relative_path' in entry:
                lookup[entry['relative_path']] = entry
            elif 'path' in entry: # Handle a simpler agent interpretation format
                lookup[entry['path']] = entry
        return lookup

    def perform_diff(
        self,
        ground_truth_manifest: list[dict],
        agent_interpretation: list[dict]
    ) -> Dict[str, Any]:
        """
        Performs a 'High-Fidelity Diff' between static ground truth and agent interpretation.
        Identifies missing files, extra files (hallucinations), and content mismatches.

        ground_truth_manifest: A list of dicts from the manifest.jsonl (e.g., from output/manifest.py).
        agent_interpretation: A list of dicts representing the agent's view. Expected to have
                              'path' and optionally 'content_hash' (SHA-256) or other properties.
        """
        discrepancies: Dict[str, Any] = {}

        gt_lookup = self._build_lookup(ground_truth_manifest)
        agent_lookup = self._build_lookup(agent_interpretation)

        # Check for files missing in agent's interpretation
        for gt_path, gt_entry in gt_lookup.items():
            if gt_path not in agent_lookup:
                discrepancies['missing_in_agent'].append(gt_path)

        # Check for hallucinations and content mismatches
        for agent_path, agent_entry in agent_lookup.items():
            if agent_path not in gt_lookup:
                discrepancies['hallucinations'].append(agent_path)
            else:
                # Compare content hashes if available in both
                gt_hashes = gt_lookup[agent_path].get('hashes', {})
                agent_hash = agent_entry.get('content_hash') # Assuming SHA-256 for agent

                if agent_hash and gt_hashes.get('sha256') and agent_hash != gt_hashes['sha256']:
                    discrepancies['content_mismatches'].append({
                        'path': agent_path,
                        'ground_truth_sha256': gt_hashes['sha256'],
                        'agent_sha256': agent_hash
                    })
                # Add more sophisticated content checks here if needed, e.g., AST diffs, regex checks

        return discrepancies


if __name__ == '__main__':
    checker = DiscrepancyChecker()

    # Helper to create a dummy manifest entry
    def create_gt_entry(rel_path, content):
        encoded_content = content.encode('utf-8')
        return {
            'relative_path': rel_path,
            'absolute_path': str(pathlib.Path('./dummy_root') / rel_path),
            'hashes': {
                'md5': hashlib.md5(encoded_content).hexdigest(),
                'sha256': hashlib.sha256(encoded_content).hexdigest()
            }
        }

    # Helper to create a dummy agent interpretation entry
    def create_agent_entry(path, content=None):
        entry = {'path': path}
        if content is not None:
            entry['content_hash'] = hashlib.sha256(content.encode('utf-8')).hexdigest()
        return entry

    # --- Dummy Data for Testing ---

    # Ground Truth Manifest
    gt_manifest_data = [
        create_gt_entry('src/main.py', 'print("Hello, World!")'),
        create_gt_entry('src/utils.py', 'def helper(): return True'),
        create_gt_entry('config.yaml', 'version: 1.0')
    ]

    # Agent Interpretation Scenarios

    # Scenario 1: Perfect Match
    print("\n--- Scenario 1: Perfect Match ---")
    agent_interpretation_1 = [
        create_agent_entry('src/main.py', 'print("Hello, World!")'),
        create_agent_entry('src/utils.py', 'def helper(): return True'),
        create_agent_entry('config.yaml', 'version: 1.0')
    ]
    discrepancies_1 = checker.perform_diff(gt_manifest_data, agent_interpretation_1)
    print("Discrepancies:", discrepancies_1)
    assert not any(discrepancies_1.values()), "Scenario 1 Failed: Expected no discrepancies!"
    print("Scenario 1 Passed.")

    # Scenario 2: Missing file in agent, and a hallucination by agent
    print("\n--- Scenario 2: Missing file and Hallucination ---")
    agent_interpretation_2 = [
        create_agent_entry('src/main.py', 'print("Hello, World!")'),
        create_agent_entry('agent_generated.log', 'Some logs here') # Hallucination
    ]
    discrepancies_2 = checker.perform_diff(gt_manifest_data, agent_interpretation_2)
    print("Discrepancies:", discrepancies_2)
    assert 'src/utils.py' in discrepancies_2['missing_in_agent'], "Scenario 2 Failed: Missing 'src/utils.py' not detected!"
    assert 'config.yaml' in discrepancies_2['missing_in_agent'], "Scenario 2 Failed: Missing 'config.yaml' not detected!"
    assert 'agent_generated.log' in discrepancies_2['hallucinations'], "Scenario 2 Failed: Hallucination not detected!"
    assert not discrepancies_2['content_mismatches'], "Scenario 2 Failed: Unexpected content mismatches!"
    print("Scenario 2 Passed.")

    # Scenario 3: Content mismatch
    print("\n--- Scenario 3: Content Mismatch ---")
    agent_interpretation_3 = [
        create_agent_entry('src/main.py', 'print("Hello, World!")'),
        create_agent_entry('src/utils.py', 'def helper(): return False') # Mismatched content
    ]
    discrepancies_3 = checker.perform_diff(gt_manifest_data, agent_interpretation_3)
    print("Discrepancies:", discrepancies_3)
    assert 'config.yaml' in discrepancies_3['missing_in_agent'], "Scenario 3 Failed: Missing 'config.yaml' not detected!"
    assert len(discrepancies_3['content_mismatches']) == 1, "Scenario 3 Failed: Expected one content mismatch!"
    assert discrepancies_3['content_mismatches'][0]['path'] == 'src/utils.py', "Scenario 3 Failed: Mismatch path incorrect!"
    assert not discrepancies_3['hallucinations'], "Scenario 3 Failed: Unexpected hallucinations!"
    print("Scenario 3 Passed.")

    # Scenario 4: Agent omits content hash for a common file
    print("\n--- Scenario 4: Agent omits content hash ---")
    agent_interpretation_4 = [
        create_agent_entry('src/main.py'), # No content hash provided by agent
        create_agent_entry('src/utils.py', 'def helper(): return True'),
        create_agent_entry('config.yaml', 'version: 1.0')
    ]
    discrepancies_4 = checker.perform_diff(gt_manifest_data, agent_interpretation_4)
    print("Discrepancies:", discrepancies_4)
    assert not any(discrepancies_4.values()), "Scenario 4 Failed: Expected no discrepancies despite omitted hash if agent matches otherwise!"
    print("Scenario 4 Passed.")

    print("\nAll DiscrepancyChecker tests completed successfully!")
