import random
import torch


def render(tokenizer, mask_id, instruction, A=None, B=None):
    mask=tokenizer.decode([mask_id],skip_special_tokens=False)
    prefix=tokenizer.apply_chat_template([{'role':'user','content':instruction}],tokenize=False,add_generation_prompt=True)
    output='{"a":"'+(A if A is not None else mask)+'","b":"'+(B if B is not None else mask)+'"}'
    ids=tokenizer.encode(prefix+output,add_special_tokens=False)
    slots={}
    if A is None or B is None:
        positions=[i for i,v in enumerate(ids) if v==mask_id]
        expected=int(A is None)+int(B is None)
        if len(positions)!=expected: raise ValueError(f'mask count {len(positions)} != {expected}')
        fields=(["A"] if A is None else [])+(["B"] if B is None else [])
        slots=dict(zip(fields,positions))
    return ids,slots


def aligned(tokenizer,mask_id,instruction,A,B):
    gold,_=render(tokenizer,mask_id,instruction,A,B)
    mask,slots=render(tokenizer,mask_id,instruction)
    a=tokenizer.encode(A,add_special_tokens=False); b=tokenizer.encode(B,add_special_tokens=False)
    return len(a)==len(b)==1 and len(mask)==len(gold) and all(mask[i]==gold[i] or i in slots.values() for i in range(len(mask))) and gold[slots['A']]==a[0] and gold[slots['B']]==b[0]


def slot_logits(model,x):
    logits=model(input_ids=x,use_cache=False).logits
    if model.config.model_type=='Dream':
        # Dream's generation_utils shifts next-token logits to masked slots.
        logits=torch.cat([logits[:,:1],logits[:,:-1]],dim=1)
    return logits


@torch.no_grad()
def decode(model,tokenizer,mask_id,ids,slots,order,seed):
    x=torch.tensor([ids],device=model.device)
    rng=random.Random(seed)
    steps=[]; step0={}; tie=False
    remaining=dict(slots)
    while remaining:
        logits=slot_logits(model,x)[0]
        choices={}
        for field,pos in remaining.items():
            z=logits[pos].float().clone(); z[mask_id]=-float('inf')
            probs=torch.softmax(z,dim=-1)
            top=torch.topk(probs,5)
            choices[field]=(int(top.indices[0]),float(top.values[0]),[int(t) for t in top.indices.tolist()],[float(p) for p in top.values.tolist()])
            if not steps: step0[field]={'top5_tokens':[tokenizer.decode([t]) for t in choices[field][2]],'top5_probs':choices[field][3]}
        if order=='CF':
            best=max(v[1] for v in choices.values()); winners=[k for k,v in choices.items() if v[1]==best]
            if len(winners)>1: tie=True
            field=rng.choice(winners)
        else: field=('A' if order=='A-first' else 'B') if ('A' if order=='A-first' else 'B') in remaining else next(iter(remaining))
        tok,prob,*_=choices[field]
        x[0,remaining[field]]=tok
        steps.append({'slot':field,'token':tokenizer.decode([tok]),'token_id':tok,'prob':prob})
        del remaining[field]
    pred={f:tokenizer.decode([int(x[0,p])]) for f,p in slots.items()}
    return pred,steps,step0,tie
