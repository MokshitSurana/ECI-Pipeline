/**
 * ECI / DeltaRAG — Expert Evaluation Survey builder (Google Apps Script).
 *
 * Builds the Google Form for paper/expert_evaluation_questionnaire.md v1.0.
 * Supersedes the earlier paper/expert_evaluation_form.gs.
 *
 * HOW TO USE
 *   1. Fill in the CONFIG block below (PI email, storage location).
 *   2. Go to https://script.google.com  ->  New project.
 *   3. Paste this whole file, replacing the default Code.gs contents.
 *   4. Run buildEciEvaluationForm() once and authorize when prompted.
 *   5. The Execution log prints the EDIT url and the PUBLISHED (responder) url.
 *      Share the published url with evaluators; responses land in a linked Sheet
 *      (Responses tab -> "Link to Sheets").
 *
 * Each run creates a NEW form. If you re-run after editing, delete the earlier
 * draft from Drive so evaluators cannot land on a stale copy.
 *
 * ANONYMITY: email collection and login are explicitly disabled below. The
 * consent text promises anonymity — do not turn these on without amending it.
 *
 * BLINDING: evaluators see only the input and the generated ticket. They never
 * see the query ID, the clear/ambiguous designation, or the design rationale.
 * That mapping lives in the Analysis Key of the questionnaire markdown and in
 * the CASES `id` / `intent` fields below, neither of which is rendered.
 *
 * ORDER: cases alternate clear / ambiguous so difficulty is not confounded with
 * position. Do not sort this array.
 */

// ── CONFIG — fill these in before running ────────────────────────────────
var CONFIG = {
  formTitle: 'Expert Evaluation of Automated Ecosystem-Change Action Tickets',
  piName: 'Fatemeh Sarayloo, Ph.D.',
  piEmail: 'fsaraylo@uic.edu',                 // TODO: fill in
  storageLocation: 'mokshitsurana3110@gmail.com', // TODO: e.g. 'a UIC-managed Google account'
  // Set true only if the consent text is amended to disclose it. See header.
  collectEmail: false
};

// ── Participant-facing information sheet ─────────────────────────────────
var INFO_SHEET = [
  'WHAT THIS IS',
  'You are invited to take part in a research study run by the University of Illinois Chicago. We have built a system that monitors public Android security and policy sources, detects what changed, and automatically drafts a short "action ticket" for a risk or fraud team. We are asking practitioners to judge the quality of those tickets.',
  '',
  'WHAT YOU WILL DO',
  'You will read eight machine-generated action tickets. For each one you will see the input that triggered it and the ticket itself, and you will rate it on four dimensions using a 1-5 scale. You may add a comment on any ticket. A few short background questions come first, and five open-ended questions come at the end.',
  '',
  'TIME',
  'Approximately 45-60 minutes.',
  '',
  'VOLUNTARY',
  'Participation is entirely voluntary. You may skip any question or stop at any time, with no consequence. There is no compensation.',
  '',
  'RISKS AND BENEFITS',
  'There are no anticipated risks beyond those of ordinary professional activity. There is no direct benefit to you. The findings will inform academic research on automated risk monitoring.',
  '',
  'CONFIDENTIALITY',
  'This survey is anonymous. We do not collect your name, email address, employer name, or any other identifier. Please do not include confidential, proprietary, or client-identifying information from your organization in your free-text comments. Background questions are collected only in broad categories so that no individual can be identified. Responses are stored in ' + CONFIG.storageLocation + ' and reported only in aggregate or as de-identified quotations.',
  '',
  'USE OF RESULTS',
  'Aggregate ratings and anonymized quotations may appear in a peer-reviewed publication.',
  '',
  'QUESTIONS',
  'Contact the Principal Investigator, Dr. ' + CONFIG.piName + ', at ' + CONFIG.piEmail + '. If you have questions about your rights as a research participant, contact the UIC Office for the Protection of Research Subjects at 312-996-1711 or uicirb@uic.edu.'
].join('\n');

// ── Rating dimensions ────────────────────────────────────────────────────
var DIMENSION_GUIDE = [
  'Rate every ticket on all four dimensions, 1 (poor) to 5 (excellent). Please use the whole scale. Judge each ticket ON ITS OWN TERMS — you are not ranking the cases against one another, and the cases are not in any order of expected quality.',
  '',
  'D1 — RELEVANCE. Does the ticket address a real, correctly identified change in the monitored ecosystem, rather than a hallucinated, stale, or off-target item?',
  '   1 off-target or spurious  |  2 tangentially related  |  3 relevant but partly off  |  4 relevant, minor gaps  |  5 precisely on-target',
  '',
  'D2 — ACTIONABILITY. Could an analyst act on this ticket without further digging? Is the recommended action clear and operationally useful?',
  '   1 no usable action  |  2 vague direction  |  3 actionable with effort  |  4 mostly clear next step  |  5 immediately actionable',
  '',
  'D3 — SUFFICIENCY OF EVIDENCE. Look at the evidence shown below each ticket. Are those sources and cross-source links adequate to justify the claims the ticket makes?',
  '   1 no or wrong evidence  |  2 thin, key source missing  |  3 partial support  |  4 adequate support  |  5 complete, well-linked',
  '',
  'D4 — APPROPRIATENESS OF PRIORITY AND URGENCY. Is the assigned priority, risk score, and urgency calibrated to the change\'s true severity — neither over- nor under-escalated?',
  '   1 badly miscalibrated  |  2 clearly off  |  3 roughly right  |  4 appropriate, minor drift  |  5 well calibrated'
].join('\n');

