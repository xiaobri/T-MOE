"""Regenerate external test tables and expert heatmaps from the public aggregate files."""
import csv
import json
from pathlib import Path
from statistics import mean

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

PAPER = Path(__file__).resolve().parent
RESULTS = PAPER.parent / 'results'
SITES = {'qilu':'Qilu', 'tiantan':'Tiantan', 'chifeng':'Chifeng', 'xian':"Xi'an"}
EXPERTS = {'frontal':'Frontal','left_temporal':'Left temporal','right_temporal':'Right temporal',
           'centro_parietal':'Centro-parietal','occipital':'Occipital','global':'Global'}
SHORT = ('Front.', 'L temp.', 'R temp.', 'C-par.', 'Occip.', 'Global')


def percent(x):
    return f'{100 * float(x):.2f}'


def csv_rows(name):
    with (RESULTS/name).open() as f:
        return list(csv.DictReader(f))


def write_table(name, rows):
    (PAPER/'tables'/f'{name}.tex').write_text(''.join(' & '.join(str(x) for x in row) + r' \\' + '\n' for row in rows))


def check_counts(row):
    tp, fp, fn, tn = (int(row[k]) for k in ('tp','fp','fn','tn'))
    assert tp + fn == int(row['positives'])
    assert tp + fp + fn + tn == int(row['windows'])
    assert abs(float(row['f1'])-2*tp/(2*tp+fp+fn)) < 1e-12


def main():
    perf = csv_rows('external_hospitals.csv')
    activity = csv_rows('expert_activation.csv')
    protocol = json.loads((RESULTS/'hospital_protocol.json').read_text())
    primary = protocol['results']
    methods = ('baseline','matched_baseline','fresh_both','t_moe')
    assert len(perf) == len(SITES)*len(methods)*2
    for r in perf:
        check_counts(r)
    overview, singles = [], []
    for code,name in {**SITES,'equal_site_mean':'Equal-site mean','pooled_windows':'Pooled windows'}.items():
        row = primary[code]
        site = protocol['sites'].get(code)
        cell = f"{site['rows']:,} ({site['positives']:,})" if site else '--'
        dif = row['paired_gain_pp']['fresh_both']
        interval = ', '.join(f'{v:+.2f}' for v in dif['interval_95'])
        overview.append([name,cell,*[percent(row['two_seed_f1'][m]) for m in methods],
                         f"{dif['point']:+.2f}",f'[{interval}]'])
        if site is None:
            continue
        subset = [r for r in perf if r['site']==code]
        for method in methods:
            s = [r for r in subset if r['model']==method]
            assert len(s)==2 and abs(mean(float(r['f1']) for r in s)-row['two_seed_f1'][method])<1e-12
        for r in sorted((r for r in subset if r['model']=='t_moe'),key=lambda r:int(r['seed'])):
            singles.append([name,r['seed'],*[f'{int(r[k]):,}' for k in ('tp','fp','fn','tn')],
                            *[percent(r[k]) for k in ('precision','recall','f1','average_precision','auroc')]])
    write_table('external_overview',overview)
    write_table('external_operating',singles)
    weights = {(r['site'],r['group'],r['expert'],int(r['seed'])):r for r in activity}
    population = {'xiehe':'Xiehe', **SITES}
    def value(site,group,expert,key):
        return mean(float(weights[site,group,expert,seed][key]) for seed in (3,42))
    src = []
    for expert,label in EXPERTS.items():
        src.append([label,*[percent(value('xiehe',g,expert,k)) for k in
                            ('mean_weight','top_weight_fraction','mean_expert_positive_probability') for g in ('negative','positive')]])
    write_table('source_experts',src)
    fig, axes = plt.subplots(2,2,figsize=(8.6,4.45))
    for j,(key,title) in enumerate([('mean_weight','Mean routing weight (%)'),
                                    ('mean_expert_positive_probability','Mean expert positive score (%)')]):
        data = [np.array([[100*value(site,g,e,key) for e in EXPERTS] for site in population]) for g in ('negative','positive')]
        ceiling = min(100, max(10, 10 * np.ceil(max(x.max() for x in data) / 10)))
        norm = Normalize(0, ceiling)
        for i,mat in enumerate(data):
            ax=axes[i,j]
            ax.imshow(mat,aspect='auto',cmap='Blues',norm=norm)
            if i==0: ax.set_title(title,fontsize=10.5,pad=8)
            ax.set_xticks(range(6),SHORT,fontsize=8)
            ax.set_yticks(range(5), list(population.values()) if j==0 else ['']*5,fontsize=8.4)
            ax.tick_params(length=0)
            if j==0: ax.set_ylabel(('Negative windows','Positive windows')[i],fontsize=9,fontweight='bold')
            for spine in ax.spines.values():
                spine.set_visible(False)
            for a in range(mat.shape[0]):
                for b in range(mat.shape[1]):
                    ax.text(b,a,f'{mat[a,b]:.1f}',ha='center',va='center',fontsize=8.4,
                            color='white' if norm(mat[a,b])>.62 else '#111e29')
    fig.subplots_adjust(left=.13,right=.992,top=.915,bottom=.062,wspace=.085,hspace=.29)
    fig.savefig(PAPER/'figures'/'hospital-experts.pdf',metadata={'CreationDate':None})


if __name__=='__main__':
    main()
