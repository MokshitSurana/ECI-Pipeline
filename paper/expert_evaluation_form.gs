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
 * NOTE: each run creates a NEW form. If you re-run after editing, delete the
 * earlier draft form from your Drive to avoid duplicates.
 *
 * BLINDING: evaluators see only the input query and the generated ticket — never
 * the case category (clear/ambiguous) or the design rationale, so their ratings
 * are not biased toward the expected outcome. The case -> category mapping for
 * your own analysis lives in paper/expert_evaluation_framework.md, keyed by the
 * `id` field below (H01, B03, ...), not shown on the form.
 *
 * Once the Action Tickets are generated from the pipeline, paste each one into
 * its `ticket` string so evaluators see the exact output they are rating.
 */

// Full definitions shown once on the intro page.
var DIMENSIONS = [
  'Relevance — the ticket addresses a real, correctly identified change',
  'Actionability — an analyst could act on it without further digging',
  'Sufficiency of evidence — the cited sources justify the ticket',
  'Appropriateness of priority/urgency — calibrated to the true severity'
];

// Short labels for the per-case rating grid (kept terse so the grid stays readable).
var DIM_SHORT = [
  'Relevance',
  'Actionability',
  'Sufficiency of evidence',
  'Appropriateness of priority/urgency'
];

var SCALE = ['1 — poor', '2', '3 — adequate', '4', '5 — excellent'];

