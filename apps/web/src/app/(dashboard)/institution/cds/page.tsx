import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function CDSDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Curriculum Drift Score (CDS)</h1>
          <p className="text-muted-foreground mt-1">Measure alignment against real-time industry demand.</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Overall CDS</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-amber-500">18.4%</div>
            <p className="text-xs text-muted-foreground mt-2">Moderate Drift detected</p>
          </CardContent>
        </Card>
        
        <Card className="md:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Largest Gaps (Missing from Curriculum)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between items-center text-sm border-b pb-1">
              <span>Cloud Native Architecture</span>
              <span className="text-red-500 font-medium">Critical Deficit</span>
            </div>
            <div className="flex justify-between items-center text-sm border-b pb-1">
              <span>Prompt Engineering</span>
              <span className="text-red-500 font-medium">Critical Deficit</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Time Machine</CardTitle>
          <CardDescription>Historical CDS Trend over the last 4 years</CardDescription>
        </CardHeader>
        <CardContent className="flex items-center justify-center h-64 bg-muted/30 border-dashed border-2 rounded-md">
          <p className="text-muted-foreground">[ Line Chart Placeholder: CDS Over Time ]</p>
        </CardContent>
      </Card>
    </div>
  )
}
