"""Recompute published sourced-locked metrics and validate the six-expert aggregates."""
import csv
import json
from math import isclose
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parent


def close(a,b):
    assert isclose(float(a),float(b),rel_tol=1e-9,abs_tol=1e-9), (a,b)


def records(name):
    with (ROOT/name).open() as f:
        return list(csv.DictReader(f))


def main():
    meta=json.loads((ROOT/'hospital_protocol.json').read_text())
    src=json.loads((ROOT/'summary.json').read_text())
    perf=records('external_hospitals.csv')
    experts=records('expert_activation.csv')
    seeds=meta['seeds']
    sites=[s for s in meta['sites'] if s!='xiehe']
    methods=meta['models']
    assert len(perf)==len(sites)*len(seeds)*len(methods)
    assert len(experts)==len(meta['sites'])*len(seeds)*3*len(meta['expert_order'])
    def c(row):
        return [int(row[x]) for x in ('tp','fp','fn','tn')]
    def f1(v):
        tp,fp,fn,_=v
        return 2*tp/(2*tp+fp+fn)
    scores={}
    for row in perf:
        site,method,seed=row['site'],row['model'],int(row['seed'])
        v=c(row);tp,fp,fn,tn=v
        assert sum(v)==meta['sites'][site]['rows']==int(row['windows'])
        assert tp+fn==meta['sites'][site]['positives']==int(row['positives'])
        close(row['f1'],f1(v));close(row['precision'],tp/(tp+fp));close(row['recall'],tp/(tp+fn))
        close(row['specificity'],tn/(tn+fp))
        if method=='t_moe':
            assert int(row['epoch'])==src['threshold_replay'][str(seed)]['epoch']
            close(row['threshold'],src['threshold_replay'][str(seed)]['threshold'])
        key=(site,method,seed)
        assert key not in scores
        scores[key]=v
    for method in methods:
        vals=[]
        for site in sites:
            value=mean(f1(scores[site,method,s]) for s in seeds)
            close(value,meta['results'][site]['two_seed_f1'][method]);vals.append(value)
        close(mean(vals),meta['results']['equal_site_mean']['two_seed_f1'][method])
        pooled=[list(map(sum,zip(*(scores[site,method,s] for site in sites)))) for s in seeds]
        close(mean(map(f1,pooled)),meta['results']['pooled_windows']['two_seed_f1'][method])
    for v in meta['results'].values():
        for name,comp in v['paired_gain_pp'].items():
            close(comp['point'],100*(v['two_seed_f1']['t_moe']-v['two_seed_f1'][name]))
            assert len(comp['interval_95'])==2 and comp['interval_95'][0]<=comp['interval_95'][1]
    bykey={(r['site'],int(r['seed']),r['group'],r['expert']):r for r in experts}
    assert len(bykey)==len(experts)
    for site,info in meta['sites'].items():
        for s in seeds:
            for group,n in [('all', info['rows']), ('positive',info['positives']), ('negative',info['rows']-info['positives'])]:
                rows=[bykey[(site,s,group,e)] for e in meta['expert_order']]
                assert all(int(v['windows'])==n for v in rows)
                assert sum(int(v['top_weight_windows']) for v in rows)==n
                assert abs(sum(float(v['mean_weight']) for v in rows)-1)<1e-6
                for r in rows:
                    assert 0<=float(r['weight_q25'])<=float(r['weight_median'])<=float(r['weight_q75'])<=1
                    assert 0<=float(r['mean_expert_positive_probability'])<=1
                    close(r['top_weight_fraction'],int(r['top_weight_windows'])/n)
            for e in meta['expert_order']:
                rows=[bykey[site,s,g,e] for g in ('negative','positive')]
                all_row=bykey[site,s,'all',e]
                for metric in ('mean_weight','mean_expert_positive_probability','mean_weighted_margin'):
                    close(all_row[metric],sum(float(r[metric])*int(r['windows']) for r in rows)/info['rows'])
    print(f'Verified {len(perf)} external model/seed/site results and {len(experts)} activation rows.')


if __name__=='__main__':
    main()
