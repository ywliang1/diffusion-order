import random
import re


def pool(tokenizer, mask_id, minimum=200):
    candidates=[]; seen=set()
    for token_id in range(len(tokenizer)):
        if token_id == mask_id: continue
        word=tokenizer.decode([token_id],skip_special_tokens=False)
        if re.fullmatch(r'[a-z]{3,9}',word) and len(tokenizer.encode(' '+word,add_special_tokens=False))==1 and word not in seen:
            candidates.append(word);seen.add(word)
    if len(candidates)<minimum: raise ValueError(f'only {len(candidates)} plain alphabetic single tokens')
    return candidates


def make_source(size, source_id, words, seed):
    rng=random.Random((seed*1000003+size*1009+source_id))
    # Shuffle the value pool and use each lexical value once per source.
    vals=rng.sample(words,6*size)
    rows=[]
    for i in range(size):
        rows.append(dict(q=f'k{i:02d}',A=vals[6*i],H=vals[6*i+1],B=vals[6*i+2],C=vals[6*i+3],D=vals[6*i+4],E=vals[6*i+5]))
    target=rng.randrange(size)
    wrong=rng.choice([i for i in range(size) if i!=target])
    return dict(size=size,source_id=source_id,rows=rows,target=target,wrong=wrong)


def tables(source,condition,seed):
    rows=source['rows']; n=len(rows)
    rng=random.Random(seed*1000003+n*1009+source['source_id']*17+{'Direct':1,'Shared-path':2,'Separate-path':3}[condition])
    a=list(rows); b=list(rows); rng.shuffle(a); rng.shuffle(b)
    if condition=='Direct':
        anchor=[f"{r['q']} {r['A']} {r['H']} {r['B']}" for r in a]
        mapping=[f"{r['D']} {r['E']}" for r in b]
    elif condition=='Shared-path':
        anchor=[f"{r['q']} {r['A']} {r['H']} {r['C']}" for r in a]
        mapping=[f"{r['A']} {r['B']}" for r in b]
    else:
        anchor=[f"{r['q']} {r['A']} {r['H']} {r['C']}" for r in a]
        mapping=[f"{r['H']} {r['B']}" for r in b]
    return 'Anchor (key A H value):\n'+'\n'.join(anchor)+'\nMapping (left right):\n'+'\n'.join(mapping)


def integrity(source,condition):
    rows=source['rows']; t=source['target']; target=rows[t]
    assert len({r['q'] for r in rows})==len(rows)
    assert len({v for r in rows for k,v in r.items() if k!='q'})==6*len(rows)
    if condition=='Shared-path': assert [r['B'] for r in rows if r['A']==target['A']]==[target['B']]
    if condition=='Separate-path': assert [r['B'] for r in rows if r['H']==target['H']]==[target['B']]
    return True

def usable_pool(tokenizer,mask_id,raw_words,instruction,minimum=200):
    from phase1.decoder import aligned
    anchor=next((w for w in raw_words if aligned(tokenizer,mask_id,instruction,w,w)),None)
    if anchor is None: raise ValueError('no self-aligned anchor value')
    usable=[w for w in raw_words if aligned(tokenizer,mask_id,instruction,w,anchor) and aligned(tokenizer,mask_id,instruction,anchor,w)]
    if len(usable)<minimum: raise ValueError(f'only {len(usable)} aligned values')
    return usable
