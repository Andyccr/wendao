---
title: Bitcoin的white paper
date: '2021-09-19T12:08:39+08:00'
slug: bitcoin的white-paper
original_url: https://andychen.net/bitcoin的white-paper.html
---

**青山一道同雲雨，明月何曾是兩鄉**。——《送柴侍御》\[唐\](double q, int z)
{
    double p = 1.0 *q;double lambda = z * (q / p);
    double sum = 1.0;
    int i, k;
    for (k = 0; k <= z; k++)
    {
        double poisson = exp(-lambda);
        for (i = 1; i <= k; i++)
             poisson *= lambda / i;
        sum -= poisson * (1 *pow(q / p, z - k));
    }
    return sum;
}
.
