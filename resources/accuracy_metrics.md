# Accuracy Metrics in Adjustment Computations

These metrics quantify the precision and correlation of the results obtained from a least squares adjustment.

## 1. Standard Deviation (σ)

* **Definition:** A measure of the dispersion or spread of random errors around the mean (most probable) value. Represents the precision of a measurement or a calculated parameter-
* **Calculation (for Adjusted Parameters):** Derived from the diagonal elements of the variance-covariance matrix (`Σxx`) of the adjusted parameters: `σ_xi = sqrt(Σxx[i, i])` .
* **Calculation (A Posteriori Variance Factor):** The standard deviation of an observation with weight 1, estimated *after* the adjustment: `σ0 = sqrt( (VT * P * V) / df )` .

## 2. Variance (σ^2)

* **Definition:** The square of the standard deviation (`σ^2`). Represents the average squared deviation from the mean. Used extensively in weighting (`p = σ0^2 / σ^2`) and error propagation 

## 3. Covariance (σxy or Σ)

* **Definition:** A measure of how two random variables change together.
    * **Positive Covariance:** Indicates variables tend to increase together.
    * **Negative Covariance:** Indicates one tends to increase as the other decreases.
    * **Zero Covariance:** Indicates no linear relationship (but not necessarily full independence).
* **Variance-Covariance Matrix (Σxx or Qxx):** A square matrix containing variances on the diagonal and covariances between pairs of parameters off the diagonal 
    * **Calculation:** `Σxx = σ0^2 * Qxx = σ0^2 * (AT P A)^-1`. `Qxx` is the cofactor matrix.
* **Importance:** Essential for understanding correlations between adjusted coordinates (e.g., how an error in Northing affects Easting) and for calculating error ellipses.

## 4. Correlation Coefficient (rxy)

* **Definition:** A *normalized* measure of the linear relationship between two variables, ranging from -1 to +1 
    * +1: Perfect positive linear correlation.
    * -1: Perfect negative linear correlation.
    * 0: No linear correlation.
* **Calculation:** `rxy = σxy / (σx * σy)`, where `σxy` is the covariance, and `σx`, `σy` are the standard deviations.

## 5. Error Ellipse (Chapter 18.2)

* **Purpose:** A graphical representation of the positional uncertainty (precision) of a calculated 2D point (e.g., Northing, Easting). It shows the region within which the true point lies with a certain probability (e.g., 95%).
* **Derivation:** Calculated from the 2x2 variance-covariance submatrix corresponding to the point's coordinates (`Σ_NE = [[σN^2, σNE], [σNE, σE^2]]`) .
* **Parameters:**
    * **Semi-major axis (a):** Length of the ellipse's longest radius (maximum error direction).
    * **Semi-minor axis (b):** Length of the ellipse's shortest radius (minimum error direction).
    * **Orientation (ϕa or θ):** The angle of the semi-major axis relative to the coordinate system's primary axis (e.g., North) 
* **Formulas:**
    * Orientation: `tan(2*ϕa) = 2 * σNE / (σN^2 - σE^2)` (adapted from `arctan` formula using Q matrix elements).
    * Semi-axes squared (`a^2`, `b^2`) are related to the eigenvalues of the covariance matrix `Σ_NE`.
        * `a^2 = (σN^2 + σE^2)/2 + sqrt( ((σN^2 - σE^2)/2)^2 + σNE^2 )` (scaled by confidence factor)
        * `b^2 = (σN^2 + σE^2)/2 - sqrt( ((σN^2 - σE^2)/2)^2 + σNE^2 )` (scaled by confidence factor)
        * Simplified formulas using Q matrix elements are also shown in.