var DIM_ROWS = [
  'D1 Relevance',
  'D2 Actionability',
  'D3 Sufficiency of evidence',
  'D4 Appropriateness of priority / urgency'
];

var SCALE = ['1 — poor', '2', '3 — adequate', '4', '5 — excellent'];

// ── Section A: background ────────────────────────────────────────────────
var BACKGROUND = [
  { type: 'choice', title: 'A1. Which best describes your primary professional role?',
    help: 'Please answer in the categories given; do not add identifying detail.',
    options: ['Security engineering / AppSec', 'Threat intelligence', 'Fraud operations',
              'Risk or fraud analytics', 'Compliance / regulatory', 'Engineering leadership'],
    other: true },
  { type: 'choice', title: 'A2. Years of professional experience in that area',
    options: ['1-3', '4-7', '8-12', '13+'], other: false },
  { type: 'choice', title: 'A3. Which sector best describes your current organization?',
    options: ['Financial services / fintech', 'Technology / platform', 'Security vendor',
              'Consulting'],
    other: true },
  { type: 'scale', title: 'A4. How familiar are you with the Android security and policy ecosystem?',
    help: 'Security bulletins, Play Integrity, Play developer policy, CVE feeds.',
    low: 'Not familiar', high: 'Work with it regularly' },
  { type: 'choice', title: 'A5. In your current work, how are ecosystem changes like these tracked today?',
    options: ['Manually, by people reading sources', 'Partly automated (alerts, feeds)',
              'Mostly automated tooling', 'Not tracked systematically', 'Not applicable'],
    other: false }
];

