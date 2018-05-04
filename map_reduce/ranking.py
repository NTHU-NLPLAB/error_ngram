import fileinput
from operator import itemgetter

all_pat = []
for line in fileinput.input():
    patterns = line.split('\t')
    
    main, total_count = patterns[0].split('|')
    
    # 同組的 pattern 先排序
    items = sorted(map(lambda ptn: ptn.split('|'), patterns[1:]), key=itemgetter(1), reverse=True)

    all_pat.append([[main, total_count]] + items)

# 不同組 pattern 排序
all_pat = sorted(all_pat, key=lambda x: x[1][1]) # 抓 index = 1 的 count

for pats in all_pat:
    main, total_count = pats[0]
    
    print("{} {}".format(main, total_count))
    for p, count in pats[1:]:
        print("{}: [{}, {}]".format(p, count, int(count)/int(total_count)))
    print("="*50)
