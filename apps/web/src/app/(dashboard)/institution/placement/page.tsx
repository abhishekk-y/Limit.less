import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function PlacementPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Placement Dashboard</h1>
          <p className="text-muted-foreground mt-1">Cohort readiness and placement metrics.</p>
        </div>
        <Button variant="outline">Download Report</Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Cohort Size</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">450</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Readiness</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-secondary">72%</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Top Percentile (90+)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">45</div>
            <p className="text-xs text-muted-foreground">students</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg STS Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">68</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Top Students (by Readiness)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex justify-between items-center border-b pb-2">
              <div>
                <p className="font-semibold">Student A</p>
                <p className="text-sm text-muted-foreground">B.Tech CS</p>
              </div>
              <span className="font-bold text-secondary">94%</span>
            </div>
            <div className="flex justify-between items-center border-b pb-2">
              <div>
                <p className="font-semibold">Student B</p>
                <p className="text-sm text-muted-foreground">B.Tech IT</p>
              </div>
              <span className="font-bold text-secondary">91%</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
