import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score

scores = []
with open("pair_score.list") as f:
    lines = f.readlines()
    for line in lines:
      line = line.strip()
      score = float(line)
      scores.append(score)

# test
scores = np.random.rand(6000).tolist()

y = []
for i in range(6000):
    if i < 3000:  
        y.append(0)
    else:
        y.append(1)
        
roc_x = []
roc_y = []
min_score = min(scores)
max_score = max(scores)
thr = np.linspace(min_score, max_score, 100)

FP = 0
TP = 0
TN = 0
N = 3000
P = 3000
acc_list = []
for i, T in enumerate(thr):
    for i in range(0, len(scores)):
      if scores[i] > T:
          if y[i] == 1:
              TP = TP + 1
          if y[i] == 0:
              FP = FP + 1
      else:
          if y[i] == 0:
              TN = TN + 1
    roc_x.append(FP / float(N))
    roc_y.append(TP / float(P))
    acc= (TP + TN) * 1.0 / (N+P)
    acc_list.append(acc)
    FP = 0
    TP =0
    TN = 0
    
plt.plot(roc_x, roc_y, '--*b')
plt.savefig("roc.pdf")

auc = roc_auc_score(y, scores)
print('AUC: {}'.format(auc))
print('ACC:'.format(max(acc_list)))
