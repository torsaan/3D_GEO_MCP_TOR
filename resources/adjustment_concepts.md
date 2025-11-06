# Core Concepts of Least Squares Adjustment

This document summarizes fundamental principles from adjustment computations, primarily used in surveying and geomatics to find the best fit solution from redundant measurements.

## Least Squares Principle (Chapter 13)

* **Goal:** To find the most probable values for unknown parameters (e.g., coordinates) based on measurements that contain random errors[cite: 2930].
* **Overdetermined Systems:** Occurs when there are more observations (measurements) than unknown parameters[cite: 2931]. This redundancy allows for error checking and improved accuracy.
* **Minimization Criterion:** The method minimizes the sum of the squares of the weighted residuals (`Σ(p*v^2)` -> min) [cite: 2939-2941, 2963-2964].
* **Residual (v):** The difference between a measured value and its adjusted (most probable) value [cite: 2950-2951].

## Observation Equations (Chapters 14, 15, 16, 17, 18)

* **Definition:** Mathematical models that relate measured quantities (observations) to the unknown parameters.
* **Linear Form:** Often expressed in matrix form `A * X = L + V`, where:
    * `A`: Design matrix (coefficients derived from geometry/model) [cite: 2974-2975].
    * `X`: Vector of unknown parameters (e.g., coordinate adjustments `dx`, `dy`) [cite: 2974-2975].
    * `L`: Observation vector (measured values minus computed values based on approximate parameters) [cite: 2974-2975].
    * `V`: Residual vector [cite: 2974-2975].
* **Non-Linear Equations:** Many surveying problems (e.g., distances, angles) involve non-linear relationships. These must be **linearized** using Taylor series expansion around approximate values before adjustment [cite: 2994-2995, 3145-3149]. The adjustment then calculates corrections (`dx`, `dy`) to these approximate values, often requiring iterations [cite: 3180-3184].
* **Examples:**
    * Distance Observation: `sqrt((xj - xi)^2 + (yj - yi)^2) = lij + vij`[cite: 3145].
    * Direction/Angle Observation: `atan((yj-yi)/(xj-xi)) - Zi = rij + vij` [cite: 3216-3217, 3220-3223].
    * Leveling: `Hj - Hi = dHij + vij` [cite: 2997-2999].

## Weighting (Chapter 12)

* **Purpose:** To assign influence to observations based on their precision [cite: 2886-2887]. More precise measurements should have a greater impact on the solution.
* **Weight (p):** Inversely proportional to the variance (`σ^2`) of the observation: `pi = σ0^2 / σi^2` [cite: 2900-2901].
    * `σi^2`: Variance of observation `i`.
    * `σ0^2`: A priori variance factor (or variance of unit weight), an arbitrary constant used to scale the weights [cite: 2900-2901]. Often set based on the variance of a "standard" observation type (e.g., a direction measurement).
* **Weight Matrix (P):** For uncorrelated observations, this is a diagonal matrix with individual weights `pi` on the diagonal [cite: 2915-2917, 2927-2928]. If observations are correlated (like GNSS vector components), the full variance-covariance matrix (`Σ`) is used, and `P = σ0^2 * Σ^-1`.

## Solution (Matrix Form)

* **Normal Equations:** The least squares criterion leads to the matrix equation: `(AT * P * A) * X = AT * P * L`[cite: 2982].
* **Solution for Unknowns:** `X = (AT * P * A)^-1 * (AT * P * L)`[cite: 2982, 3016].
    * `N = AT * P * A` is the normal equation matrix.
    * `U = AT * P * L` is the constant vector.
    * `X = N^-1 * U`.