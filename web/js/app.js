// Main UI controller: profiles, measurements, view state, chart wiring.
import {
  listProfiles, getProfile, createProfile, updateProfile, deleteProfile,
  addMeasurement, deleteMeasurement, ageInMonths, formatAge,
  exportState, importProfiles,
} from './store.js';
import { renderCharts, clearCharts } from './charts.js';

const els = {
  profileList:    document.getElementById('profile-list'),
  newProfileBtn:  document.getElementById('btn-new-profile'),
  profileForm:    document.getElementById('profile-form'),
  profileFormTitle: document.getElementById('profile-form-title'),
  cancelProfile:  document.getElementById('btn-cancel-profile'),
  detail:         document.getElementById('profile-detail'),
  emptyState:     document.getElementById('empty-state'),
  detailName:     document.getElementById('detail-name'),
  detailMeta:     document.getElementById('detail-meta'),
  editBtn:        document.getElementById('btn-edit-profile'),
  deleteBtn:      document.getElementById('btn-delete-profile'),
  measurementForm: document.getElementById('measurement-form'),
  entriesBody:    document.querySelector('#entries-table tbody'),
  entriesTable:   document.getElementById('entries-table'),
  entriesEmpty:   document.getElementById('entries-empty'),
  exportBtn:      document.getElementById('btn-export'),
  importBtn:      document.getElementById('btn-import'),
  importFile:     document.getElementById('import-file'),
};

let activeId = null;
let editingId = null;

function renderProfileList() {
  const profiles = listProfiles();
  els.profileList.innerHTML = '';
  if (!profiles.length) {
    const li = document.createElement('li');
    li.className = 'empty';
    li.textContent = 'No profiles yet.';
    els.profileList.appendChild(li);
    return;
  }
  profiles.forEach((p) => {
    const li = document.createElement('li');
    li.dataset.id = p.id;
    if (p.id === activeId) li.classList.add('active');
    li.innerHTML =
      `<strong>${escapeHtml(p.name)}</strong>` +
      `<span class="meta">${p.sex === 'female' ? '♀' : '♂'} · DOB ${p.dob}</span>`;
    li.addEventListener('click', () => selectProfile(p.id));
    els.profileList.appendChild(li);
  });
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => (
    { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
  ));
}

function selectProfile(id) {
  activeId = id;
  const profile = getProfile(id);
  if (!profile) {
    showEmptyState();
    return;
  }
  els.detail.hidden = false;
  els.emptyState.hidden = true;
  els.detailName.textContent = profile.name;
  els.detailMeta.textContent =
    `${profile.sex === 'female' ? 'Female' : 'Male'} · DOB ${profile.dob}` +
    ` · current age ${formatAge(ageInMonths(profile.dob, todayIso()))}`;
  renderProfileList();
  renderEntries(profile);
  els.measurementForm.querySelector('input[name="date"]').value = todayIso();
  renderCharts(profile);
}