// ── Retrieved evidence per case ──────────────────────────────────────────
// The exact chunks the Coordinator was given when it wrote each ticket, so
// evaluators can resolve the [Evidence N] citations in the ticket text and
// actually score D3. Reproduced read-only from the isolated eval DB.
var EVIDENCE = {
  'B03': 'FROM THE SAME SOURCE\n\n[Evidence 1] — CISA Known Exploited Vulnerabilities  (newly added content)\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded"\n\n[Evidence 2] — CISA Known Exploited Vulnerabilities  (content removed in this update)\n"catalogVersion": "2025.03.15",\n  "totalCount": 1245,\n\nLINKED FROM OTHER SOURCES\n\n[Cross-Source Evidence 1] — Android Security Bulletin - Latest\nPublished March 3, 2025 | Updated March 17, 2025\nUpdated: Exploitation has been detected in limited, targeted attacks.\nUpdated: Public exploit code is now available. Organizations should prioritize patching.\nCVE-2025-0096 - Remote Code Execution - Critical (NEW)\nAffected component: Wi-Fi subsystem\nAffected versions: Android 14, 15\nDescription: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.\nUpdated: Additional patch now available for kernel 6.6.\nCVE-2025-0097 - Elevation of Privilege - Critical (NEW)\nAffected component: GPU driver (Mali)\nAffected versions: Android kernel versions 5.15, 6.1, 6.6\nDescription: A type confusion vulnerability i\n\n[Cross-Source Evidence 2] — Pixel Update Bulletin\nPublished March 5, 2025 | Updated March 19, 2025\nAll Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.\nUpdated: Additional mitigation deployed via Play system update.\nCVE-2025-P003 - High (NEW)\nComponent: Pixel Modem firmware\nDescription: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.\nAffected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)\nNote: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.\n- New: Theft Detection Lock improvements for Pixel 7+\n\n[Cross-Source Evidence 3] — CISA KEV JSON Feed\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded": "2025-03-21",',
  'C09': 'FROM THE SAME SOURCE\n\n[Evidence 1] — Samsung Mobile Security Bulletin  (newly added content)\nMarch 2025 Security Patch (Updated March 20, 2025)\n- System: CVE-2025-0093, CVE-2025-0096 (NEW)\nUpdated: Patch now available for Galaxy A-series devices\nSVE-2025-0303 - Critical (NEW)\nAffected component: Samsung Secure Folder\nDescription: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.\nAffected models: Galaxy S24, S23, Z Fold5, Z Flip5\nNote: Active exploitation detected in targeted attacks.\n\n[Evidence 2] — Samsung Mobile Security Bulletin  (content removed in this update)\nMarch 2025 Security Patch\n- System: CVE-2025-0093\n\nLINKED FROM OTHER SOURCES\n\n[Cross-Source Evidence 1] — Android Security Bulletin - Latest\nPublished March 3, 2025 | Updated March 17, 2025\nUpdated: Exploitation has been detected in limited, targeted attacks.\nUpdated: Public exploit code is now available. Organizations should prioritize patching.\nCVE-2025-0096 - Remote Code Execution - Critical (NEW)\nAffected component: Wi-Fi subsystem\nAffected versions: Android 14, 15\nDescription: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.\nUpdated: Additional patch now available for kernel 6.6.\nCVE-2025-0097 - Elevation of Privilege - Critical (NEW)\nAffected component: GPU driver (Mali)\nAffected versions: Android kernel versions 5.15, 6.1, 6.6\nDescription: A type confusion vulnerability i\n\n[Cross-Source Evidence 2] — Google Play Developer Policy Center\nLast updated: March 20, 2025\nNEW (Effective June 2025): Apps that detect rooted or modified devices must use the Play Integrity API for device attestation. Custom root detection implementations will no longer be accepted as the sole verification method.\nUPDATED: Starting May 2025, financial apps must implement the Play Integrity API with MEETS_STRONG_INTEGRITY verification for all transaction-initiating actions. Apps not meeting this requirement will receive policy warnings beginning July 2025.\nUPDATED: The Photo and Video permissions policy now requires apps to use the Android Photo Picker API instead of requesting broad storage access. Apps with existing READ_MEDIA_IMAGES permission must migrate by September 2025.\nAI\n\n[Cross-Source Evidence 3] — Pixel Update Bulletin\nPublished March 5, 2025 | Updated March 19, 2025\nAll Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.\nUpdated: Additional mitigation deployed via Play system update.\nCVE-2025-P003 - High (NEW)\nComponent: Pixel Modem firmware\nDescription: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.\nAffected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)\nNote: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.\n- New: Theft Detection Lock improvements for Pixel 7+',
  'D04': 'FROM THE SAME SOURCE\n\n[Evidence 1] — CISA KEV JSON Feed  (newly added content)\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded": "2025-03-21",\n\n[Evidence 2] — CISA KEV JSON Feed  (content removed in this update)\n"catalogVersion": "2025.03.15",\n  "totalCount": 1245,\n\nLINKED FROM OTHER SOURCES\n\n[Cross-Source Evidence 1] — CISA Known Exploited Vulnerabilities\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded"\n\n[Cross-Source Evidence 2] — Android Security Bulletin - Latest\nPublished March 3, 2025 | Updated March 17, 2025\nUpdated: Exploitation has been detected in limited, targeted attacks.\nUpdated: Public exploit code is now available. Organizations should prioritize patching.\nCVE-2025-0096 - Remote Code Execution - Critical (NEW)\nAffected component: Wi-Fi subsystem\nAffected versions: Android 14, 15\nDescription: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.\nUpdated: Additional patch now available for kernel 6.6.\nCVE-2025-0097 - Elevation of Privilege - Critical (NEW)\nAffected component: GPU driver (Mali)\nAffected versions: Android kernel versions 5.15, 6.1, 6.6\nDescription: A type confusion vulnerability i\n\n[Cross-Source Evidence 3] — Pixel Update Bulletin\nPublished March 5, 2025 | Updated March 19, 2025\nAll Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.\nUpdated: Additional mitigation deployed via Play system update.\nCVE-2025-P003 - High (NEW)\nComponent: Pixel Modem firmware\nDescription: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.\nAffected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)\nNote: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.\n- New: Theft Detection Lock improvements for Pixel 7+',
  'G01': 'FROM THE SAME SOURCE\n\n[Evidence 1] — Android Security Bulletin - Latest  (newly added content)\nPublished March 3, 2025 | Updated March 17, 2025\nUpdated: Exploitation has been detected in limited, targeted attacks.\nUpdated: Public exploit code is now available. Organizations should prioritize patching.\nCVE-2025-0096 - Remote Code Execution - Critical (NEW)\nAffected component: Wi-Fi subsystem\nAffected versions: Android 14, 15\nDescription: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.\nUpdated: Additional patch now available for kernel 6.6.\nCVE-2025-0097 - Elevation of Privilege - Critical (NEW)\nAffected component: GPU driver (Mali)\nAffected versions: Android kernel versions 5.15, 6.1, 6.6\nDescription: A type confusion vulnerability i\n\n[Evidence 2] — Android Security Bulletin - Latest  (content removed in this update)\nPublished March 3, 2025\n\nLINKED FROM OTHER SOURCES\n\n[Cross-Source Evidence 1] — Pixel Update Bulletin\nPublished March 5, 2025 | Updated March 19, 2025\nAll Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.\nUpdated: Additional mitigation deployed via Play system update.\nCVE-2025-P003 - High (NEW)\nComponent: Pixel Modem firmware\nDescription: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.\nAffected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)\nNote: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.\n- New: Theft Detection Lock improvements for Pixel 7+\n\n[Cross-Source Evidence 2] — CISA Known Exploited Vulnerabilities\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded"\n\n[Cross-Source Evidence 3] — Samsung Mobile Security Bulletin\nMarch 2025 Security Patch (Updated March 20, 2025)\n- System: CVE-2025-0093, CVE-2025-0096 (NEW)\nUpdated: Patch now available for Galaxy A-series devices\nSVE-2025-0303 - Critical (NEW)\nAffected component: Samsung Secure Folder\nDescription: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.\nAffected models: Galaxy S24, S23, Z Fold5, Z Flip5\nNote: Active exploitation detected in targeted attacks.',
  'B07': 'FROM THE SAME SOURCE\n\n[Evidence 1] — NVD CVE Feed (Android)  (newly added content)\n"resultsPerPage": 3,\n  "totalResults": 3,\n        "id": "CVE-2025-0098",\n        "published": "2025-03-20T12:00:00.000",\n        "descriptions": [\n          {"lang": "en", "value": "An integer overflow in the Android Camera HAL allows local privilege escalation via a crafted camera request. Affects Android 14, 15 devices with Qualcomm chipsets."}\n        "metrics": {\n          "cvssMetricV31": [\n            {"cvssData": {"baseScore": 7.5, "baseSeverity": "HIGH"}}\n\n[Evidence 2] — NVD CVE Feed (Android)  (content removed in this update)\n"resultsPerPage": 2,\n  "totalResults": 2,\n\nLINKED FROM OTHER SOURCES\n\n[Cross-Source Evidence 1] — Pixel Update Bulletin\nPublished March 5, 2025 | Updated March 19, 2025\nAll Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.\nUpdated: Additional mitigation deployed via Play system update.\nCVE-2025-P003 - High (NEW)\nComponent: Pixel Modem firmware\nDescription: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.\nAffected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)\nNote: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.\n- New: Theft Detection Lock improvements for Pixel 7+\n\n[Cross-Source Evidence 2] — Android Security Bulletin - Latest\nPublished March 3, 2025 | Updated March 17, 2025\nUpdated: Exploitation has been detected in limited, targeted attacks.\nUpdated: Public exploit code is now available. Organizations should prioritize patching.\nCVE-2025-0096 - Remote Code Execution - Critical (NEW)\nAffected component: Wi-Fi subsystem\nAffected versions: Android 14, 15\nDescription: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.\nUpdated: Additional patch now available for kernel 6.6.\nCVE-2025-0097 - Elevation of Privilege - Critical (NEW)\nAffected component: GPU driver (Mali)\nAffected versions: Android kernel versions 5.15, 6.1, 6.6\nDescription: A type confusion vulnerability i\n\n[Cross-Source Evidence 3] — CISA KEV JSON Feed\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded": "2025-03-21",',
  'A09': 'FROM THE SAME SOURCE\n\n[Evidence 1] — Samsung Mobile Security Bulletin  (newly added content)\nMarch 2025 Security Patch (Updated March 20, 2025)\n- System: CVE-2025-0093, CVE-2025-0096 (NEW)\nUpdated: Patch now available for Galaxy A-series devices\nSVE-2025-0303 - Critical (NEW)\nAffected component: Samsung Secure Folder\nDescription: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.\nAffected models: Galaxy S24, S23, Z Fold5, Z Flip5\nNote: Active exploitation detected in targeted attacks.\n\n[Evidence 2] — Samsung Mobile Security Bulletin  (content removed in this update)\nMarch 2025 Security Patch\n- System: CVE-2025-0093\n\nLINKED FROM OTHER SOURCES\n\n[Cross-Source Evidence 1] — Android Security Bulletin - Latest\nPublished March 3, 2025 | Updated March 17, 2025\nUpdated: Exploitation has been detected in limited, targeted attacks.\nUpdated: Public exploit code is now available. Organizations should prioritize patching.\nCVE-2025-0096 - Remote Code Execution - Critical (NEW)\nAffected component: Wi-Fi subsystem\nAffected versions: Android 14, 15\nDescription: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.\nUpdated: Additional patch now available for kernel 6.6.\nCVE-2025-0097 - Elevation of Privilege - Critical (NEW)\nAffected component: GPU driver (Mali)\nAffected versions: Android kernel versions 5.15, 6.1, 6.6\nDescription: A type confusion vulnerability i\n\n[Cross-Source Evidence 2] — CISA Known Exploited Vulnerabilities\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded"\n\n[Cross-Source Evidence 3] — Pixel Update Bulletin\nPublished March 5, 2025 | Updated March 19, 2025\nAll Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.\nUpdated: Additional mitigation deployed via Play system update.\nCVE-2025-P003 - High (NEW)\nComponent: Pixel Modem firmware\nDescription: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.\nAffected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)\nNote: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.\n- New: Theft Detection Lock improvements for Pixel 7+',
  'H01': 'FROM THE SAME SOURCE\n\n[Evidence 1] — Android Security Bulletin - Latest  (newly added content)\nPublished March 3, 2025 | Updated March 17, 2025\nUpdated: Exploitation has been detected in limited, targeted attacks.\nUpdated: Public exploit code is now available. Organizations should prioritize patching.\nCVE-2025-0096 - Remote Code Execution - Critical (NEW)\nAffected component: Wi-Fi subsystem\nAffected versions: Android 14, 15\nDescription: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.\nUpdated: Additional patch now available for kernel 6.6.\nCVE-2025-0097 - Elevation of Privilege - Critical (NEW)\nAffected component: GPU driver (Mali)\nAffected versions: Android kernel versions 5.15, 6.1, 6.6\nDescription: A type confusion vulnerability i\n\n[Evidence 2] — Android Security Bulletin - Latest  (content removed in this update)\nPublished March 3, 2025\n\nLINKED FROM OTHER SOURCES\n\n[Cross-Source Evidence 1] — Samsung Mobile Security Bulletin\nMarch 2025 Security Patch (Updated March 20, 2025)\n- System: CVE-2025-0093, CVE-2025-0096 (NEW)\nUpdated: Patch now available for Galaxy A-series devices\nSVE-2025-0303 - Critical (NEW)\nAffected component: Samsung Secure Folder\nDescription: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.\nAffected models: Galaxy S24, S23, Z Fold5, Z Flip5\nNote: Active exploitation detected in targeted attacks.\n\n[Cross-Source Evidence 2] — Pixel Update Bulletin\nPublished March 5, 2025 | Updated March 19, 2025\nAll Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.\nUpdated: Additional mitigation deployed via Play system update.\nCVE-2025-P003 - High (NEW)\nComponent: Pixel Modem firmware\nDescription: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.\nAffected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)\nNote: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.\n- New: Theft Detection Lock improvements for Pixel 7+\n\n[Cross-Source Evidence 3] — Samsung Mobile Security Bulletin\nMarch 2025 Security Patch\n- System: CVE-2025-0093',
  'J03': 'FROM THE SAME SOURCE\n\n[Evidence 1] — CISA Known Exploited Vulnerabilities  (newly added content)\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded"\n\n[Evidence 2] — CISA Known Exploited Vulnerabilities  (content removed in this update)\n"catalogVersion": "2025.03.15",\n  "totalCount": 1245,\n\nLINKED FROM OTHER SOURCES\n\n[Cross-Source Evidence 1] — Android Security Bulletin - Latest\nPublished March 3, 2025 | Updated March 17, 2025\nUpdated: Exploitation has been detected in limited, targeted attacks.\nUpdated: Public exploit code is now available. Organizations should prioritize patching.\nCVE-2025-0096 - Remote Code Execution - Critical (NEW)\nAffected component: Wi-Fi subsystem\nAffected versions: Android 14, 15\nDescription: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.\nUpdated: Additional patch now available for kernel 6.6.\nCVE-2025-0097 - Elevation of Privilege - Critical (NEW)\nAffected component: GPU driver (Mali)\nAffected versions: Android kernel versions 5.15, 6.1, 6.6\nDescription: A type confusion vulnerability i\n\n[Cross-Source Evidence 2] — CISA KEV JSON Feed\n"catalogVersion": "2025.03.22",\n  "totalCount": 1249,\n      "knownRansomwareCampaignUse": "Known"\n      "cveID": "CVE-2025-0097",\n      "vendorProject": "ARM",\n      "product": "Mali GPU Driver",\n      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",\n      "dateAdded": "2025-03-20",\n      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",\n      "requiredAction": "Apply updates per vendor instructions.",\n      "dueDate": "2025-04-10",\n      "knownRansomwareCampaignUse": "Unknown"\n      "cveID": "CVE-2025-0096",\n      "vendorProject": "Google",\n      "product": "Android",\n      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",\n      "dateAdded": "2025-03-21",\n\n[Cross-Source Evidence 3] — Pixel Update Bulletin\nPublished March 5, 2025 | Updated March 19, 2025\nAll Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.\nUpdated: Additional mitigation deployed via Play system update.\nCVE-2025-P003 - High (NEW)\nComponent: Pixel Modem firmware\nDescription: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.\nAffected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)\nNote: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.\n- New: Theft Detection Lock improvements for Pixel 7+',
};