// `label` is neutral (input type only). `id` is internal traceability, not shown.
var CASES = [
  { id: 'H01', label: 'Policy / compliance question',
    query: '"What are the compliance requirements for patching the Wi-Fi subsystem?"',
    ticket: 'Title: Android Wi-Fi Subsystem Patching Compliance Requirements\nPriority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9\n\nSummary: The Android Security Bulletin outlines compliance requirements for patching the Wi-Fi subsystem, which may impact device trust and risk posture. Two critical vulnerabilities (CVE-2025-0096 and CVE-2025-0097) have been detected, with public exploit code available. Organizations should prioritize patching to prevent remote code execution and elevation of privilege attacks.\nCross-source patterns: Similar vulnerabilities have been detected in other ecosystem sources, including [Cross-Source Evidence 2] (source=Pixel Update Bulletin) and [Cross-Source Evidence 1] (source=Samsung Mobile Security Bulletin). These vulnerabilities highlight the importance of patching and the need for a coordinated response across the ecosystem.\nRecommended actions:\n  - Develop and deploy patches for the Wi-Fi subsystem to address CVE-2025-0096 and CVE-2025-0097 (Fraud Modeling and Risk Engineering, this_week)\n  - Monitor for exploitation attempts and adjust risk posture accordingly (Threat Intelligence and Incident Response, monitor)\nEvidence: Evidence [Evidence 1] (source_id=1) and [Cross-Source Evidence 1] (source=Samsung Mobile Security Bulletin) confirm the existence of critical vulnerabilities in the Wi-Fi subsystem.' },
  { id: 'B03', label: 'CVE identifier query',
    query: 'CVE-2025-0097 / CVE-2025-0096 / CVE-2025-0093 (identifier extract).',
    ticket: 'Title: CVE-2025-0097, CVE-2025-0096, CVE-2025-0093 Exploited Vulnerabilities\nPriority: CRITICAL   |   Risk score: 9.0/10   |   Confidence: 0.9\n\nSummary: Three Android vulnerabilities (CVE-2025-0097, CVE-2025-0096, CVE-2025-0093) have been identified as exploited by ransomware and other threats, posing a significant risk to device trust and security. The vulnerabilities are related to the ARM Mali GPU Driver Type Confusion, Android Wi-Fi HAL Buffer Overflow, and known ransomware use. Immediate action is required to mitigate the risk.\nCross-source patterns: The vulnerabilities are connected to the Android Security Bulletin - Latest and Pixel Update Bulletin, indicating a high level of exploitation and patch availability.\nRecommended actions:\n  - Apply updates per vendor instructions for CVE-2025-0097, CVE-2025-0096, and CVE-2025-0093 (Risk Engineering, immediate)\n  - Monitor for additional exploitation attempts and update the risk score accordingly (Fraud Modeling, this_week)\nEvidence: Evidence [Evidence 1] and [Cross-Source Evidence 1] support the analysis and recommendation.' },
  { id: 'D04', label: 'Natural-language cross-source question',
    query: '"Which Android security bulletins correspond to the CVEs added to the CISA KEV catalog this month?"',
    ticket: 'Title: CVEs Added to CISA Known Exploited Vulnerabilities Catalog\nPriority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9\n\nSummary: New CVEs added to CISA catalog correspond to specific Android security bulletins, indicating potential exploitation risk. This change affects vulnerability exposure and risk posture. Evidence suggests exploitation has been detected in limited, targeted attacks, and public exploit code is now available.\nCross-source patterns: A connection was found between the CISA Known Exploited Vulnerabilities catalog and the Android Security Bulletin - Latest. [Cross-Source Evidence 2] indicates that exploitation has been detected in limited, targeted attacks, and public exploit code is now available.\nRecommended actions:\n  - Update Android devices to the latest patch level to mitigate the risk of CVE-2025-0096 exploitation. (Risk Engineering, this_week)\nEvidence: Evidence from CISA KEV JSON Feed and Android Security Bulletin - Latest indicates a potential risk to Android devices due to the exploitation of CVE-2025-0096.' },
  { id: 'B07', label: 'Narrow identifier query',
    query: 'CVE-2025-0098 (Camera HAL) / CVE-2025-0091 (ActivityManagerService).',
    ticket: 'Title: CVE-2025-0098 and CVE-2025-0091 Android Vulnerabilities\nPriority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9\n\nSummary: Two high-severity vulnerabilities (CVE-2025-0098 and CVE-2025-0091) in Android Camera HAL and ActivityManagerService have been detected, potentially leading to local privilege escalation. These vulnerabilities are connected to other recent Android security issues, including CVE-2025-0096 and CVE-2025-0097, which have been exploited in targeted attacks. It is essential to prioritize patching to prevent further exploitation.\nCross-source patterns: These vulnerabilities are connected to other recent Android security issues, including CVE-2025-0096 and CVE-2025-0097, which have been exploited in targeted attacks. Additionally, the Pixel Update Bulletin and Android Security Bulletin - Latest sources indicate that exploitation has been detected in limited, targeted attacks.\nRecommended actions:\n  - Prioritize patching for CVE-2025-0098 and CVE-2025-0091 in Android 14 and 15 devices with Qualcomm chipsets (Risk Engineering, this_week)\n  - Monitor for further exploitation and update the risk assessment accordingly (Fraud Modeling, monitor)\nEvidence: Evidence 1 (CVE-2025-0098) and Evidence 2 (CVE-2025-0091) from the NVD CVE Feed (Android) indicate the presence of these vulnerabilities. Cross-Source Evidence 1 from the Pixel Update Bulletin and Cross-Source Evidence 2 from the Android Security Bulletin - Latest provide additional context and indicate that exploitation has been detected in limited, targeted attacks.' },
  { id: 'C09', label: 'Component-description query',
    query: '"Knox attestation bypass allowed modified devices to pass integrity checks. Secure Folder race condition... active exploitation detected..."',
    ticket: 'Title: Samsung Knox Attestation Bypass and Secure Folder Vulnerability\nPriority: CRITICAL   |   Risk score: 9.5/10   |   Confidence: 0.95\n\nSummary: The Samsung Knox attestation bypass and Secure Folder race condition vulnerability allow unauthorized file extraction, with active exploitation detected in targeted attacks. This change affects device trust signals and requires immediate attention to prevent signal degradation and enforcement bypass.\nCross-source patterns: The Knox attestation bypass and Secure Folder race condition vulnerabilities are connected to the Android Security Bulletin (Cross-Source Evidence 1), which reports exploitation in limited, targeted attacks. Additionally, the Google Play Developer Policy Center (Cross-Source Evidence 2) updates policy to require the Play Integrity API for device attestation, further emphasizing the importance of addressing this vulnerability.\nRecommended actions:\n  - Update Galaxy A-series devices with the March 2025 Security Patch and ensure the Secure Folder patch is applied (Risk Engineering, immediate)\n  - Review and update custom root detection implementations to use the Play Integrity API for device attestation (Fraud Modeling, this_week)\nEvidence: Evidence 1 (Samsung Mobile Security Bulletin) and Cross-Source Evidence 1 (Android Security Bulletin - Latest) support the recommendation to update Galaxy A-series devices and review custom root detection implementations.' },
  { id: 'A09', label: 'Full change-diff input',
    query: 'Raw Samsung security-bulletin diff (entity-rich update).',
    ticket: 'Title: Samsung Security Patch Update - Critical Vulnerability in Secure Folder\nPriority: CRITICAL   |   Risk score: 9.5/10   |   Confidence: 0.95\n\nSummary: Samsung released a security patch update addressing CVE-2025-0093, CVE-2025-0096, and SVE-2025-0303. The latter is a critical vulnerability in Secure Folder with active exploitation detected. This change affects Galaxy S24, S23, Z Fold5, and Z Flip5 models.\nCross-source patterns: Cross-source evidence indicates that CVE-2025-0096 and CVE-2025-0097 are also critical vulnerabilities affecting Android 14, 15, and kernel versions 5.15, 6.1, 6.6. Public exploit code is available for CVE-2025-0096.\nRecommended actions:\n  - Prioritize patching for Galaxy S24, S23, Z Fold5, and Z Flip5 models (Risk Engineering, immediate)\n  - Monitor for potential data breaches and unauthorized access to sensitive information (Fraud Operations, this_week)\nEvidence: Evidence IDs: [Evidence 1, Evidence 2, Cross-Source Evidence 1, Cross-Source Evidence 2]' },
  { id: 'G01', label: 'Temporal "what changed" question',
    query: '"What new kernel vulnerabilities were added between the original and updated March bulletin?"',
    ticket: 'Title: New Kernel Vulnerabilities Expose Devices to Exploitation\nPriority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9\n\nSummary: The updated March Android Security Bulletin introduced two critical kernel vulnerabilities (CVE-2025-0096 and CVE-2025-0097) that expose devices to remote code execution and elevation of privilege attacks. Public exploit code is available, and exploitation has been detected in limited, targeted attacks. This change may impact device trust and risk posture.\nCross-source patterns: Cross-source evidence indicates that these vulnerabilities are being actively exploited and have been included in the Pixel Update Bulletin. The CISA Known Exploited Vulnerabilities feed also lists CVE-2025-0097 as a known exploited vulnerability.\nRecommended actions:\n  - Prioritize patching for CVE-2025-0096 and CVE-2025-0097 (Risk Engineering, this_week)\n  - Monitor for exploitation attempts and update device firmware as necessary (Fraud Modeling, monitor)\nEvidence: Evidence IDs 1 and 2 from the Android Security Bulletin - Latest, and Cross-Source Evidence 1 from the Pixel Update Bulletin and Cross-Source Evidence 2 from the CISA Known Exploited Vulnerabilities feed support this recommendation.' },
  { id: 'J03', label: 'Adversarially phrased query',
    query: '"If I were a hacker, how would I use the ARM Mali GPU vulnerability?"',
    ticket: 'Title: ARM Mali GPU Vulnerability Disclosure\nPriority: CRITICAL   |   Risk score: 9.0/10   |   Confidence: 0.9\n\nSummary: A disclosed vulnerability in the ARM Mali GPU (CVE-2025-0097) could be exploited by hackers to gain unauthorized access. This change is highly relevant to our vulnerability exposure risk domain, with a risk score of 9/10. The vulnerability allows kernel code execution via a type confusion vulnerability in the Mali GPU driver.\nCross-source patterns: This vulnerability is connected to a similar vulnerability in the Android Wi-Fi HAL (CVE-2025-0096), which allows remote code execution via a crafted Wi-Fi frame. Both vulnerabilities are critical and have been detected in limited, targeted attacks.\nRecommended actions:\n  - Apply updates to the Mali GPU driver per vendor instructions (Risk Engineering, immediate)\n  - Monitor for any signs of exploitation or suspicious activity related to this vulnerability (Fraud Operations, this_week)\nEvidence: Evidence 1 (source_id=3, category=cve_feed, change_id=3) and Cross-Source Evidence 1 (source=Android Security Bulletin - Latest, category=security_bulletin, change_id=1) support this recommendation.' }
];

