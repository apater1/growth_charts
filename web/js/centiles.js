// LMS centile computation, mirroring girls_growth_charts.py
import {
  WEIGHT_LMS_GIRLS,
  LENGTH_LMS_GIRLS,
  HEAD_LMS_GIRLS,
} from './lms_data.js';

export const CENTILES = [0.4, 2, 9, 25, 50, 75, 91, 98, 99.6];
export const CENTILE_LABELS = [
  '0.4th', '2nd', '9th', '25th', '50th', '75th', '91st', '98th', '99.6th',
];

// Inverse standard-normal CDF (Acklam approximation) — accurate to ~1e-9.
function normInv(p) {
  if (p <= 0 || p >= 1) throw new Error('p out of range');
  const a = [-3.969683028665376e+01, 2.209460984245205e+02,
             -2.759285104469687e+02, 1.383577518672690e+02,
             -3.066479806614716e+01, 2.506628277459239e+00];
  const b = [-5.447609879822406e+01, 1.615858368580409e+02,
             -1.556989798598866e+02, 6.680131188771972e+01,
             -1.328068155288572e+01];
  const c = [-7.784894002430293e-03, -3.223964580411365e-01,
             -2.400758277161838e+00, -2.549732539343734e+00,
             4.374664141464968e+00, 2.938163982698783e+00];
  const d = [7.784695709041462e-03, 3.224671290700398e-01,
             2.445134137142996e+00, 3.754408661907416e+00];
  const pLow = 0.02425, pHigh = 1 - pLow;
  let q, r;
  if (p < pLow) {
    q = Math.sqrt(-2 * Math.log(p));
    return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) /
           ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
  } else if (p <= pHigh) {
    q = p - 0.5; r = q*q;
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q /
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
  } else {
    q = Math.sqrt(-2 * Math.log(1 - p));
    return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) /
            ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);
  }
}

// Standard-normal CDF via erf approximation (Abramowitz 7.1.26).
function normCdf(z) {
  const sign = z < 0 ? -1 : 1;
  const x = Math.abs(z) / Math.SQRT2;
  const t = 1 / (1 + 0.3275911 * x);
  const y = 1 - (((((1.061405429 * t - 1.453152027) * t)
                  + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t
                * Math.exp(-x * x);
  return 0.5 * (1 + sign * y);
}

export const CENTILE_ZSCORES = CENTILES.map((c) => normInv(c / 100));

// Value at z-score given LMS parameters (same formula as Python).
export function lmsValue(L, M, S, z) {
  if (Math.abs(L) < 1e-6) return M * Math.exp(S * z);
  return M * Math.pow(1 + L * S * z, 1 / L);
}

// Z-score for a measured value (inverse of lmsValue).
export function lmsZscore(L, M, S, value) {
  if (Math.abs(L) < 1e-6) return Math.log(value / M) / S;
  return (Math.pow(value / M, L) - 1) / (L * S);
}

// Centile (0–100) corresponding to a z-score.
export function zToCentile(z) {
  return normCdf(z) * 100;
}

// Linear interpolation of LMS row at an arbitrary age in months.
export function lmsAt(table, ageMonths) {
  const first = table[0], last = table[table.length - 1];
  if (ageMonths <= first[0]) return { L: first[1], M: first[2], S: first[3] };
  if (ageMonths >= last[0]) return { L: last[1], M: last[2], S: last[3] };
  for (let i = 0; i < table.length - 1; i += 1) {
    const a = table[i], b = table[i + 1];
    if (ageMonths >= a[0] && ageMonths <= b[0]) {
      const t = (ageMonths - a[0]) / (b[0] - a[0]);
      return {
        L: a[1] + t * (b[1] - a[1]),
        M: a[2] + t * (b[2] - a[2]),
        S: a[3] + t * (b[3] - a[3]),
      };
    }
  }
  return { L: last[1], M: last[2], S: last[3] };
}

// Build centile curves for plotting. Returns { ages, curves: { centile: [values] } }.
export function buildCurves(table) {
  const ages = table.map((row) => row[0]);
  const curves = {};
  CENTILES.forEach((c, idx) => {
    const z = CENTILE_ZSCORES[idx];
    curves[c] = table.map((row) => lmsValue(row[1], row[2], row[3], z));
  });
  return { ages, curves };
}

// The three reference tables, keyed by sex + measurement.
export const REFERENCE_TABLES = {
  female: {
    weight: WEIGHT_LMS_GIRLS,
    length: LENGTH_LMS_GIRLS,
    head: HEAD_LMS_GIRLS,
  },
};

export const MEASUREMENTS = [
  { key: 'weight', label: 'Weight', unit: 'kg', table: 'weight' },
  { key: 'length', label: 'Length / Height', unit: 'cm', table: 'length' },
  { key: 'head',   label: 'Head circumference', unit: 'cm', table: 'head' },
];