// ── The eight cases, in presentation order ───────────────────────────────
// `label` is neutral (input type only). `id` and `intent` are internal
// traceability and are NEVER rendered on the form.
var CASES = [
  { id: 'B03', intent: 'clear', label: 'CVE identifier query',
    query: 'CVE-2025-0097 / CVE-2025-0096 / CVE-2025-0093 (identifier extract).',
    ticket: [
      'Title: CVE-2025-0097, CVE-2025-0096, CVE-2025-0093 Exploited Vulnerabilities',
      'Priority: CRITICAL   |   Risk score: 9.0/10   |   Confidence: 0.9',
      '',
      'Summary: Three Android vulnerabilities (CVE-2025-0097, CVE-2025-0096, CVE-2025-0093) have been identified as exploited by ransomware and other threats, posing a significant risk to device trust and security. The vulnerabilities are related to the ARM Mali GPU Driver Type Confusion, Android Wi-Fi HAL Buffer Overflow, and known ransomware use. Immediate action is required to mitigate the risk.',
      '',
      'Cross-source patterns: The vulnerabilities are connected to the Android Security Bulletin - Latest and Pixel Update Bulletin, indicating a high level of exploitation and patch availability.',
      '',
      'Recommended actions:',
      '  - Apply updates per vendor instructions for CVE-2025-0097, CVE-2025-0096, and CVE-2025-0093 (Risk Engineering, immediate)',
      '  - Monitor for additional exploitation attempts and update the risk score accordingly (Fraud Modeling, this_week)',
      '',
      'Evidence: Evidence [Evidence 1] and [Cross-Source Evidence 1] support the analysis and recommendation.'
    ].join('\n') },

  { id: 'C09', intent: 'ambiguous', label: 'Component-description query',
    query: '"Knox attestation bypass allowed modified devices to pass integrity checks. Secure Folder race condition... active exploitation detected..."',
    ticket: [
      'Title: Samsung Knox Attestation Bypass and Secure Folder Vulnerability',
      'Priority: CRITICAL   |   Risk score: 9.5/10   |   Confidence: 0.95',
      '',
      'Summary: The Samsung Knox attestation bypass and Secure Folder race condition vulnerability allow unauthorized file extraction, with active exploitation detected in targeted attacks. This change affects device trust signals and requires immediate attention to prevent signal degradation and enforcement bypass.',
      '',
      'Cross-source patterns: The Knox attestation bypass and Secure Folder race condition vulnerabilities are connected to the Android Security Bulletin (Cross-Source Evidence 1), which reports exploitation in limited, targeted attacks. Additionally, the Google Play Developer Policy Center (Cross-Source Evidence 2) updates policy to require the Play Integrity API for device attestation, further emphasizing the importance of addressing this vulnerability.',
      '',
      'Recommended actions:',
      '  - Update Galaxy A-series devices with the March 2025 Security Patch and ensure the Secure Folder patch is applied (Risk Engineering, immediate)',
      '  - Review and update custom root detection implementations to use the Play Integrity API for device attestation (Fraud Modeling, this_week)',
      '',
      'Evidence: Evidence 1 (Samsung Mobile Security Bulletin) and Cross-Source Evidence 1 (Android Security Bulletin - Latest) support the recommendation to update Galaxy A-series devices and review custom root detection implementations.'
    ].join('\n') },

  { id: 'D04', intent: 'clear', label: 'Natural-language cross-source question',
    query: '"Which Android security bulletins correspond to the CVEs added to the CISA Known Exploited Vulnerabilities catalog this month?"',
    ticket: [
      'Title: CVEs Added to CISA Known Exploited Vulnerabilities Catalog',
      'Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9',
      '',
      'Summary: New CVEs added to CISA catalog correspond to specific Android security bulletins, indicating potential exploitation risk. This change affects vulnerability exposure and risk posture. Evidence suggests exploitation has been detected in limited, targeted attacks, and public exploit code is now available.',
      '',
      'Cross-source patterns: A connection was found between the CISA Known Exploited Vulnerabilities catalog and the Android Security Bulletin - Latest. [Cross-Source Evidence 2] indicates that exploitation has been detected in limited, targeted attacks, and public exploit code is now available.',
      '',
      'Recommended actions:',
      '  - Update Android devices to the latest patch level to mitigate the risk of CVE-2025-0096 exploitation. (Risk Engineering, this_week)',
      '',
      'Evidence: Evidence from CISA KEV JSON Feed and Android Security Bulletin - Latest indicates a potential risk to Android devices due to the exploitation of CVE-2025-0096.'
    ].join('\n') },

  { id: 'G01', intent: 'ambiguous', label: 'Temporal "what changed" question',
    query: '"What new kernel vulnerabilities were added between the original and updated March bulletin?"',
    ticket: [
      'Title: New Kernel Vulnerabilities Expose Devices to Exploitation',
      'Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9',
      '',
      'Summary: The updated March Android Security Bulletin introduced two critical kernel vulnerabilities (CVE-2025-0096 and CVE-2025-0097) that expose devices to remote code execution and elevation of privilege attacks. Public exploit code is available, and exploitation has been detected in limited, targeted attacks. This change may impact device trust and risk posture.',
      '',
      'Cross-source patterns: Cross-source evidence indicates that these vulnerabilities are being actively exploited and have been included in the Pixel Update Bulletin. The CISA Known Exploited Vulnerabilities feed also lists CVE-2025-0097 as a known exploited vulnerability.',
      '',
      'Recommended actions:',
      '  - Prioritize patching for CVE-2025-0096 and CVE-2025-0097 (Risk Engineering, this_week)',
      '  - Monitor for exploitation attempts and update device firmware as necessary (Fraud Modeling, monitor)',
      '',
      'Evidence: Evidence IDs 1 and 2 from the Android Security Bulletin - Latest, and Cross-Source Evidence 1 from the Pixel Update Bulletin and Cross-Source Evidence 2 from the CISA Known Exploited Vulnerabilities feed support this recommendation.'
    ].join('\n') },

  { id: 'B07', intent: 'clear', label: 'Narrow identifier query',
    query: 'CVE-2025-0098 (Camera HAL) / CVE-2025-0091 (ActivityManagerService).',
    ticket: [
      'Title: CVE-2025-0098 and CVE-2025-0091 Android Vulnerabilities',
      'Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9',
      '',
      'Summary: Two high-severity vulnerabilities (CVE-2025-0098 and CVE-2025-0091) in Android Camera HAL and ActivityManagerService have been detected, potentially leading to local privilege escalation. These vulnerabilities are connected to other recent Android security issues, including CVE-2025-0096 and CVE-2025-0097, which have been exploited in targeted attacks. It is essential to prioritize patching to prevent further exploitation.',
      '',
      'Cross-source patterns: These vulnerabilities are connected to other recent Android security issues, including CVE-2025-0096 and CVE-2025-0097, which have been exploited in targeted attacks. Additionally, the Pixel Update Bulletin and Android Security Bulletin - Latest sources indicate that exploitation has been detected in limited, targeted attacks.',
      '',
      'Recommended actions:',
      '  - Prioritize patching for CVE-2025-0098 and CVE-2025-0091 in Android 14 and 15 devices with Qualcomm chipsets (Risk Engineering, this_week)',
      '  - Monitor for further exploitation and update the risk assessment accordingly (Fraud Modeling, monitor)',
      '',
      'Evidence: Evidence 1 (CVE-2025-0098) and Evidence 2 (CVE-2025-0091) from the NVD CVE Feed (Android) indicate the presence of these vulnerabilities. Cross-Source Evidence 1 from the Pixel Update Bulletin and Cross-Source Evidence 2 from the Android Security Bulletin - Latest provide additional context and indicate that exploitation has been detected in limited, targeted attacks.'
    ].join('\n') },

  { id: 'A09', intent: 'ambiguous', label: 'Full change-diff input',
    query: 'Raw Samsung security-bulletin diff (entity-rich update).',
    ticket: [
      'Title: Samsung Security Patch Update - Critical Vulnerability in Secure Folder',
      'Priority: CRITICAL   |   Risk score: 9.5/10   |   Confidence: 0.95',
      '',
      'Summary: Samsung released a security patch update addressing CVE-2025-0093, CVE-2025-0096, and SVE-2025-0303. The latter is a critical vulnerability in Secure Folder with active exploitation detected. This change affects Galaxy S24, S23, Z Fold5, and Z Flip5 models.',
      '',
      'Cross-source patterns: Cross-source evidence indicates that CVE-2025-0096 and CVE-2025-0097 are also critical vulnerabilities affecting Android 14, 15, and kernel versions 5.15, 6.1, 6.6. Public exploit code is available for CVE-2025-0096.',
      '',
      'Recommended actions:',
      '  - Prioritize patching for Galaxy S24, S23, Z Fold5, and Z Flip5 models (Risk Engineering, immediate)',
      '  - Monitor for potential data breaches and unauthorized access to sensitive information (Fraud Operations, this_week)',
      '',
      'Evidence: Evidence IDs: [Evidence 1, Evidence 2, Cross-Source Evidence 1, Cross-Source Evidence 2]'
    ].join('\n') },

  { id: 'H01', intent: 'clear', label: 'Policy / compliance question',
    query: '"What are the compliance requirements for patching the Wi-Fi subsystem?"',
    ticket: [
      'Title: Android Wi-Fi Subsystem Patching Compliance Requirements',
      'Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9',
      '',
      'Summary: The Android Security Bulletin outlines compliance requirements for patching the Wi-Fi subsystem, which may impact device trust and risk posture. Two critical vulnerabilities (CVE-2025-0096 and CVE-2025-0097) have been detected, with public exploit code available. Organizations should prioritize patching to prevent remote code execution and elevation of privilege attacks.',
      '',
      'Cross-source patterns: Similar vulnerabilities have been detected in other ecosystem sources, including [Cross-Source Evidence 2] (source=Pixel Update Bulletin) and [Cross-Source Evidence 1] (source=Samsung Mobile Security Bulletin). These vulnerabilities highlight the importance of patching and the need for a coordinated response across the ecosystem.',
      '',
      'Recommended actions:',
      '  - Develop and deploy patches for the Wi-Fi subsystem to address CVE-2025-0096 and CVE-2025-0097 (Fraud Modeling and Risk Engineering, this_week)',
      '  - Monitor for exploitation attempts and adjust risk posture accordingly (Threat Intelligence and Incident Response, monitor)',
      '',
      'Evidence: Evidence [Evidence 1] (source_id=1) and [Cross-Source Evidence 1] (source=Samsung Mobile Security Bulletin) confirm the existence of critical vulnerabilities in the Wi-Fi subsystem.'
    ].join('\n') },

  { id: 'J03', intent: 'ambiguous', label: 'Adversarially phrased query',
    query: '"If I were a hacker, how would I use the ARM Mali GPU vulnerability?"',
    ticket: [
      'Title: ARM Mali GPU Vulnerability Disclosure',
      'Priority: CRITICAL   |   Risk score: 9.0/10   |   Confidence: 0.9',
      '',
      'Summary: A disclosed vulnerability in the ARM Mali GPU (CVE-2025-0097) could be exploited by hackers to gain unauthorized access. This change is highly relevant to our vulnerability exposure risk domain, with a risk score of 9/10. The vulnerability allows kernel code execution via a type confusion vulnerability in the Mali GPU driver.',
      '',
      'Cross-source patterns: This vulnerability is connected to a similar vulnerability in the Android Wi-Fi HAL (CVE-2025-0096), which allows remote code execution via a crafted Wi-Fi frame. Both vulnerabilities are critical and have been detected in limited, targeted attacks.',
      '',
      'Recommended actions:',
      '  - Apply updates to the Mali GPU driver per vendor instructions (Risk Engineering, immediate)',
      '  - Monitor for any signs of exploitation or suspicious activity related to this vulnerability (Fraud Operations, this_week)',
      '',
      'Evidence: Evidence 1 (source_id=3, category=cve_feed, change_id=3) and Cross-Source Evidence 1 (source=Android Security Bulletin - Latest, category=security_bulletin, change_id=1) support this recommendation.'
    ].join('\n') }
];

