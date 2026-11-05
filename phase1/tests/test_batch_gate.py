import torch

def decision(logits,positions,mask):
    opts=[]
    for field,pos in positions.items():
        z=logits[pos].float().clone();z[mask]=-float('inf')
        p=torch.softmax(z,dim=-1)
        opts.append((field,int(p.argmax()),float(p.max())))
    best=max(x[2] for x in opts)
    return sorted((field,tok) for field,tok,p in opts if p==best)

def test_nonwinning_logit_variation_does_not_change_decision():
    one=torch.tensor([[2.,1.,0.],[0.,2.,1.]])
    batched=torch.tensor([[2.,1.03,0.],[0.02,2.,1.]])
    assert not torch.equal(one,batched)
    assert decision(one,{'A':0,'B':1},2)==decision(batched,{'A':0,'B':1},2)