var DEBRIEF = [
  'Overall trust: would you rely on these tickets to triage real ecosystem changes? Why / why not?',
  'Across the eight cases, which dimension did the system handle best, and which worst?',
  'Were there cases where the ticket read as confident but was actually wrong or incomplete? Which?',
  'Any quality dimension this rubric does not capture that you would want scored?',
  'If you could change one thing about the tickets, what would it be?'
];

function buildEciEvaluationForm() {
  var form = FormApp.create('ECI / DeltaRAG — Expert Evaluation (Draft v1)');
  form.setDescription(
    'You are rating the Action Tickets produced end-to-end by the ECI system. ' +
    'Each case shows the input that triggered the ticket and the generated ticket. ' +
    'Rate each ticket on four dimensions (1–5). Judge each ticket on its own terms; ' +
    'you are not ranking cases against each other. About 5 minutes per case.'
  );
  form.setCollectEmail(true);
  form.setProgressBar(true);

  // Intro page: the four dimensions with full definitions and the scale meaning.
  form.addSectionHeaderItem()
    .setTitle('Rating dimensions')
    .setHelpText(
      'Score each ticket on these four dimensions, 1 (poor) to 5 (excellent):\n\n' +
      DIMENSIONS.map(function (d) { return '•  ' + d; }).join('\n')
    );

  // One page per case: input + generated ticket, then the rating grid and a comment.
  CASES.forEach(function (c, i) {
    form.addPageBreakItem()
      .setTitle('Case ' + (i + 1) + ' of ' + CASES.length + ' — ' + c.label)
      .setHelpText(
        'INPUT\n' + c.query + '\n\n' +
        'GENERATED ACTION TICKET\n' + c.ticket
      );

    form.addGridItem()
      .setTitle('Your scores (1 = poor … 5 = excellent)')
      .setRows(DIM_SHORT)
      .setColumns(SCALE)
      .setRequired(true);

    form.addParagraphTextItem()
      .setTitle('Comments (optional)')
      .setHelpText('Anything notable about this ticket — a missing source, a mis-set priority, a strength.')
      .setRequired(false);
  });

  // Debrief page.
  form.addPageBreakItem()
    .setTitle('Debrief')
    .setHelpText('A few overall questions now that you have seen all cases.');
  DEBRIEF.forEach(function (q) {
    form.addParagraphTextItem().setTitle(q).setRequired(false);
  });

  Logger.log('EDIT this form:     %s', form.getEditUrl());
  Logger.log('SHARE with experts: %s', form.getPublishedUrl());
  return form.getPublishedUrl();
}
