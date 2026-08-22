/* Aster selected-UI v1.1 integration example. Documentation, not a drop-in patch. */

const orbitEntries = require('./default-registry.json').orbitEntries;

orbitEntries.forEach((entry) => {
  Aster.dashboard.registerOrbit(entry.id, entry);
});

// registerOrbitEntry(id, def) and unregisterOrbitEntry(id) are compatibility
// aliases for registerOrbit/unregisterOrbit. Do not call both registration
// names for the same id. activeId is the stable identity; index is derived
// from the ring's current sorted entries and may change after registration.
const orbitState = Aster.dashboard.state().orbits;
void orbitState.inner.activeId;
void orbitState.inner.index;

// Existing API remains a facade for outer-ring compatibility only.
Aster.dashboard.registerRoute('mod-weather', {
  label: '世界天气',
  iconAssetId: 'ui.icon.weather',
  order: 80,
  panel: 'world-weather'
});

// The renderer must still expose exactly two rings. The new route rotates into
// the outer ring from the hidden/back-side buffer; it never creates a new rail.

Aster.social.registerSection('calendar', {
  label: '日历',
  title: '世界日历',
  presentation: 'calendar',
  iconAssetId: 'ui.icon.calendar',
  order: 40,
  pageSize: 6,
  searchFields: ['title', 'summary', 'tag']
});

Aster.social.registerEntry('calendar:new-moon', {
  section: 'calendar',
  title: '新月观测夜',
  summary: '星轨旅人的世界日历事件。',
  timestamp: 1767301200000,
  iconAssetId: 'ui.icon.calendar',
  unread: 0,
  followed: true,
  online: false,
  kind: 'calendar-event',
  status: 'scheduled'
});

// Section registration appends to the same vertical rail. It must not create
// a mobile bottom tab or another global application entry. Custom presentation
// ids use their registered presenter when available and the shared generic
// index/detail presenter otherwise.
