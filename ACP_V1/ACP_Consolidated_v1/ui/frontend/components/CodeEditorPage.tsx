import React from 'react';
import { Layers, FileText } from 'lucide-react';

const fileSystem = { name: 'code-factory', children: [ { name: 'stackbuilder', children: [ { name: 'stacks', children: [ { name: 'schema\'s', children: [{name: 'auth_v1.json'}] }, { name: 'generated_schema\'s', children: [{name: 'exp_payment_v3.json'}] }, { name: 'payment_gateway_v2.stack' } ] } ] } ]};

const FileTree = ({ node }) => (
    <div>
        <div className="flex items-center gap-2 text-sm py-1 cursor-pointer hover:bg-gray-800 rounded pr-2">
            {node.children ? <Layers size={14} className="shrink-0 text-gray-500" /> : <FileText size={14} className="shrink-0 text-blue-400" />}
            <span className="truncate">{node.name}</span>
        </div>
        {node.children && <div className="pl-4 border-l border-gray-800">{node.children.map((child, i) => <FileTree key={i} node={child} />)}</div>}
    </div>
);

export const CodeEditor = () => (
    <div className="h-full flex gap-6">
        <div className="w-1/3 max-w-xs bg-gray-900/50 border border-gray-800 rounded-xl p-4 overflow-y-auto">
            <h3 className="font-semibold text-lg flex items-center gap-2 mb-4">File Explorer</h3>
            <FileTree node={fileSystem} />
        </div>
        <div className="flex-1 h-full bg-[#1e1e1e] rounded-xl border border-gray-700 flex flex-col font-mono text-sm overflow-hidden">
            <div className="flex bg-[#252526] px-4 py-2 border-b border-black text-gray-400 gap-4 shrink-0">
                <span className="text-white bg-[#1e1e1e] px-3 py-1 rounded-t border-t-2 border-blue-500">auth_v1.json</span>
            </div>
            <div className="p-4 text-gray-300 overflow-auto">
                <pre>{`{
  "schema_name": "auth_v1",
  "version": "1.0.0",
  "components": [
    {
      "name": "JWT_Service",
      "type": "Security",
      "endpoint": "/auth/token"
    },
    {
      "name": "User_Database",
      "type": "Database",
      "provider": "PostgreSQL"
    }
  ]
}`}</pre>
            </div>
        </div>
    </div>
);