function showEmptyState() {
  activeId = null;
  els.detail.hidden = true;
  els.emptyState.hidden = false;
  clearCharts();
  renderProfileList();
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function renderEntries(profile) {
  els.entriesBody.innerHTML = '';
  if (!profile.measurements.length) {
    els.entriesTable.hidden = true;
    els.entriesEmpty.hidden = false;
    return;
  }
  els.entriesTable.hidden = false;
  els.entriesEmpty.hidden = true;
  const rows = profile.measurements.slice().reverse();
  rows.forEach((m) => {
    const tr = document.createElement('tr');
    const ageM = ageInMonths(profile.dob, m.date);
    tr.innerHTML =
      `<td>${m.date}</td>` +
      `<td>${formatAge(ageM)}</td>` +
      `<td class="num">${fmt(m.weight)}</td>` +
      `<td class="num">${fmt(m.length)}</td>` +
      `<td class="num">${fmt(m.head)}</td>` +
      `<td><button class="row-del" data-id="${m.id}">Delete</button></td>`;
    els.entriesBody.appendChild(tr);
  });
  els.entriesBody.querySelectorAll('button.row-del').forEach((btn) => {
    btn.addEventListener('click', () => {
      deleteMeasurement(activeId, btn.dataset.id);
      selectProfile(activeId);
    });
  });
}

function fmt(v) {
  return v == null || v === '' ? '—' : Number(v).toFixed(2);
}

// --- profile form ---------------------------------------------------------

function openProfileForm(profile) {
  editingId = profile ? profile.id : null;
  els.profileForm.hidden = false;
  els.profileFormTitle.textContent = profile ? 'Edit profile' : 'New profile';
  els.profileForm.elements.name.value = profile ? profile.name : '';
  els.profileForm.elements.sex.value = profile ? profile.sex : 'female';
  els.profileForm.elements.dob.value = profile ? profile.dob : '';
  els.profileForm.elements.name.focus();
}

function closeProfileForm() {
  editingId = null;
  els.profileForm.hidden = true;
  els.profileForm.reset();
}

els.newProfileBtn.addEventListener('click', () => openProfileForm(null));
els.cancelProfile.addEventListener('click', closeProfileForm);

els.profileForm.addEventListener('submit', (ev) => {
  ev.preventDefault();
  const fd = new FormData(els.profileForm);
  const data = { name: fd.get('name'), sex: fd.get('sex'), dob: fd.get('dob') };
  let profile;
  if (editingId) {
    profile = updateProfile(editingId, data);
  } else {
    profile = createProfile(data);
  }
  closeProfileForm();
  selectProfile(profile.id);
});

els.editBtn.addEventListener('click', () => {
  if (!activeId) return;
  openProfileForm(getProfile(activeId));
});

els.deleteBtn.addEventListener('click', () => {
  if (!activeId) return;
  const p = getProfile(activeId);
  if (!confirm(`Delete profile "${p.name}" and all its measurements?`)) return;
  deleteProfile(activeId);
  showEmptyState();
});

// --- measurement form -----------------------------------------------------

els.measurementForm.addEventListener('submit', (ev) => {
  ev.preventDefault();
  if (!activeId) return;
  const fd = new FormData(els.measurementForm);
  const entry = {
    date: fd.get('date'),
    weight: numOrNull(fd.get('weight')),
    length: numOrNull(fd.get('length')),
    head: numOrNull(fd.get('head')),
  };
  if (entry.weight == null && entry.length == null && entry.head == null) {
    alert('Enter at least one measurement.');
    return;
  }
  addMeasurement(activeId, entry);
  els.measurementForm.reset();
  els.measurementForm.elements.date.value = todayIso();
  selectProfile(activeId);
});

function numOrNull(v) {
  if (v === null || v === '') return null;
  const n = Number(v);
  return Number.isFinite(n) ? n : null;
}

// --- export / import -----------------------------------------------------

els.exportBtn.addEventListener('click', () => {
  const state = exportState();
  if (!state.profiles.length) {
    alert('No profiles to export.');
    return;
  }
  const blob = new Blob([JSON.stringify(state, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `growth-tracker-${state.exportedAt.slice(0, 10)}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});

els.importBtn.addEventListener('click', () => els.importFile.click());

els.importFile.addEventListener('change', async (ev) => {
  const file = ev.target.files && ev.target.files[0];
  els.importFile.value = '';
  if (!file) return;
  let payload;
  try {
    const text = await file.text();
    payload = JSON.parse(text);
  } catch (err) {
    alert(`Could not read file: ${err.message}`);
    return;
  }
  const hasExisting = listProfiles().length > 0;
  let mode = 'replace';
  if (hasExisting) {
    const replace = confirm(
      'Replace existing profiles with the imported file?\n\n' +
      'OK = replace all current data\n' +
      'Cancel = merge (keep existing and add imported)',
    );
    mode = replace ? 'replace' : 'merge';
  }
  try {
    const result = importProfiles(payload, mode);
    alert(`Imported ${result.count} profile(s) (${result.mode}).`);
  } catch (err) {
    alert(`Import failed: ${err.message}`);
    return;
  }
  const next = listProfiles()[0];
  if (next) selectProfile(next.id);
  else showEmptyState();
});

// --- bootstrap ------------------------------------------------------------

renderProfileList();
const initial = listProfiles()[0];
if (initial) selectProfile(initial.id);
else showEmptyState();
