import React from 'react';
import { PageHeader } from '@/components/common/page-header';
import { LineageCard } from '@/components/common/lineage-card';

export default function DataLineagePage() {
  return (
    <div className="p-6 space-y-6">
      <PageHeader 
        title="Data Lineage Explorer" 
        description="Track the origin and transformations of platform metrics."
      />

      <div className="grid gap-6 md:grid-cols-2">
        <LineageCard 
          source="GitHub + Jira + Workday"
          period="Last 90 days"
          recordsProcessed={15420}
          formula="Weighted average of commit frequency, ticket resolution, and peer reviews."
          confidence="high"
          limitations={["Does not account for non-code contributions"]}
        />
        <LineageCard 
          source="Self-Assessment + Manager Review"
          period="H1 2023"
          recordsProcessed={850}
          formula="Normalized distribution across departments."
          confidence="medium"
          limitations={["Subjective bias possible", "Incomplete data for new hires"]}
        />
      </div>
    </div>
  );
}
