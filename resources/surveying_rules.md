# Geomatics Principles for Norwegian Land Surveying (FKB Context)

This document summarizes key concepts from Norwegian land surveying ("Landmåling") relevant for processing and validating FKB data.

## 1. Coordinate Systems & Datums 

* **Official Horizontal Datum:** **EUREF89** is the standard geodetic datum for Norway, based on the ETRS89 system. It uses the **GRS80 ellipsoid**.
* **Official Vertical Datum:** **NN2000** (Normal Null 2000) is the official height system, providing **normal heights** relative to a defined zero-level (null geoide). This is the required height reference for FKB data (`..VERT-DATUM NN2000`).
* **Map Projection:** **UTM (Universal Transverse Mercator)** is the standard map projection used with EUREF89 for FKB data.
    * **Norway Zones:** Primarily uses UTM zones **32, 33, and 35** depending on location. Zone 32 is extended westwards.
    * **Coordinates:** UTM provides planar coordinates (**N** for Northing, **E** for Easting) in meters. Easting includes a **false easting of 500,000m**. Northing is meters from the equator.
* **Alternative Projection (NTM):** EUREF89 NTM (Norsk Transversal Mercator) exists mainly for construction projects to minimize scale distortion, using a scale factor of 1.0 at the central meridian. Data might be delivered in NTM but usually needs **conversion to UTM** for official FKB delivery.
* **Height Types:**
    * **Ellipsoidal Height (h):** Height above the GRS80 ellipsoid, typically measured by GNSS.
    * **Normal Height (Hn):** Height above the quasi-geoid (used in NN2000), related to gravity potential.
    * **Orthometric Height (H):** Height above the geoid (mean sea level). NN1954 used heights approximating this.
    * **Geoid Height (N):** The separation between the ellipsoid and the geoid (`h = H + N`). Required for converting GNSS heights to FKB-compliant heights.

## 2. Map Projection Corrections 

Measurements made on the physical Earth (distances, angles) need correction when represented on the flat UTM map projection plane.

* **Distance Correction:** A distance measured on the ground (`Ds`) must be corrected for:
    1.  **Height:** Reduced to the ellipsoid surface (`De`).
    2.  **Projection:** Scaled to the UTM plane (`Dk`).
    * **UTM Scale Factor:** UTM uses a central meridian scale factor of **k0 = 0.9996**. Distances *increase* as you move away from the central meridian. The formula for converting ellipsoid distance (`De`) to map distance (`Dk`) in UTM is approximately:
        `Dk = De * k0 * (1 + (y1^2 + y1*y2 + y2^2) / (6 * R^2))` where y1, y2 are distances from the central meridian and R is Earth radius.
* **Direction Correction (Meridian Convergence):** Angles measured relative to true North (azimuth) differ from angles relative to grid North (retningsvinkel) in UTM, except on the central meridian. Measured directions (`r`) must be corrected (`rk = r + ∆r`) to get grid bearings. The correction `∆r` depends on position within the UTM zone.

## 3. Measurement Principles & Accuracy 

* **Standard Angular Unit:** **Gon (Gradian)** is the standard unit for angles in Norwegian land surveying. 400 gon = 360 degrees.
* **Measurement Redundancy ("Overbestemmelser"):** Measurements should always include redundancy (more measurements than strictly necessary) to allow for error detection and quality assessment.
* **Least Squares Adjustment:** This is the standard mathematical method for calculating the most probable coordinates from redundant measurements, minimizing the sum of squared residuals (`Σv^2`).
* **Weighting:** Measurements are weighted in adjustments based on their precision (inversely proportional to variance, `p = σ0^2 / σ^2`).
* **Error Propagation:** The law of error propagation (`Σzz = AΣAT`) is used to calculate the accuracy (standard deviation, error ellipses) of computed coordinates based on measurement accuracy.
* **Gross Error Detection ("Grovfeilsøk"):** Statistical tests (like the t-test on residuals) are used to identify and remove blunders from measurements before final adjustment.
* **Total Station Corrections:** Total station measurements require corrections for atmospheric conditions (temperature, pressure affecting EDM speed), prism constants, Earth curvature, and atmospheric refraction (k-factor).

## 4. Relevant Tools & Techniques

* **Coordinate Calculation Methods :** Polar calculation (distance+angle), intersection (framskjæring), resection (tilbakeskjæring), trilateration (distances only).
* **Height Measurement (Chapter 9):** Leveling (nivellement) for high precision, trigonometric heighting with total stations. Trigonometric heighting requires curvature and refraction corrections.
* **GNSS :** Explains GPS, Glonass, Galileo; coordinate systems (WGS84 vs EUREF89); measurement types (code vs phase); error sources (atmosphere, multipath); differential techniques (RTK, CPOS) for cm-accuracy. Explains conversion from ellipsoidal height (GNSS) to orthometric/normal height using a geoid model.