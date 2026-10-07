import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function ExperimentCenterPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Experiment Center</h1>
          <p className="text-muted-foreground mt-1">Platform Admin: ML Model evaluation and rollout.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Model Comparison: STS Prediction (v2.1)</CardTitle>
          <CardDescription>Evaluating new models against baseline</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs uppercase bg-muted">
                <tr>
                  <th className="px-6 py-3">Model</th>
                  <th className="px-6 py-3">MAE</th>
                  <th className="px-6 py-3">MAPE</th>
                  <th className="px-6 py-3">Latency (ms)</th>
                  <th className="px-6 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b">
                  <td className="px-6 py-4 font-medium">Linear Regression (Baseline)</td>
                  <td className="px-6 py-4">4.2</td>
                  <td className="px-6 py-4">8.5%</td>
                  <td className="px-6 py-4">12</td>
                  <td className="px-6 py-4">
                    <span className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded">DEPRECATED</span>
                  </td>
                </tr>
                <tr className="border-b bg-emerald-50/50">
                  <td className="px-6 py-4 font-medium">XGBoost (Candidate A)</td>
                  <td className="px-6 py-4 text-emerald-600 font-bold">2.1</td>
                  <td className="px-6 py-4 text-emerald-600 font-bold">4.2%</td>
                  <td className="px-6 py-4">45</td>
                  <td className="px-6 py-4">
                    <span className="bg-emerald-100 text-emerald-800 text-xs px-2 py-1 rounded">PRODUCTION</span>
                  </td>
                </tr>
                <tr className="border-b">
                  <td className="px-6 py-4 font-medium">Random Forest (Candidate B)</td>
                  <td className="px-6 py-4">2.4</td>
                  <td className="px-6 py-4">4.8%</td>
                  <td className="px-6 py-4">120</td>
                  <td className="px-6 py-4">
                    <span className="bg-amber-100 text-amber-800 text-xs px-2 py-1 rounded">EVALUATING</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="font-semibold mb-1">Deployment Decision</h4>
            <p className="text-sm text-muted-foreground">
              XGBoost selected for production rollout. It offers a 50% improvement in Mean Absolute Error over baseline, 
              with an acceptable inference latency of 45ms.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
