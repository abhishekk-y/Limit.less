"""Regenerate README figures from recorded public/aggregate evidence (no raw inputs)."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/assets/figures'
OUT.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
g=json.loads((ROOT/'docs/evidence/greenhouse-live-check.json').read_text(encoding='utf-8'))
h=json.loads((ROOT/'sas-hackathon/evidence/reproduced_source_metrics.json').read_text(encoding='utf-8'))
rows=g['skill_mentions'][:8][::-1]
fig,ax=plt.subplots(figsize=(10,5.8),layout='constrained')
bars=ax.barh([r['skill'] for r in rows],[r['rate_percent'] for r in rows],color='#7c3aed')
ax.bar_label(bars,labels=[f"{r['rate_percent']:.2f}% ({r['count']}/{r['denominator']})" for r in rows],padding=6)
ax.set_xlim(0,100);ax.set_xlabel('Returned postings mentioning skill (%)')
ax.set_title('Observed skill mentions · selected employer board',loc='left',weight='bold')
fig.supxlabel(f"Greenhouse / cloudflare · n={g['row_count']} · collection {g['retrieved_at_utc'][:10]} UTC\nRecorded feed evidence; not national market demand",fontsize=9)
for suffix in ('png','svg'):fig.savefig(OUT/f'live-skill-demand.{suffix}',dpi=180,bbox_inches='tight')
plt.close(fig)
quality=[('Missing descriptions',3508,15841),('Missing job type',12011,15841),('Skill fields with ellipsis',13806,15841),('Excess repeated references',142,1602)]
fig,ax=plt.subplots(figsize=(10,5.3),layout='constrained')
bars=ax.barh([r[0] for r in quality][::-1],[r[1]/r[2]*100 for r in quality][::-1],color=['#7c3aed','#f59e0b','#f59e0b','#f59e0b'])
ax.bar_label(bars,labels=[f'{n/d*100:.2f}% ({n:,}/{d:,})' for _,n,d in quality][::-1],padding=6)
ax.set_xlim(0,115);ax.set_xlabel('Diagnostic share within its source (%)')
ax.set_title('Recorded dataset quality diagnostics',loc='left',weight='bold')
fig.supxlabel('Descriptions, type and ellipsis: Analytics Jobs. Reference repeats: DataScience Jobs.\nLocal aggregate reproduction; SAS VFL verification pending.',fontsize=9)
for suffix in ('png','svg'):fig.savefig(OUT/f'dataset-quality.{suffix}',dpi=180,bbox_inches='tight')
plt.close(fig)
print('Generated PNG and SVG evidence figures from recorded counts.')
