import React from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, CheckCircle } from 'lucide-react';

export default function FairnessAuditPage() {
  return (
    <div className="p-6 space-y-6">
      <PageHeader 
        title="Fairness & Bias Audit" 
        description="Monitor AI recommendations for potential demographic bias."
      />

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="text-emerald-500" size={20} />
              Promotion Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600 mb-4">Analysis of Career GPS promotion suggestions across demographic groups.</p>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Gender Distribution</span>
                <span className="font-medium text-emerald-600">Within acceptable variance (±2%)</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Age Distribution</span>
                <span className="font-medium text-emerald-600">Within acceptable variance (±3%)</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="border-amber-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="text-amber-500" size={20} />
              Skill Inference Model
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-slate-600 mb-4">Analysis of skills extracted from unstructured data (resumes, projects).</p>
            <div className="p-3 bg-amber-50 text-amber-800 text-sm rounded-md border border-amber-100">
              <span className="font-semibold block mb-1">Observation:</span>
              The model tends to over-index leadership skills for users in specific tenure brackets. Requires calibration.
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
