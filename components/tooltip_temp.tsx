// Temporary file to verify exact tooltip content
const tooltipSection = `
{/* Tooltip on Hover */}
<div className="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 w-64 p-3 bg-slate-900 border border-amber-500/30 rounded-xl shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50 pointer-events-none">
    <div className="text-[10px] space-y-2">
        <div className="font-black text-amber-400 uppercase tracking-wider border-b border-slate-700 pb-1">
            Desglose: {broker.name}
        </div>
        
        {/* Engagement Breakdown */}
        <div className="flex items-center justify-between">
            <span className="text-emerald-400 font-bold">🟢 Engagement & Gestión:</span>
            <span className="text-white font-mono">{((broker.score_engagement || 0) * 100).toFixed(1)} / 35</span>
        </div>
        
        {/* Rendimiento Breakdown */}
        <div className="flex items-center justify-between">
            <span className="text-blue-400 font-bold">🔵 Rendimiento & Conversión:</span>
            <span className="text-white font-mono">{((broker.score_rendimiento || 0) * 100).toFixed(1)} / 40</span>
        </div>
        
        <div className="border-t border-slate-700 pt-1 mt-1 flex items-center justify-between">
            <span className="text-slate-400 font-bold">TOTAL:</span>
            <span className="text-amber-400 font-black font-mono">{((broker.score || 0) * 100).toFixed(1)} / 75</span>
        </div>
    </div>
</div>
`;
