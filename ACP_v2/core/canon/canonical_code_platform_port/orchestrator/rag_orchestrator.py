"""
RAG Integration Orchestrator Command

Handles:
1. Triggering RAG indexing when files are ingested
2. Performing semantic analysis on components
3. Generating recommendations
4. Publishing RAG-augmented analysis events
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from bus.message_bus import MessageBus  # type: ignore
from bus.settings_db import SettingsDB  # type: ignore
from rag_engine import get_rag_analyzer, RAGVectorDB  # type: ignore

logger = logging.getLogger(__name__)


class RAGOrchestrator:
    """Orchestrates RAG workflows."""

    def __init__(self):
        """Initialize RAG orchestrator."""
        self.bus = MessageBus()
        self.settings = SettingsDB()
        self.analyzer = get_rag_analyzer()
        self.logger = logging.getLogger(__name__)

    def is_rag_enabled(self) -> bool:
        """Check if RAG is enabled in settings."""
        return self.settings.is_feature_enabled('rag_integration_enabled')

    def trigger_indexing(self, file_id: str, repo_path: str) -> bool:
        """Trigger RAG indexing for an ingested file."""
        if not self.is_rag_enabled():
            self.logger.info("RAG is disabled, skipping indexing")
            return False

        try:
            # Build/update index
            indexed_count = self.analyzer.build_index_from_canon_db()

            # Publish event
            self.bus.publish_event(
                event_type='rag_indexing_completed',
                source='rag_orchestrator',
                payload={
                    'file_id': file_id,
                    'repo_path': repo_path,
                    'components_indexed': indexed_count,
                    'timestamp': datetime.now().isoformat(),
                }
            )

            self.logger.info(f"RAG indexing completed: {indexed_count} components")
            return True

        except Exception as e:
            self.logger.error(f"RAG indexing failed: {e}")
            self.bus.publish_event(
                event_type='rag_indexing_failed',
                source='rag_orchestrator',
                payload={'error': str(e)}
            )
            return False

    def analyze_component(self, component_id: str) -> Dict:
        """Perform semantic analysis on a component."""
        if not self.is_rag_enabled():
            return {}

        try:
            analysis = self.analyzer.analyze_with_context(component_id)

            # Get recommendations
            recommendations = self.analyzer.get_semantic_recommendations(component_id)

            analysis['recommendations'] = recommendations

            # Publish analysis event
            self.bus.publish_event(
                event_type='rag_component_analysis',
                source='rag_orchestrator',
                payload={
                    'component_id': component_id,
                    'analysis': analysis,
                    'timestamp': datetime.now().isoformat(),
                }
            )

            return analysis

        except Exception as e:
            self.logger.error(f"Component analysis failed: {e}")
            return {}

    def search_components(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for components using semantic search."""
        if not self.is_rag_enabled():
            return []

        try:
            results = self.analyzer.rag_db.search(query, top_k=top_k)

            # Convert to serializable format
            search_results = [
                {
                    'component_id': r.component_id,
                    'component_name': r.component_name,
                    'similarity_score': r.similarity_score,
                    'context': r.context,
                    'relationships': r.relationships,
                }
                for r in results
            ]

            # Publish search event
            self.bus.publish_event(
                event_type='rag_semantic_search',
                source='rag_orchestrator',
                payload={
                    'query': query,
                    'results_count': len(search_results),
                    'top_k': top_k,
                    'timestamp': datetime.now().isoformat(),
                }
            )

            return search_results

        except Exception as e:
            self.logger.error(f"Semantic search failed: {e}")
            return []

    def get_augmented_report(self, file_id: str) -> Dict:
        """Generate RAG-augmented analysis report for a file."""
        if not self.is_rag_enabled():
            return {}

        try:
            # Get indexed components for this file
            db = RAGVectorDB()
            components = db.get_indexed_components(limit=100)

            file_components = [c for c in components if c.get('file_id') == file_id]

            # Analyze each component
            analyses = []
            for comp in file_components:
                analysis = self.analyzer.analyze_with_context(comp['component_id'])
                if analysis:
                    analyses.append(analysis)

            report = {
                'file_id': file_id,
                'total_components': len(file_components),
                'analyzed_components': len(analyses),
                'component_analyses': analyses,
                'generated_at': datetime.now().isoformat(),
            }

            # Publish report event
            self.bus.publish_event(
                event_type='rag_augmented_report',
                source='rag_orchestrator',
                payload={
                    'file_id': file_id,
                    'components_analyzed': len(analyses),
                    'timestamp': datetime.now().isoformat(),
                }
            )

            return report

        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            return {}

    def process_command(self, command: Dict) -> bool:
        """Process RAG orchestrator commands from bus."""
        try:
            cmd_type = command.get('command_type', '')

            if cmd_type == 'rag_index':
                file_id = command.get('file_id')
                repo_path = command.get('repo_path')
                if file_id is None or repo_path is None:
                    self.logger.error("file_id or repo_path is not defined")
                    return False
                return self.trigger_indexing(file_id, repo_path)

            elif cmd_type == 'rag_analyze':
                component_id = command.get('component_id')
                if component_id is None:
                    self.logger.error("component_id is not defined")
                    return False
                self.analyze_component(component_id)
                return True

            elif cmd_type == 'rag_search':
                self.search_components(
                    command.get('query', ''),
                    command.get('top_k', 5)
                )
                return True

            elif cmd_type == 'rag_report':
                file_id = command.get('file_id')
                if file_id is None:
                    self.logger.error("file_id is not defined")
                    return False
                self.get_augmented_report(file_id)
                return True

            else:
                self.logger.warning(f"Unknown RAG command: {cmd_type}")
                return False

        except Exception as e:
            self.logger.error(f"Command processing failed: {e}")
            return False

    def get_status(self) -> Dict:
        """Get RAG system status."""
        try:
            db = RAGVectorDB()
            indexed_components = db.get_indexed_components(limit=1)
            total_indexed = len(indexed_components)

            return {
                'rag_enabled': self.is_rag_enabled(),
                'total_indexed_components': total_indexed,
                'status': 'READY' if total_indexed > 0 else 'PENDING_INDEX',
                'vector_db': 'rag_vectors.db',
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Status check failed: {e}")
            return {'status': 'ERROR', 'error': str(e)}


# Singleton instance
_rag_orchestrator = None


def get_rag_orchestrator() -> RAGOrchestrator:
    """Get RAG orchestrator singleton."""
    global _rag_orchestrator
    if _rag_orchestrator is None:
        _rag_orchestrator = RAGOrchestrator()
    return _rag_orchestrator


if __name__ == "__main__":
    """Example usage."""
    logging.basicConfig(level=logging.INFO)

    orch = get_rag_orchestrator()

    print("RAG Orchestrator Status:")
    status = orch.get_status()
    print(json.dumps(status, indent=2))

    if orch.is_rag_enabled():
        print("\nRAG system is enabled and ready")
    else:
        print("\nRAG system is disabled - enable via settings")
