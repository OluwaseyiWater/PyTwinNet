## Propagation & Link Budget
$\mathrm{FSPL}(d, f) = 20\log_{10}(d) + 20\log_{10}(f) - 147.55$

## Received Power
$P_{rx} = P_{tx} + G_t + G_r - \mathrm{FSPL}(d,f)$

## SINR
$\mathrm{SINR}_j = \frac{S_{s,j}}{\sum_{i\in\mathcal{I}} S_{i,j} + N_0B}$

## Throughput
$R_j = \eta B \log_2(1+\mathrm{SINR}_j)$

