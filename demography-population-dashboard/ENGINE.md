# Vital Stats Suite — Core Demographic Engine Reference Manual (`ENGINE.md`)

This document serves as the authoritative mathematical, demographic, and statistical reference for the 22 demographic measures and data quality checks implemented in the `engine/` package.

---

## 1. Data Quality Module

### 1.1 Whipple's Index ($W$)
Evaluates terminal digit preference for digits `0` and `5` in reported single-year age data in the adult range (ages 23 to 62 inclusive).

$$\text{Whipple's Index} = \frac{\sum_{x=25, 30, \dots, 60} P_x}{\frac{1}{5} \sum_{y=23}^{62} P_y} \times 100$$

- **Theoretical Basis**: Under uniform distribution, exactly $20\%$ of individuals aged 23–62 should report an age ending in 0 or 5 ($W = 100$).
- **UN Quality Scale**:
  - $< 105$: Highly accurate
  - $105 - 109.9$: Fairly accurate
  - $110 - 124.9$: Approximate
  - $125 - 174.9$: Rough
  - $\ge 175$: Very rough
- **Citation**: United Nations (1955). *Manual II: Methods of Appraisal of Quality of Basic Data for Population Estimates*, ST/SOA/Series A/23.

### 1.2 Myers' Blended Index ($M$)
Evaluates digit attraction across all 10 digits ($0, 1, 2, \dots, 9$) over ages 10 to 69 by applying linear weights to eliminate the confounding effect of natural population decline with age.

$$M = \frac{1}{2} \sum_{d=0}^{9} \left| \%_d - 10.0\% \right|$$

- **Theoretical Range**: $0$ (no preference) to $90$ (all population clustered on one digit).
- **Quality Scale**: $< 5$ (Low preference), $5-10$ (Moderate), $10-20$ (Substantial), $> 20$ (Severe age heaping).
- **Citation**: Myers, R. J. (1940). *Errors and Bias in the Reporting of Ages in Census Data*. TASA, 41: 395–415.

### 1.3 Post-Enumeration Check (PEC) & Dual-System Estimation
Evaluates under-enumeration and net coverage error via dual-system estimation (Chandra-Deming formula):

$$N_{\text{true}} = \frac{N_{\text{census}} \times N_{\text{PEC}}}{M_{\text{matched}}}$$
$$\text{Omission Rate } (O) = \frac{N_{\text{true}} - N_{\text{census}}}{N_{\text{true}}}, \quad \text{Completeness } (C) = 1 - O$$
$$\text{Coverage Adjustment Multiplier } (k) = \frac{1}{C}$$

- **Citation**: Chandrasekaran, C., & Deming, W. E. (1949). *On a Method of Estimating Birth and Death Rates and the Extent of Registration*. JASA, 44(245): 101–115.

---

## 2. Block A: Sex Composition (3 Measures)

### 1. Masculinity Proportion (MP)
Percentage of the total population that is male.

$$\text{MP} = \left( \frac{P_m}{P_t} \right) \times 100$$

- **Standard Range**: $49.5\% - 51.5\%$.
- **Citation**: Shryock, H. S., & Siegel, J. S. (1976). *The Methods and Materials of Demography*, Ch. 7.

### 2. Sex Ratio (SR)
Number of males per 100 females in the population.

$$\text{SR} = \left( \frac{P_m}{P_f} \right) \times 100$$

- **Standard Range**: $95 - 105$ males per 100 females (Biological Sex Ratio at Birth $\approx 105$).
- **Citation**: United Nations Demographic Yearbook; Shryock & Siegel (1976).

### 3. Excess of Males ($E_m$)
The absolute count and relative percentage difference between male and female populations.

$$E_m = P_m - P_f, \quad \% E_m = \left( \frac{P_m - P_f}{P_t} \right) \times 100$$

- **Citation**: Bhende, A., & Kanitkar, T. (2010). *Principles of Population Studies*, Ch. 5.

---

## 3. Block B: Age Composition & Dependency (4 Measures)

### 4. Age Composition Ratio (ACR)
Proportion of total population in functional life stages:
- **Young Age Share (0–14)**: $\text{ACR}_{0-14} = (P_{0-14} / P_t) \times 100$
- **Working Age Share (15–64)**: $\text{ACR}_{15-64} = (P_{15-64} / P_t) \times 100$
- **Elderly Share (65+)**: $\text{ACR}_{65+} = (P_{65+} / P_t) \times 100$

- **Demographic Dividend Window**: Occurs when $\text{ACR}_{15-64} \ge 60\% - 65\%$.
- **Citation**: Rowland, D. T. (2003). *Demographic Methods and Concepts*, Oxford University Press.

### 5. Total Dependency Ratio (TDR)
Total dependent population (children + elderly) per 100 working-age individuals.

$$\text{TDR} = \left( \frac{P_{0-14} + P_{65+}}{P_{15-64}} \right) \times 100$$

- **Global Benchmark**: $< 50$ (Favorable demographic dividend); $> 70$ (Heavy economic burden).
- **Citation**: UN DESA Population Division; World Bank World Development Indicators.

### 6. Child Dependency Ratio ($\text{CDR}_{\text{child}}$)
Children (0–14) per 100 working-age individuals.

$$\text{CDR}_{\text{child}} = \left( \frac{P_{0-14}}{P_{15-64}} \right) \times 100$$

- **Citation**: Bhende & Kanitkar (2010), Ch. 5.

### 7. Old-Age Dependency Ratio (OADR)
Elderly individuals (65+) per 100 working-age individuals.

$$\text{OADR} = \left( \frac{P_{65+}}{P_{15-64}} \right) \times 100$$

- **Aging Benchmark**: $> 20$ (Aging society); $> 35$ (Hyper-aged society).
- **Citation**: OECD Social Indicators; UN Population Division.

---

## 4. Block C: Fertility (7 Measures)

### 8. Crude Birth Rate (CBR)
Annual live births per 1,000 mid-year population.

$$\text{CBR} = \left( \frac{B}{P} \right) \times 1,000$$

- **Citation**: Preston, S. H., Heuveline, P., & Guillot, M. (2001). *Demography: Measuring and Modeling Population Processes*, Ch. 5.

### 9. Marital Birth Rate (MBR / GMFR)
Annual births to married women per 1,000 married women of reproductive age (15–49).

$$\text{MBR} = \left( \frac{B_{\text{marital}}}{W_{\text{married}, 15-49}} \right) \times 1,000$$

- **Citation**: Newell, C. (1988). *Methods and Models in Demography*, Ch. 4.

### 10. General Fertility Rate (GFR)
Annual live births per 1,000 women of reproductive age (15–49).

$$\text{GFR} = \left( \frac{B}{W_{15-49}} \right) \times 1,000$$

- **Citation**: Shryock & Siegel (1976), Ch. 16.

### 11. Age-Specific Fertility Rate (ASFR)
Annual live births to women in a 5-year age group $i$ per 1,000 women in that age group.

$$\text{ASFR}_i = \left( \frac{B_i}{W_i} \right) \times 1,000$$

- **Citation**: Preston et al. (2001), Ch. 5.

### 12. Total Fertility Rate (TFR)
Average number of children a hypothetical woman would bear over her reproductive lifetime if subject to current age-specific fertility schedules.

$$\text{TFR} = \frac{n \times \sum_{i=1}^{7} \text{ASFR}_i}{1,000} = 5 \times \sum_{i=1}^{7} \left( \frac{B_i}{W_i} \right)$$

- **Replacement Level**: $\approx 2.1$ children per woman in low-mortality environments.
- **Citation**: UN DESA Population Division; Preston et al. (2001).

### 13. Gross Reproduction Rate (GRR)
Average number of female daughters a woman would bear over her lifetime assuming no maternal mortality before the end of the reproductive period.

$$\text{GRR} = \text{TFR} \times \left( \frac{B_f}{B_t} \right) \approx \text{TFR} \times 0.4878$$

- **Citation**: Preston et al. (2001), Ch. 5; Rowland (2003).

### 14. Net Reproduction Rate (NRR)
Average number of daughters a newborn female would bear over her lifetime, accounting for mortality prior to and during reproductive ages.

$$\text{NRR} = \sum_{i=1}^{7} \left( \text{ASFR}_{f, i} \times \frac{{}_5L_{x_i}}{5 \times l_0} \right) \approx \text{GRR} \times p_s$$

- **Exact Replacement**: $\text{NRR} = 1.00$. ($\text{NRR} > 1$ denotes long-term population growth; $\text{NRR} < 1$ denotes contraction).
- **Citation**: Preston et al. (2001), Ch. 5; Bhende & Kanitkar (2010).

---

## 5. Block D: Mortality & Standardization (8 Measures)

### 15. Crude Death Rate (CDR)
Annual deaths per 1,000 mid-year population.

$$\text{CDR} = \left( \frac{D}{P} \right) \times 1,000$$

- **Citation**: Preston et al. (2001), Ch. 2.

### 16. Corrected Crude Death Rate
Mortality rate adjusted for vital registration undercount and PEC completeness.

$$\text{Corrected CDR} = \frac{\text{CDR}}{C} = \frac{\text{CDR}}{1 - O}$$

- **Citation**: Bennett, N. G., & Horiuchi, S. (1981). *Estimating the Completeness of Death Registration in a Closed Population*. Population Index, 47(2): 207–221.

### 17. Neonatal Mortality Rate (NMR)
Deaths within the first 28 days of life per 1,000 live births.

$$\text{NMR} = \left( \frac{D_{<28\text{ days}}}{B} \right) \times 1,000$$

- **SDG Target 3.2**: $\le 12.0$ per 1,000 live births.
- **Citation**: World Health Organization (WHO) Global Health Observatory.

### 18. Infant Mortality Rate (IMR)
Deaths under 1 year of age per 1,000 live births.

$$\text{IMR} = \left( \frac{D_{<1\text{ year}}}{B} \right) \times 1,000$$

- **Citation**: UNICEF / WHO Child Mortality Standards; Preston et al. (2001).

### 19. Child Mortality Rate (CMR / U5MR)
- **Age 1–4 Specific Mortality**: $\text{CMR}_{1-4} = (D_{1-4} / P_{1-4}) \times 1,000$
- **Under-5 Mortality Rate (U5MR)**: $\text{U5MR} = (D_{<5} / B) \times 1,000$
- **SDG Target 3.2.1**: $\le 25.0$ per 1,000 live births.
- **Citation**: UN Inter-agency Group for Child Mortality Estimation (UN IGME).

### 20. Age-Specific Death Rate (ASDR)
Annual deaths in age group $i$ per 1,000 mid-year population in age group $i$.

$$\text{ASDR}_i = \left( \frac{D_i}{P_i} \right) \times 1,000$$

- **Citation**: Preston et al. (2001), Ch. 2.

### 21. Direct Standardized Death Rate (DSDR)
Age-adjusted death rate obtained by applying the study population's age-specific death rates to a standard reference population (e.g. WHO Standard World Population 2000–2025).

$$\text{DSDR} = \frac{\sum_{i} \left( \text{ASDR}_i \times P^{\text{std}}_i \right)}{\sum_i P^{\text{std}}_i}$$

- **Citation**: World Health Organization (WHO) Age Standardization Standards; Preston et al. (2001).

### 22. Standardized Mortality Ratio (SMR) & Indirect Standardized Death Rate (ISDR)
Compares observed deaths in the study population to expected deaths under standard age-specific death rates.

$$\text{Expected Deaths } (E) = \sum_{i} \left( \frac{P_i \times \text{ASDR}^{\text{std}}_i}{1,000} \right)$$
$$\text{SMR} = \frac{D_{\text{observed}}}{E}, \quad \text{ISDR} = \text{SMR} \times \text{CDR}^{\text{std}}$$

- **Reconciliation Property**: When the study population is identical in age distribution and rates to the standard population, $\text{SMR} = 1.00$ and $\text{DSDR} = \text{ISDR} = \text{CDR}^{\text{std}}$.
- **Citation**: Breslow, N. E., & Day, N. E. (1987). *Statistical Methods in Cancer Research*, IARC Scientific Publications.
