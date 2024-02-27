# https://keisan.casio.jp/exec/user/1490184062
from scipy import stats
total = 1732
m = 48
t = 46
observed = [total - m - t, m, t] 
expected = [total * 0.94, total * 0.03, total * 0.03] 
print([a / total for a in observed])
result = stats.chisquare(observed, expected)
print(result)
