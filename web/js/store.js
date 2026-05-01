// Tiny localStorage-backed store for profiles + measurements.
// Schema:
//   { profiles: [ { id, name, sex, dob, measurements: [ { id, date, weight?, length?, head? } ] } ] }

const KEY = 'growth-tracker-v1';

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

function read() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return { profiles: [] };
    const parsed = JSON.parse(raw);
    if (!parsed || !Array.isArray(parsed.profiles)) return { profiles: [] };
    return parsed;
  } catch (_e) {
    return { profiles: [] };
  }
}

function write(state) {
  localStorage.setItem(KEY, JSON.stringify(state));
}

export function listProfiles() {
  return read().profiles.slice().sort((a, b) => a.name.localeCompare(b.name));
}

export function getProfile(id) {
  return read().profiles.find((p) => p.id === id) || null;
}

export function createProfile({ name, sex, dob }) {
  const state = read();
  const profile = {
    id: uid(),
    name: name.trim(),
    sex,
    dob,
    measurements: [],
  };
  state.profiles.push(profile);
  write(state);
  return profile;
}

export function updateProfile(id, patch) {
  const state = read();
  const profile = state.profiles.find((p) => p.id === id);
  if (!profile) return null;
  Object.assign(profile, patch);
  write(state);
  return profile;
}

export function deleteProfile(id) {
  const state = read();
  state.profiles = state.profiles.filter((p) => p.id !== id);
  write(state);
}

export function addMeasurement(profileId, entry) {
  const state = read();
  const profile = state.profiles.find((p) => p.id === profileId);
  if (!profile) return null;
  const measurement = { id: uid(), ...entry };
  profile.measurements.push(measurement);
  profile.measurements.sort((a, b) => a.date.localeCompare(b.date));
  write(state);
  return measurement;
}

export function deleteMeasurement(profileId, measurementId) {
  const state = read();
  const profile = state.profiles.find((p) => p.id === profileId);
  if (!profile) return;
  profile.measurements = profile.measurements.filter((m) => m.id !== measurementId);
  write(state);
}

// Age in months between two ISO date strings (YYYY-MM-DD).
// Uses a fractional-month approximation (days / 30.4375).
export function ageInMonths(dobIso, dateIso) {
  const dob = new Date(`${dobIso}T00:00:00`);
  const date = new Date(`${dateIso}T00:00:00`);
  const ms = date - dob;
  if (Number.isNaN(ms)) return null;
  return ms / (1000 * 60 * 60 * 24 * 30.4375);
}

export function formatAge(months) {
  if (months == null || Number.isNaN(months)) return '';
  if (months < 0) return 'before birth';
  const totalDays = months * 30.4375;
  if (totalDays < 31) return `${Math.round(totalDays)}d`;
  const whole = Math.floor(months);
  const y = Math.floor(whole / 12);
  const m = whole % 12;
  if (y === 0) return `${m}m`;
  if (m === 0) return `${y}y`;
  return `${y}y ${m}m`;
}

// --- export / import ------------------------------------------------------

export const EXPORT_SCHEMA = 'growth-tracker-v1';

export function exportState() {
  const state = read();
  return {
    schema: EXPORT_SCHEMA,
    exportedAt: new Date().toISOString(),
    profiles: state.profiles,
  };
}

// Validate and normalize an imported payload. Accepts either the full
// export object or a bare profiles array. Throws on invalid input.
function normalizeImport(payload) {
  let profiles;
  if (Array.isArray(payload)) {
    profiles = payload;
  } else if (payload && Array.isArray(payload.profiles)) {
    profiles = payload.profiles;
  } else {
    throw new Error('File does not contain a "profiles" array.');
  }
  return profiles.map((p, i) => {
    if (!p || typeof p !== 'object') throw new Error(`Profile #${i + 1} is not an object.`);
    if (typeof p.name !== 'string' || !p.name.trim()) throw new Error(`Profile #${i + 1} is missing a name.`);
    if (p.sex !== 'female' && p.sex !== 'male') throw new Error(`Profile "${p.name}" has invalid sex.`);
    if (typeof p.dob !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(p.dob)) {
      throw new Error(`Profile "${p.name}" has invalid date of birth.`);
    }
    const measurements = Array.isArray(p.measurements) ? p.measurements : [];
    return {
      name: p.name.trim(),
      sex: p.sex,
      dob: p.dob,
      measurements: measurements
        .filter((m) => m && /^\d{4}-\d{2}-\d{2}$/.test(m.date))
        .map((m) => ({
          date: m.date,
          weight: numOrNull(m.weight),
          length: numOrNull(m.length),
          head: numOrNull(m.head),
        })),
    };
  });
}

function numOrNull(v) {
  if (v == null || v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

// mode: 'replace' wipes existing data; 'merge' keeps existing and appends imports.
// Imported records always receive fresh ids to avoid collisions.
export function importProfiles(payload, mode = 'merge') {
  const incoming = normalizeImport(payload);
  const state = mode === 'replace' ? { profiles: [] } : read();
  incoming.forEach((p) => {
    state.profiles.push({
      id: uid(),
      name: p.name,
      sex: p.sex,
      dob: p.dob,
      measurements: p.measurements
        .map((m) => ({ id: uid(), ...m }))
        .sort((a, b) => a.date.localeCompare(b.date)),
    });
  });
  write(state);
  return { count: incoming.length, mode };
}
