'use client';

import React, { useState, useEffect, useRef } from 'react';

interface SkillNode {
  id: string;
  label: string;
  demand: number;
  userHas: boolean;
  isGap: boolean;
  growth: number;
  category: string;
}

const demoNodes: SkillNode[] = [
  { id: 'python', label: 'Python', demand: 92, userHas: true, isGap: false, growth: 5, category: 'Programming' },
  { id: 'fastapi', label: 'FastAPI', demand: 68, userHas: true, isGap: false, growth: 25, category: 'Web' },
  { id: 'docker', label: 'Docker', demand: 81, userHas: false, isGap: true, growth: 12, category: 'DevOps' },
  { id: 'aws', label: 'AWS', demand: 85, userHas: false, isGap: true, growth: 15, category: 'Cloud' },
  { id: 'react', label: 'React', demand: 78, userHas: true, isGap: false, growth: 3, category: 'Web' },
  { id: 'sql', label: 'SQL', demand: 82, userHas: true, isGap: false, growth: 2, category: 'Data' },
  { id: 'ml', label: 'Machine Learning', demand: 89, userHas: true, isGap: false, growth: 20, category: 'AI/ML' },
  { id: 'pytorch', label: 'PyTorch', demand: 75, userHas: false, isGap: true, growth: 30, category: 'AI/ML' },
  { id: 'kubernetes', label: 'Kubernetes', demand: 72, userHas: false, isGap: true, growth: 18, category: 'DevOps' },
  { id: 'git', label: 'Git', demand: 72, userHas: true, isGap: false, growth: 1, category: 'Tools' },
  { id: 'linux', label: 'Linux', demand: 70, userHas: true, isGap: false, growth: 2, category: 'Systems' },
  { id: 'rag', label: 'RAG', demand: 65, userHas: false, isGap: true, growth: 85, category: 'AI/ML' },
  { id: 'ci_cd', label: 'CI/CD', demand: 66, userHas: false, isGap: true, growth: 10, category: 'DevOps' },
  { id: 'typescript', label: 'TypeScript', demand: 74, userHas: false, isGap: false, growth: 15, category: 'Programming' },
  { id: 'postgres', label: 'PostgreSQL', demand: 71, userHas: true, isGap: false, growth: 8, category: 'Data' },
  { id: 'terraform', label: 'Terraform', demand: 58, userHas: false, isGap: true, growth: 22, category: 'DevOps' },
];

const modes = ['Demand', 'Growth', 'SHI', 'User Profile', 'Gaps'] as const;
const timelineModes = ['NOW', 'NEXT (6-12 mo)', 'HORIZON (2+ yr)'] as const;
const categoryColors: Record<string, string> = {
  Programming: '#3b82f6', Web: '#8b5cf6', DevOps: '#f97316', Cloud: '#06b6d4',
  'AI/ML': '#ec4899', Data: '#10b981', Tools: '#6b7280', Systems: '#eab308',
};

export default function SkillGalaxyPage() {
  const [mode, setMode] = useState<typeof modes[number]>('Demand');
  const [timeline, setTimeline] = useState(0);
  const [selectedNode, setSelectedNode] = useState<SkillNode | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, rect.width, rect.height);

    // Draw edges (co-occurrence)
    const edges = [
      ['python', 'fastapi'], ['python', 'ml'], ['python', 'sql'], ['python', 'pytorch'],
      ['docker', 'kubernetes'], ['docker', 'ci_cd'], ['docker', 'aws'],
      ['aws', 'terraform'], ['aws', 'kubernetes'], ['ml', 'pytorch'], ['ml', 'rag'],
      ['react', 'typescript'], ['sql', 'postgres'], ['linux', 'docker'], ['git', 'ci_cd'],
      ['fastapi', 'postgres'], ['fastapi', 'docker'],
    ];

    const nodePositions: Record<string, { x: number; y: number }> = {};
    const cx = rect.width / 2, cy = rect.height / 2;
    demoNodes.forEach((node, i) => {
      const angle = (2 * Math.PI * i) / demoNodes.length;
      const radius = 140 + Math.random() * 60;
      nodePositions[node.id] = { x: cx + Math.cos(angle) * radius, y: cy + Math.sin(angle) * radius };
    });

    edges.forEach(([from, to]) => {
      const a = nodePositions[from], b = nodePositions[to];
      if (a && b) {
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.3)';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }
    });

    // Draw nodes
    demoNodes.forEach(node => {
      const pos = nodePositions[node.id];
      const size = 8 + (node.demand / 100) * 20;
      const color = categoryColors[node.category] || '#6b7280';

      // Glow for user skills
      if (node.userHas) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, size + 6, 0, 2 * Math.PI);
        ctx.fillStyle = `${color}33`;
        ctx.fill();
      }

      // Red ring for gaps
      if (node.isGap) {
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, size + 3, 0, 2 * Math.PI);
        ctx.strokeStyle = '#ef4444';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Node
      ctx.beginPath();
      ctx.arc(pos.x, pos.y, size, 0, 2 * Math.PI);
      ctx.fillStyle = node.userHas ? color : `${color}88`;
      ctx.fill();

      // Label
      ctx.fillStyle = '#1f2937';
      ctx.font = '11px Inter, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(node.label, pos.x, pos.y + size + 14);
    });
  }, [mode, timeline]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Skill Galaxy</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Interactive skill-role-demand visualization</p>
        </div>
        <span className="text-xs px-2 py-1 rounded bg-purple-100 text-purple-800 mt-2 md:mt-0">DEMO</span>
      </div>

      {/* Mode Selector */}
      <div className="flex flex-wrap gap-2">
        {modes.map(m => (
          <button key={m} onClick={() => setMode(m)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              mode === m ? 'bg-blue-600 text-white' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-700 hover:bg-gray-50'
            }`}>{m}</button>
        ))}
      </div>

      {/* Galaxy Canvas */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-2">
        <canvas ref={canvasRef} className="w-full h-[500px] rounded-lg cursor-crosshair" style={{ background: 'radial-gradient(circle, #f8fafc 0%, #e2e8f0 100%)' }} />
      </div>

      {/* Telescope Timeline */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3">Skill Telescope</h3>
        <div className="flex items-center gap-4">
          {timelineModes.map((t, i) => (
            <button key={t} onClick={() => setTimeline(i)}
              className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                timeline === i ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300'
              }`}>{t}</button>
          ))}
        </div>
        <input type="range" min={0} max={2} value={timeline} onChange={e => setTimeline(Number(e.target.value))}
          className="w-full mt-3 accent-blue-600" aria-label="Timeline slider" />
      </div>

      {/* Legend */}
      <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
        <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Legend</h4>
        <div className="flex flex-wrap gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500" /> <span>Your Skill (glowing)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-300 ring-2 ring-red-500" /> <span>Skill Gap</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-gray-300" /> <span>Large = High Demand</span>
          </div>
          {Object.entries(categoryColors).map(([cat, color]) => (
            <div key={cat} className="flex items-center gap-1">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} /> <span>{cat}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
