import React from 'react';

interface DialecticalProps {
  data: { thesis: string; antithesis: string; synthesis: string; };
}

const DialecticalView: React.FC<DialecticalProps> = ({ data }) => {
  return (
    <div className="flex flex-col w-full bg-slate-900 text-slate-100 p-4 rounded-lg border border-slate-700 my-4">
      <div className="text-center border-b border-slate-700 pb-2 mb-4">
        <h2 className="text-xs font-bold text-cyan-400 tracking-widest uppercase">Dialectical Engine</h2>
      </div>
      <div className="flex flex-row gap-4 mb-4">
        <div className="w-1/2 p-3 border border-green-900 bg-green-900/10 rounded">
          <h3 className="text-green-500 font-bold text-xs uppercase mb-2">Thesis</h3>
          <p className="text-sm text-slate-300">{data.thesis}</p>
        </div>
        <div className="w-1/2 p-3 border border-red-900 bg-red-900/10 rounded">
          <h3 className="text-red-500 font-bold text-xs uppercase mb-2">Antithesis</h3>
          <p className="text-sm text-slate-300">{data.antithesis}</p>
        </div>
      </div>
      <div className="p-3 border-t border-cyan-900 bg-cyan-900/10 rounded">
        <h3 className="text-cyan-500 font-bold text-xs uppercase mb-2 text-center">Synthesis</h3>
        <p className="text-sm text-slate-200 text-center">{data.synthesis}</p>
      </div>
    </div>
  );
};

export default DialecticalView;
