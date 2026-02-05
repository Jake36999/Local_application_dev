import React from 'react';
import { ToggleLeft, ToggleRight, Eye } from 'lucide-react';

interface CognitiveToolbarProps {
  dialecticalMode: boolean;
  setDialecticalMode: (enabled: boolean) => void;
  activeLens: string;
  setActiveLens: (lens: string) => void;
}

const LENSES = ["None", "Security", "UX", "Performance", "Ethical"];

const CognitiveToolbar: React.FC<CognitiveToolbarProps> = ({
  dialecticalMode,
  setDialecticalMode,
  activeLens,
  setActiveLens
}) => {
  return (
    <div className="flex items-center justify-between bg-gray-800 p-3 rounded-t-lg border-b border-gray-700">
      <div className="flex items-center space-x-3">
        <button
          onClick={() => setDialecticalMode(!dialecticalMode)}
          className="flex items-center gap-2 text-sm font-mono text-cyan-400 font-bold uppercase hover:text-cyan-300"
        >
          {dialecticalMode ? <ToggleRight size={24} /> : <ToggleLeft size={24} />}
          <span>Dialectical Mode</span>
        </button>
      </div>
      <div className="flex items-center space-x-2">
        <Eye size={16} className="text-gray-400" />
        <span className="text-sm text-gray-400 font-mono">Lens:</span>
        <select
          value={activeLens}
          onChange={(e) => setActiveLens(e.target.value)}
          className="bg-gray-900 text-white border border-gray-600 rounded px-2 py-1 text-xs font-mono focus:border-cyan-500 outline-none"
        >
          {LENSES.map((lens) => (
            <option key={lens} value={lens}>{lens}</option>
          ))}
        </select>
      </div>
    </div>
  );
};

export default CognitiveToolbar;
