# RQ3 Cross-Scale (1M vs 8M) — 5/7 03:55

> 5 common method × 2 sel ([0.1, 0.3]) × 2 scale (1M, 8M) = 측정값 비교

## 1M vs 8M mean q_error

| method | sel | 1M mean | 8M mean | Δ (8M-1M) | Δ% |
|--------|-----|--------:|--------:|----------:|---:|
| hilbert | 0.1 | 1.1313 | 1.1175 | -0.0137 | -1.21% |
| lsh | 0.1 | 1.1721 | 1.1576 | -0.0144 | -1.23% |
| minibatch | 0.1 | 1.1376 | 1.1185 | -0.0191 | -1.68% |
| random_proj | 0.1 | 1.2118 | 1.1713 | -0.0405 | -3.34% |
| zorder | 0.1 | 1.1270 | 1.1289 | +0.0019 | +0.17% |
| hilbert | 0.3 | 1.0628 | 1.0549 | -0.0078 | -0.74% |
| lsh | 0.3 | 1.0865 | 1.0784 | -0.0080 | -0.74% |
| minibatch | 0.3 | 1.0632 | 1.0579 | -0.0053 | -0.50% |
| random_proj | 0.3 | 1.1101 | 1.0818 | -0.0283 | -2.55% |
| zorder | 0.3 | 1.0580 | 1.0570 | -0.0010 | -0.09% |

## 해석

- 8M q_error 가 1M 보다 일관되게 작으면 → 큰 데이터에서 sampling 정확도 향상 (cardinality estimation 의 자연 안정화).
- method 간 ranking 이 1M / 8M 에서 일치하면 → 본 연구의 method 우수성 결론이 cross-scale robust.
- 차이 큰 method 가 있으면 → scale-dependent 효과, future work 의 명시적 limitation.