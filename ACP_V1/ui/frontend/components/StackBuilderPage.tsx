import React, { useCallback } from 'react';
import ReactFlow, { MiniMap, Controls, Background, useNodesState, useEdgesState, addEdge } from 'reactflow';
import { Play } from 'lucide-react';

const initialNodes = [{ id: '1', type: 'input', data: { label: 'Data Ingest (S3)' }, position: { x: 50, y: 50 } }, { id: '2', data: { label: 'Auth Service' }, position: { x: 50, y: 200 } }, { id: '3', data: { label: 'Payment Gateway' }, position: { x: 300, y: 200 } }];
const initialEdges = [{ id: 'e1-2', source: '1', target: '2', animated: true, label: 'Confidence: 98%' }, { id: 'e2-3', source: '2', target: '3', label: 'Confidence: 95%' }];

export const StackBuilder = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
    const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
    const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

    return (
        <div className="h-full flex flex-col">
            <div className="mb-6 flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">Code Factory: Stack Builder</h2>
                    <p className="text-gray-400 text-sm">Visually compose, manage, and automate component stacks.</p>
                </div>
                <div className="flex gap-2 items-center">
                    <div className="flex gap-2 bg-gray-800 p-1 rounded-lg">
                        <button className="px-4 py-1.5 bg-gray-700 text-white text-sm rounded shadow">Manual Mode</button>
                        <button className="px-4 py-1.5 text-gray-400 hover:text-white text-sm rounded">Auto-Gen (AI)</button>
                    </div>
                    <button className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm rounded-lg font-medium flex items-center gap-2"><Play size={16}/>Deploy Stack</button>
                </div>
            </div>
            <div className="flex-1 rounded-xl overflow-hidden border border-gray-800"><ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} fitView><Controls /><MiniMap /><Background variant="dots" gap={12} size={1} /></ReactFlow></div>
        </div>
    );
};
