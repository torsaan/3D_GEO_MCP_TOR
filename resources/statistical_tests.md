# Statistical Tests in Adjustment Computations

After a least squares adjustment, statistical tests are crucial for validating the results and detecting potential errors in the measurements.

## 1. Global Test (Overall Goodness-of-Fit)

* **Purpose:** To check if the overall adjustment is statistically acceptable by comparing the estimated variance factor (` posteriori σ0^2`) with the assumed variance factor (` priori σ0^2`).
* **Test Statistic:** Often uses the Chi-squared (`χ^2`) distribution. The statistic is calculated as `T = (df * posteriori_σ0^2) / priori_σ0^2`, where `df` is the degrees of freedom (redundancy = number of observations - number of unknowns) .
    * `posteriori_σ0^2 = (VT * P * V) / df` . `VT*P*V` is the weighted sum of squared residuals.
* **Hypothesis:**
    * H0: The adjustment fits the mathematical model and ` priori σ0^2` is correct.
    * H1: The adjustment does not fit, possibly due to model errors or incorrect weighting/outliers.
* **Decision:** Compare `T` against critical values from the `χ^2` distribution with `df` degrees of freedom at a chosen significance level (e.g., α = 0.05). If `T` falls outside the acceptance region (typically `T > χ^2(1-α/2, df)` or `T < χ^2(α/2, df)`), H0 is rejected.

## 2. Outlier Detection (Gross Error Search - Chapter 22)

* **Purpose:** To identify individual observations that contain blunders (gross errors) inconsistent with the random error model [
* **Method:** Commonly uses statistical tests on the **residuals (v)** or **standardized residuals**.
* **Standardized Residual (w):** `wi = vi / σvi`, where `σvi` is the standard deviation of the residual `vi`. This requires the covariance matrix of the residuals (`Σvv = σ0^2 * Qvv`, where `Qvv = P^-1 - A * (AT P A)^-1 * AT`).
* **Data Snooping (Baarda's Method):** Tests each observation individually.
    * Calculate standardized residuals for all observations.
    * Compare the *largest* absolute standardized residual (`|w_max|`) against a critical value from the Tau (`τ`) distribution or the standard normal distribution (adjusted for multiple tests, e.g., using Bonferroni correction) .
    * If `|w_max|` exceeds the critical value, the corresponding observation is flagged as a potential outlier.
    * **Procedure:** Remove the worst outlier, re-run the adjustment, and repeat the test until no more outliers are detected .
* **Alternative (t-test on Estimated Blunder - ∇):** As described in the PDF, estimate the size of the blunder (`∇` or `gf`) for each observation by adding an extra parameter to the adjustment. Calculate its standard deviation (`s_gf`). The test statistic is `t = gf / s_gf`. Compare `t` to a critical value from the t-distribution (adjusted for multiple tests) [.

## 3. Reliability (Chapter 23)

* **Purpose:** To assess the network's ability to detect gross errors (internal reliability) and how much an undetected error might affect the final coordinates (external reliability)[cite: 3468].
* **Internal Reliability (MDB - Marginally Detectable Blunder):** The smallest gross error in an observation that *can* be detected by the statistical test with a certain probability (related to `σvi` and critical test values) .
* **External Reliability:** The effect of an undetected MDB (from internal reliability) on the computed parameters (e.g., coordinates) . Calculated by propagating the effect of the MDB through the adjustment using the design matrix `A` and the normal matrix inverse `Q` (`(AT P A)^-1`) .

**Significance Level (α):** Commonly set to 0.01 or 0.05 (1% or 5%). This represents the probability of incorrectly rejecting a true hypothesis (Type I error).