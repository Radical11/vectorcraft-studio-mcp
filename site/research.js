/* Read-only presentation of source-bound existing observations. No new ratings. */
'use strict';
const data = JSON.parse(document.querySelector('#stage-data').textContent);
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const repo = 'https://github.com/Radical11/vectorcraft-studio-mcp/blob/main/';
const profiles = ['designer-v1', 'layout-blockout-v1', 'designer-process-v1'];
let mode = 'within';
for (const t of data.trials) $('trial').add(new Option(`${t.short_id} · ${t.display_name}`, t.id));
$('trial').value = 'tyre-designer-process-v1-1';
const text = value => Array.isArray(value) ? value.join(' ') : String(value ?? '');
const checkList = value => Array.isArray(value) ? value : Object.entries(value || {}).map(([id, result]) => typeof result === 'object' ? {id, ...result} : {id, outcome: result});
function captureCard(c, trial, prefix = '') {
  if (!c) return `<article class="capture empty"><h3>${esc(prefix || data.profile_names[trial.condition])}</h3><p>${esc(trial.short_id)} · ${esc(trial.label)}</p><p>No capture for this stage. No substitute image is shown.</p></article>`;
  const image = c.images[$('size').value];
  const obs = c.observations;
  const notes = text(obs.observations || obs.decision || 'No confirmation observation recorded.');
  const checks = [...checkList(obs.check_results), ...checkList(obs.stage_checks)];
  const title = `${prefix ? prefix + ' · ' : ''}${c.title}`;
  const status = [c.confirmed ? 'Confirmed capture' : 'Unconfirmed capture', c.retained_best ? 'Retained best' : c.working ? 'Working at stop' : 'Historical capture'];
  if (c.task_outcome) status.push(`Task: ${c.task_outcome}`);
  if (c.stage_complete === true) status.push('Stage explicitly accepted');
  if (prefix) status.push(trial.label);
  const plan = c.plan;
  const next = !c.confirmed ? 'Inspect and confirm before accepting this capture.' : c.task_outcome === 'revise' ? 'Resolve the recorded finding in a planned correction.' : c.retained_best ? 'Retained version; consult the attempt outcome for final acceptance.' : 'Historical step; follow the later captures and recorded outcome.';
  return `<article class="capture">${image ? `<a class="image-link" href="${esc(image.site_path)}" target="_blank" rel="noopener"><img loading="lazy" src="${esc(image.site_path)}" alt="${esc(trial.display_name + ': ' + c.title + ', ' + $('size').value + ' capture')}"></a>` : '<div class="empty">This preview is unavailable.</div>'}<div class="body"><p class="step-label">${esc(c.step)} · ${esc(data.stages[c.stage].title)} · ${esc(c.progress_label)}</p><h3>${esc(title)}</h3><div class="badges">${status.map(s => `<span class="badge ${!c.confirmed || c.task_outcome === 'revise' ? 'warn' : ''}">${esc(s)}</span>`).join('')}</div><p><b>Change / check:</b> ${esc(c.change)}</p><p class="progress-reading"><b>Progress:</b> ${esc(c.reading)}</p><details><summary>Original observation, checks and source IDs</summary><p><b>Recorded observation:</b> ${esc(notes)}</p><p><b>Stage purpose:</b> ${esc(data.stages[c.stage].purpose)}</p><p><b>Original task:</b> ${esc(plan.goal || plan.purpose || 'See source checkpoint.')}</p>${plan.changes ? `<p><b>Planned change:</b> ${esc(plan.changes)}</p>` : ''}${plan.preserve ? `<p><b>Preserve:</b> ${esc(plan.preserve)}</p>` : ''}${checks.length ? `<ul>${checks.map(x => `<li><b>${esc(x.id)} — ${esc(x.outcome)}:</b> ${esc(x.observation || x.reason)}</li>`).join('')}</ul>` : '<p>No structured check results in this capture. Consult the source record.</p>'}${obs.reason ? `<p><b>Finding:</b> ${esc(obs.reason)}</p>` : ''}<p><b>Reading this state:</b> ${esc(next)}</p><p>${esc(obs.attribution)}</p><p>Source attempt: <code>${esc(trial.id)}</code>; version: <code>${esc(c.version)}</code>. Document revision ${esc(c.revision)}; specification revision ${esc(c.spec_revision)}. Stage and chronology come from recorded events.</p>${c.native ? `<p><a href="${repo + esc(c.native.path)}">Native source</a></p>` : ''}</details>${trial.report ? `<p class="evidence-link"><a href="${repo + esc(trial.report.path)}">Creator report and remaining weaknesses</a></p>` : ''}</div></article>`;
}
function selected(trial, stage) {
  return stage === 'retained' ? trial.captures.filter(c => c.selected_for_display) : trial.captures.filter(c => c.stage === stage);
}
function draw() {
  const stage = $('stage').value;
  if (mode === 'within') {
    const trial = data.trials.find(t => t.id === $('trial').value);
    const captures = stage === 'all' ? trial.captures : selected(trial, stage);
    $('view-note').textContent = 'Captures follow the recorded timestamps. Read the checks and recorded observations; a later capture does not automatically replace the retained best.';
    $('results').innerHTML = `<div class="trial-summary"><b>${esc(trial.short_id)} · ${esc(trial.display_name)}</b><p>${esc(trial.label)}</p><p>${trial.captures.length} recorded steps. Accepted production stages: ${esc(trial.completed_stages.map(s => data.stages[s]?.title || s).join(', ') || 'none')}.</p><p>Step numbers follow this attempt's capture order. Trying another layout and checking unchanged work are both labeled explicitly; a later step is not automatically better.</p></div><nav class="step-index" aria-label="Steps in this attempt">${captures.map(c => `<a href="#step-${esc(c.step.replace('.', '-'))}">${esc(c.step)} · ${esc(c.title)}</a>`).join('')}</nav><div class="capture-grid">${captures.length ? captures.map(c => `<div id="step-${esc(c.step.replace('.', '-'))}">${captureCard(c, trial)}</div>`).join('') : '<div class="empty">No captured evidence for this selection. The attempt outcome remains visible below.</div>'}</div>`;
  } else {
    const trials = data.trials.filter(t => t.brief === $('brief').value && t.repeat === Number($('repeat').value));
    const stages = stage === 'all' ? [...Object.keys(data.stages), 'retained'] : [stage];
    $('view-note').textContent = 'Same brief and repeat only. Each stage displays its latest recorded capture, including an unconfirmed capture when present. Retained/working-at-stop uses the original checkpoint selection. These displays introduce no preference judgments.';
    $('results').innerHTML = stages.map(s => `<div class="comparison-row"><h3>${esc(s === 'retained' ? 'Kept result / work at stop' : data.stages[s].title)}</h3><div class="capture-grid">${profiles.map(p => {const t = trials.find(x => x.condition === p); return captureCard(selected(t, s).at(-1), t, data.profile_names[p]);}).join('')}</div></div>`).join('');
  }
}
function setMode(next) {
  mode = next;
  for (const name of ['within', 'across']) $(name).setAttribute('aria-pressed', String(mode === name));
  $('trial-control').hidden = mode !== 'within';
  $('brief-control').hidden = $('repeat-control').hidden = mode !== 'across';
  draw();
}
$('outcomes').innerHTML = data.trials.map(t => `<tr><td>${esc(t.short_id)}</td><td><button class="table-link" data-trial="${esc(t.id)}">${esc(t.display_name)}</button></td><td>${esc(t.label)}</td><td>${t.captures.length}</td></tr>`).join('');
$('outcomes').addEventListener('click', e => {if (e.target.dataset.trial) {$('trial').value = e.target.dataset.trial; $('stage').value = 'all'; setMode('within'); $('explorer-title').scrollIntoView();}});
for (const id of ['trial', 'stage', 'size', 'brief', 'repeat']) $(id).addEventListener('change', draw);
$('within').addEventListener('click', () => setMode('within'));
$('across').addEventListener('click', () => setMode('across'));
draw();
