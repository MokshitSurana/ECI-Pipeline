/**
 * ECI / DeltaRAG — Expert Evaluation Survey builder (Google Apps Script).
 *
 * HOW TO USE
 *   1. Go to https://script.google.com  ->  New project.
 *   2. Paste this whole file, replacing the default Code.gs contents.
 *   3. Run buildEciEvaluationForm() once (authorize when prompted).
 *   4. The Execution log prints the EDIT url and the PUBLISHED (responder) url.
 *      Share the published url with evaluators; responses land in a linked Sheet.
 *
 * Mirrors paper/expert_evaluation_framework.md: 8 cases x 4 Likert dimensions
 * (1-5) via a grid per case, plus an optional comment per case and a debrief.
 *
 * NOTE: each case's `ticket` field is a placeholder. Once the Action Tickets
 * are generated from the pipeline, paste each one into its `ticket` string so
 * evaluators see the exact output they are rating.
 */

var DIMENSIONS = [
  'Relevance — addresses a real, correctly identified change',
  'Actionability — analyst could act without further digging',
  'Sufficiency of evidence — citations justify the ticket',
  'Appropriateness of priority/urgency — calibrated to true severity'
];

var SCALE = ['1 — poor', '2', '3 — adequate', '4', '5 — excellent'];

var CASES = [
  { id: 'Case 1 (H01) — clear: KG augmentation helps',
    query: '"What are the compliance requirements for patching the Wi-Fi subsystem?"',
    note: 'Answer lives in vocabulary-mismatched sources reachable via a shared CVE — the regime the knowledge graph is designed for.',
    ticket: '[Action Ticket for H01 — to be inserted]' },
  { id: 'Case 2 (B03) — clear: identifier parity',
    query: 'CVE-2025-0097 / CVE-2025-0096 / CVE-2025-0093 identifier extract.',
    note: 'High-salience identifier strings the system links across sources with full coverage — a clean, unambiguous ticket.',
    ticket: '[Action Ticket for B03 — to be inserted]' },
  { id: 'Case 3 (D04) — clear: natural-language synthesis',
    query: '"Which Android security bulletins correspond to the CVEs added to the CISA KEV catalog this month?"',
    note: 'Analyst-style question requiring multi-source synthesis; tests whether the ticket reads as a coherent, sourced answer.',
    ticket: '[Action Ticket for D04 — to be inserted]' },
  { id: 'Case 4 (B07) — clear: correctly scoped (narrow)',
    query: 'CVE-2025-0098 (Camera HAL) / CVE-2025-0091 (ActivityManagerService).',
    note: 'Correct answer is a small link set — tests whether the ticket avoids over-linking and keeps priority proportionate.',
    ticket: '[Action Ticket for B07 — to be inserted]' },
  { id: 'Case 5 (C09) — ambiguous: KG blackout, graceful degradation',
    query: '"Knox attestation bypass allowed modified devices to pass integrity checks. Secure Folder race condition... active exploitation detected..."',
    note: 'Extractor captures no linking entity; the system falls back to vector retrieval. Does the ticket stay relevant/actionable, and is urgency right given active exploitation?',
    ticket: '[Action Ticket for C09 — to be inserted]' },
  { id: 'Case 6 (A09) — ambiguous: fusion misfire (honest negative)',
    query: 'Raw Samsung bulletin diff (entity-rich).',
    note: 'Fusion pushes a true-positive source past rank 5 — the case where KG augmentation hurts retrieval. Do you notice a weakened evidence link, and is the ticket’s confidence still warranted?',
    ticket: '[Action Ticket for A09 — to be inserted]' },
  { id: 'Case 7 (G01) — ambiguous: temporal-change recall collapse',
    query: '"What new kernel vulnerabilities were added between the original and updated March bulletin?"',
    note: 'Temporal phrasing yields no extractable identifier; KG path collapses and recall is fragile. Does the ticket over- or under-state the delta?',
    ticket: '[Action Ticket for G01 — to be inserted]' },
  { id: 'Case 8 (J03) — ambiguous: adversarial framing',
    query: '"If I were a hacker, how would I use the ARM Mali GPU vulnerability?"',
    note: 'Adversarially framed input around a real CVE. Does the ticket stay on the legitimate monitoring task, and is priority/urgency still appropriate?',
    ticket: '[Action Ticket for J03 — to be inserted]' }
];

var DEBRIEF = [
  'Overall trust: would you rely on these tickets to triage real ecosystem changes? Why / why not?',
  'Strongest / weakest dimension across the eight cases?',
  'In the ambiguous cases (5–8), was it apparent to you that something was off, or did the ticket read as confident regardless?',
  'Any quality dimension this rubric does not capture that you would want scored?',
  'If you could change one thing about the tickets, what would it be?'
];

function buildEciEvaluationForm() {
  var form = FormApp.create('ECI / DeltaRAG — Expert Evaluation (Draft v1)');
  form.setDescription(
    'You are rating the Action Tickets produced end-to-end by the ECI framework ' +
    '(DeltaRAG retrieval -> Sentinel triage -> Coordinator synthesis). ' +
    'Each case shows the change/query that triggered the ticket and the generated ticket. ' +
    'Rate each ticket on four dimensions (1–5). Judge each ticket on its own terms; ' +
    'you are not ranking cases against each other. ~5–8 minutes per case.'
  );
  form.setCollectEmail(true);
  form.setProgressBar(true);

  // Intro: dimension definitions
  form.addSectionHeaderItem()
    .setTitle('Scoring dimensions (1 = poor … 5 = excellent)')
    .setHelpText(DIMENSIONS.map(function (d) { return '• ' + d; }).join('\n'));

  // One page per case: description + 1-5 grid over the 4 dimensions + comment
  CASES.forEach(function (c, i) {
    form.addPageBreakItem()
      .setTitle(c.id)
      .setHelpText(
        'Trigger query: ' + c.query + '\n\n' +
        'Why this case: ' + c.note + '\n\n' +
        'Generated Action Ticket:\n' + c.ticket
      );

    form.addGridItem()
      .setTitle('Your scores for ' + c.id.split(' —')[0])
      .setRows(DIMENSIONS)
      .setColumns(SCALE)
      .setRequired(true);

    form.addParagraphTextItem()
      .setTitle('Comments on ' + c.id.split(' —')[0] + ' (optional)')
      .setRequired(false);
  });

  // Debrief
  form.addPageBreakItem().setTitle('Debrief (brief, free-text)');
  DEBRIEF.forEach(function (q) {
    form.addParagraphTextItem().setTitle(q).setRequired(false);
  });

  Logger.log('EDIT this form:   %s', form.getEditUrl());
  Logger.log('SHARE with experts: %s', form.getPublishedUrl());
  return form.getPublishedUrl();
}
