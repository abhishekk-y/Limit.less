import * as React from "react"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function TeamComposerPage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-primary">Team Composer</h1>
          <p className="text-muted-foreground mt-1">Assemble the perfect cross-functional team.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Project Requirements</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-2">
                <label className="text-sm font-medium">Target Role / Project Type</label>
                <select className="border rounded-md px-3 py-2 w-full bg-background">
                  <option>GenAI Product Launch</option>
                  <option>Cloud Migration</option>
                </select>
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Required Team Size</label>
                <input type="number" className="border rounded-md px-3 py-2" defaultValue={5} />
              </div>
              <div className="grid gap-2">
                <label className="text-sm font-medium">Critical Skills (comma separated)</label>
                <input className="border rounded-md px-3 py-2" defaultValue="React, Python, AWS" />
              </div>
              <Button className="w-full mt-2">Generate Team</Button>
            </CardContent>
          </Card>
        </div>

        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Recommended Composition</CardTitle>
                <CardDescription>Optimized for skill coverage and availability</CardDescription>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-secondary">94%</div>
                <div className="text-xs text-muted-foreground">Skill Coverage</div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  { name: "Alice Sharma", role: "Lead Dev", match: 98 },
                  { name: "Bob Kumar", role: "Cloud Architect", match: 95 },
                  { name: "Carol Singh", role: "Data Scientist", match: 91 },
                ].map((emp) => (
                  <div key={emp.name} className="flex justify-between items-center p-3 border rounded-lg hover:bg-muted/30">
                    <div>
                      <p className="font-semibold">{emp.name}</p>
                      <p className="text-sm text-muted-foreground">{emp.role}</p>
                    </div>
                    <span className="text-sm font-medium bg-emerald-100 text-emerald-800 px-2 py-1 rounded">
                      {emp.match}% Match
                    </span>
                  </div>
                ))}
              </div>
              <Button className="w-full mt-6" variant="outline">Save Team Draft</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
