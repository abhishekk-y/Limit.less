import React from 'react';
import { PageHeader } from '@/components/common/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

export default function BillingPage() {
  return (
    <div className="p-6 space-y-6">
      <PageHeader title="Billing & Plans" description="Manage platform subscriptions and view invoices." />

      <div className="grid gap-6 md:grid-cols-3">
        <Card className="border-blue-200 shadow-sm relative overflow-hidden">
          <div className="absolute top-0 right-0 bg-blue-600 text-white text-xs px-3 py-1 font-semibold rounded-bl-lg">
            CURRENT PLAN
          </div>
          <CardHeader>
            <CardTitle>Enterprise</CardTitle>
            <div className="text-3xl font-bold mt-2">$2,499<span className="text-sm font-normal text-slate-500">/mo</span></div>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-slate-600 mb-6">
              <li>✓ Unlimited Users</li>
              <li>✓ Advanced Skill Galaxy</li>
              <li>✓ SSO Integration</li>
              <li>✓ Dedicated Success Manager</li>
            </ul>
            <Button variant="outline" className="w-full">Manage Subscription</Button>
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Recent Invoices</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {[
                { id: 'INV-2023-10', date: 'Oct 01, 2023', amount: '$2,499.00', status: 'Paid' },
                { id: 'INV-2023-09', date: 'Sep 01, 2023', amount: '$2,499.00', status: 'Paid' },
              ].map((invoice, idx) => (
                <div key={idx} className="flex justify-between items-center p-3 border-b last:border-0">
                  <div>
                    <div className="font-medium text-slate-800">{invoice.id}</div>
                    <div className="text-sm text-slate-500">{invoice.date}</div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="font-medium">{invoice.amount}</div>
                    <div className="text-xs bg-emerald-100 text-emerald-800 px-2 py-1 rounded-full">{invoice.status}</div>
                    <Button variant="ghost" size="sm" className="text-blue-600">Download</Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
