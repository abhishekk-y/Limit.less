import React from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { LineageCard } from '@/components/common/lineage-card';

export default function InterventionPlannerPage() {
  return (
    <div className="p-6 space-y-6">
      <PageHeader 
        title="Intervention Planner & Budget Optimizer" 
        description="Plan skill interventions and optimize L&D budget allocation."
        isDemo
        action={<Button className="bg-blue-800 hover:bg-blue-900">Run Optimizer</Button>}
      />

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recommended Interventions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { name: 'Cloud Native Upskilling', target: 'Backend Team', budget: '$15,000', impact: 'High' },
                { name: 'GenAI Prompt Engineering', target: 'Marketing', budget: '$5,000', impact: 'Medium' },
              ].map((item, idx) => (
                <div key={idx} className="flex justify-between items-center p-4 border rounded-lg bg-slate-50">
                  <div>
                    <h4 className="font-semibold text-slate-800">{item.name}</h4>
                    <p className="text-sm text-slate-500">Target: {item.target}</p>
                  </div>
                  <div className="text-right">
                    <div className="font-medium text-slate-900">{item.budget}</div>
                    <div className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded inline-block mt-1">Impact: {item.impact}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Budget Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-slate-800">$120,000</div>
              <p className="text-sm text-slate-500 mb-4">Total L&D Budget FY24</p>
              <div className="w-full bg-slate-200 rounded-full h-2 mb-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: '15%' }} />
              </div>
              <p className="text-xs text-right text-slate-500">15% Allocated ($20,000)</p>
            </CardContent>
          </Card>

          <LineageCard 
            source="HRIS Budget Module & L&D Feedback"
            period="FY24 Q1-Q4"
            recordsProcessed={450}
            formula="Risk vs Cost Matrix"
            confidence="medium"
            limitations={["Does not account for mid-year budget cuts"]}
          />
        </div>
      </div>
    </div>
  );
}
