"use client"

import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function ShockSimulatorPage() {
  const [aiDemand, setAiDemand] = React.useState(50)

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Shock Simulator</h1>
          <p className="text-muted-foreground mt-1">Model macroeconomic shocks and tech disruptions.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Scenario Variables</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium">GenAI Adoption Acceleration</label>
                  <span className="text-sm font-medium text-primary">+{aiDemand}%</span>
                </div>
                <input 
                  type="range" 
                  min="0" max="100" 
                  value={aiDemand}
                  onChange={(e) => setAiDemand(Number(e.target.value))}
                  className="w-full"
                />
              </div>
              <Button className="w-full">Run Simulation</Button>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Impact Analysis</CardTitle>
              <CardDescription>Predicted impact on current workforce over 18 months</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 mb-6">
                <div className="p-4 bg-red-50 rounded-lg border border-red-100">
                  <p className="text-sm font-medium text-red-800 mb-1">Roles at Risk</p>
                  <p className="text-3xl font-bold text-red-600">
                    {Math.floor(aiDemand * 2.5)}
                  </p>
                </div>
                <div className="p-4 bg-emerald-50 rounded-lg border border-emerald-100">
                  <p className="text-sm font-medium text-emerald-800 mb-1">New Roles Needed</p>
                  <p className="text-3xl font-bold text-emerald-600">
                    {Math.floor(aiDemand * 1.8)}
                  </p>
                </div>
              </div>

              <h4 className="font-semibold mb-3">Action Plan Recommendation</h4>
              <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-5">
                <li>Initiate immediate reskilling program for <strong>{Math.floor(aiDemand * 1.2)}</strong> employees in legacy tech.</li>
                <li>Open external hiring for <strong>{Math.floor(aiDemand * 0.6)}</strong> prompt engineers and LLM specialists.</li>
                <li>Estimated Budget Required: <strong>₹{(aiDemand * 0.5).toFixed(1)} Cr</strong></li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