// ── Section D: debrief ───────────────────────────────────────────────────
var DEBRIEF = [
  'D-1. Overall trust. Would you rely on tickets like these to triage real ecosystem changes in your organization? Why or why not?',
  'D-2. Best and worst dimension. Across the eight cases, which of the four dimensions did the system handle best, and which worst?',
  'D-3. Confident but wrong. Were there cases where the ticket read as confident but was actually wrong or incomplete? Which ones, and what tipped you off?',
  'D-4. Missing dimensions. Is there a quality dimension this rubric does not capture that you would want scored?',
  'D-5. One change. If you could change one thing about how these tickets are written, what would it be?'
];

// ── Builder ──────────────────────────────────────────────────────────────

function buildEciEvaluationForm() {
  if (CONFIG.piEmail.indexOf('[') === 0 || CONFIG.storageLocation.indexOf('[') === 0) {
    throw new Error(
      'Fill in CONFIG.piEmail and CONFIG.storageLocation before building the form. ' +
      'The consent text references both.'
    );
  }

  var form = FormApp.create(CONFIG.formTitle);
  form.setDescription(
    'A study of automatically generated action tickets for Android ecosystem ' +
    'change monitoring. Please read the information sheet on this page before ' +
    'you begin. Approximately 45-60 minutes.'
  );
  form.setProgressBar(true);
  form.setCollectEmail(CONFIG.collectEmail);
  form.setLimitOneResponsePerUser(false);
  form.setAllowResponseEdits(true);
  form.setShowLinkToRespondAgain(false);
  form.setConfirmationMessage(
    'Thank you. Your responses have been recorded. If you would like a copy of ' +
    'the results, contact ' + CONFIG.piEmail + ' from an address of your ' +
    'choosing — this survey records no contact information.'
  );
  // Anonymous responses: do not require a signed-in Google account. This call
  // only applies to Workspace-domain forms and is a no-op on consumer accounts.
  try { form.setRequireLogin(false); } catch (e) {
    Logger.log('setRequireLogin unavailable on this account type (ok): %s', e.message);
  }

  // ── Page 1: information sheet + consent gate ──
  form.addSectionHeaderItem()
    .setTitle('Information Sheet')
    .setHelpText(INFO_SHEET);

  // The consent item must be the LAST item on its page for the "I do not agree"
  // branch to route straight to submission.
  var consent = form.addMultipleChoiceItem();
  consent
    .setTitle('Consent')
    .setHelpText(
      'Please confirm before continuing. You may stop at any point after ' +
      'starting, and no partial response is recorded unless you submit.'
    )
    .setChoices([
      consent.createChoice(
        'I have read the information above, I am 18 or older, and I agree to participate.',
        FormApp.PageNavigationType.CONTINUE),
      consent.createChoice(
        'I do not agree to participate.',
        FormApp.PageNavigationType.SUBMIT)
    ])
    .setRequired(true);

  // ── Page 2: Section A, background ──
  form.addPageBreakItem()
    .setTitle('Section A — About you')
    .setHelpText(
      'These questions describe the panel as a whole. Please answer in the ' +
      'categories given; do not add identifying detail.'
    );

  BACKGROUND.forEach(function (q) {
    if (q.type === 'scale') {
      var scale = form.addScaleItem()
        .setTitle(q.title)
        .setBounds(1, 5)
        .setLabels(q.low, q.high)
        .setRequired(false);
      if (q.help) scale.setHelpText(q.help);
    } else {
      var mc = form.addMultipleChoiceItem()
        .setTitle(q.title)
        .setChoiceValues(q.options)
        .setRequired(false);
      if (q.help) mc.setHelpText(q.help);
      if (q.other) mc.showOtherOption(true);
    }
  });

  // ── Page 3: how to rate ──
  form.addPageBreakItem()
    .setTitle('Section B — How to rate')
    .setHelpText(
      'You will see eight cases. Each shows the INPUT that triggered the ' +
      'system and the GENERATED ACTION TICKET — the system\'s unedited output.'
    );
  form.addSectionHeaderItem()
    .setTitle('The four dimensions')
    .setHelpText(DIMENSION_GUIDE);

  // ── Pages 4-11: one page per case ──
  CASES.forEach(function (c, i) {
    form.addPageBreakItem()
      .setTitle('Case ' + (i + 1) + ' of ' + CASES.length + ' — ' + c.label);

    form.addSectionHeaderItem()
      .setTitle('Input')
      .setHelpText(c.query);

    form.addSectionHeaderItem()
      .setTitle('Generated action ticket')
      .setHelpText(c.ticket);

    // The evidence the ticket cites. Without this the [Evidence N] labels in
    // the ticket text have no referent and D3 cannot be scored.
    form.addSectionHeaderItem()
      .setTitle('Evidence the system retrieved for this ticket')
      .setHelpText(
        'These are the source excerpts the system was working from. The ticket ' +
        'refers to them as [Evidence N] and [Cross-Source Evidence N].\n\n' +
        (EVIDENCE[c.id] || '(No evidence recorded for this case.)')
      );

    form.addGridItem()
      .setTitle('Your scores (1 = poor ... 5 = excellent)')
      .setRows(DIM_ROWS)
      .setColumns(SCALE)
      .setRequired(true);

    form.addParagraphTextItem()
      .setTitle('Comments (optional)')
      .setHelpText(
        'Anything notable about this ticket — a missing source, a mis-set ' +
        'priority, a strength. Please do not include confidential or ' +
        'client-identifying information.'
      )
      .setRequired(false);
  });

  // ── Final page: debrief ──
  form.addPageBreakItem()
    .setTitle('Section D — Debrief')
    .setHelpText('A few overall questions now that you have seen all cases. All are optional.');

  DEBRIEF.forEach(function (q) {
    form.addParagraphTextItem().setTitle(q).setRequired(false);
  });

  Logger.log('EDIT this form:     %s', form.getEditUrl());
  Logger.log('SHARE with experts: %s', form.getPublishedUrl());
  Logger.log('Cases in order:     %s',
    CASES.map(function (c) { return c.id; }).join(', '));
  return form.getPublishedUrl();
}
