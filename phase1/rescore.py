"""Independent trace field scorer; does not import the task or decoder modules."""
import argparse,json,random
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--model',required=True);a=p.parse_args()
base=Path('results/phase1');summary={}
for exp in (1,2,3):
    rows=[json.loads(s) for s in (base/'traces'/f'{a.model}-exp{exp}.jsonl').read_text().splitlines() if s]
    rng=random.Random(81173+exp)
    sample=rng.sample(rows,min(20,len(rows)))
    for row in sample:
        expected_a=row['predicted_A']==row['target_A']
        expected_b=row['predicted_B']==row['target_B']
        assert row['A_correct'] is expected_a,row['run_id']
        assert row['B_correct'] is expected_b,row['run_id']
        assert row['both_correct'] is (expected_a and expected_b),row['run_id']
        assert row['B_matches_alternative'] is (None if row['alternative_B'] is None else row['predicted_B']==row['alternative_B']),row['run_id']
        assert len(row['steps'])==(2 if exp in (1,2) else 1),row['run_id']
        assert len({step['slot'] for step in row['steps']})==len(row['steps']),row['run_id']
        assert row['first_field']==row['steps'][0]['slot'],row['run_id']
        final={step['slot']:step['token'] for step in row['steps']}
        assert final.get('B')==row['predicted_B'],row['run_id']
        if exp in (1,2):assert final.get('A')==row['predicted_A'],row['run_id']
        assert all(0<=step['prob']<=1 for step in row['steps']),row['run_id']
    summary[str(exp)]={'checked':len(sample),'run_ids':[r['run_id'] for r in sample],'status':'pass'}
(base/f'rescore-{a.model}.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:{'checked':v['checked'],'status':v['status']} for k,v in summary.items()},indent=2))
