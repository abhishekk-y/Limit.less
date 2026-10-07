import React from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ConfidenceBadge } from '@/components/common/confidence-badge';

export default function SuccessionPage() {
  const criticalRoles = [
    { title: 'VP of Engineering', readiness: 85, candidates: 3, confidence: 'high' as const },
    { title: 'Chief Marketing Officer', readiness: 45, candidates: 1, confidence: 'medium' as const },
    { title: 'Lead Data Scientist', readiness: 20, candidates: 0, confidence: 'low' as const },
  ];

  return (
    <div className="p-6 space-y-6">
      <PageHeader 
        title="Succession Readiness" 
        description="Monitor pipeline health for critical organizational roles."
      />

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {criticalRoles.map((role, idx) => (
          <Card key={idx}>
            <CardHeader className="pb-2 flex flex-row items-center justify-between">
              <CardTitle className="text-lg font-medium">{role.title}</CardTitle>
              <ConfidenceBadge level={role.confidence} />
            </CardHeader>
            <CardContent>
              <div className="mt-4">
                <div className="flex justify-between mb-1 text-sm">
                  <span className="text-slate-500">Readiness Score</span>
                  <span className="font-semibold text-slate-800">{role.readiness}%</span>
                </div>
                <div className="w-full bg-slate-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${role.readiness > 70 ? 'bg-emerald-500' : role.readiness > 40 ? 'bg-amber-500' : 'bg-red-500'}`} 
                    style={{ width: `${role.readiness}%` }}
                  />
                </div>
                <p className="mt-4 text-sm text-slate-600">
                  <span className="font-semibold">{role.candidates}</span> ready candidates
                </p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
