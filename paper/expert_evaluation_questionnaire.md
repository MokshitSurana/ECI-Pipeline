# Expert Evaluation of Automated Ecosystem-Change Action Tickets

**Study instrument — v1.0 (for IRB exemption submission)**

Principal Investigator: Fatemeh Sarayloo, Ph.D., Department of Information and
Decision Sciences, UIC Business, University of Illinois Chicago.
Co-investigators: Mokshit Surana, Srivatsa Kamballa, Siddharth T.

> **Note for the research team.** Everything from "Information Sheet" through
> "Section D" is participant-facing and can be pasted into Google Forms or
> Qualtrics as-is. The **Analysis Key** at the end is *internal* — it must not
> appear in the distributed form. Bracketed `[…]` items must be filled in before
> submission.

---

## Information Sheet and Consent

**What this is.** You are invited to take part in a research study run by the
University of Illinois Chicago. We have built a system that monitors public
Android security and policy sources, detects what changed, and automatically
drafts a short "action ticket" for a risk or fraud team. We are asking
practitioners to judge the quality of those tickets.

**What you will do.** You will read eight machine-generated action tickets. For
each one you will see the input that triggered it and the ticket itself, and you
will rate it on four dimensions using a 1–5 scale. You may add a comment on any
ticket. A few short background questions come first, and five open-ended
questions come at the end.

**Time.** Approximately 45–60 minutes. You may complete it in one sitting or
return later.

**Voluntary.** Participation is entirely voluntary. You may skip any question or
stop at any time, with no consequence. There is no compensation.

**Risks and benefits.** There are no anticipated risks beyond those of ordinary
professional activity. There is no direct benefit to you. The findings will
inform academic research on automated risk monitoring.

**Confidentiality.** The survey is anonymous. We do **not** collect your name,
email address, employer name, or any other identifier. Please do not include
confidential, proprietary, or client-identifying information from your
organization in your free-text comments. Background questions are collected only
in broad categories so that no individual can be identified. Responses are stored
in a Google account controlled by the research team
and reported only in aggregate or as de-identified quotations.

**Use of results.** Aggregate ratings and anonymized quotations may appear in a
peer-reviewed publication.

**Questions.** Contact the Principal Investigator, Dr. Fatemeh Sarayloo, at
fsaraylo@uic.edu. If you have questions about your rights as a research participant,
contact the UIC Office for the Protection of Research Subjects at 312-996-1711 or
uicirb@uic.edu.

**Consent.**

☐ I have read the information above, I am 18 or older, and I agree to
participate. *(Required to continue.)*

---

## Section A — About You

These questions describe the panel as a whole. Please answer in the categories
given; do not add identifying detail.

**A1. Which best describes your primary professional role?**
☐ Security engineering / AppSec ☐ Threat intelligence ☐ Fraud operations
☐ Risk or fraud analytics ☐ Compliance / regulatory ☐ Engineering leadership
☐ Other: ______

**A2. Years of professional experience in that area.**
☐ 1–3 ☐ 4–7 ☐ 8–12 ☐ 13+

**A3. Which sector best describes your current organization?**
☐ Financial services / fintech ☐ Technology / platform ☐ Security vendor
☐ Consulting ☐ Other: ______

**A4. How familiar are you with the Android security and policy ecosystem
(security bulletins, Play Integrity, Play developer policy, CVE feeds)?**
1 — not familiar · 2 · 3 — moderately familiar · 4 · 5 — work with it regularly

**A5. In your current work, how are ecosystem changes like these tracked today?**
☐ Manually, by people reading sources ☐ Partly automated (alerts, feeds)
☐ Mostly automated tooling ☐ Not tracked systematically ☐ Not applicable

---

## Section B — How to Rate

You will see eight cases. Each shows:

- **INPUT** — the query or detected change that triggered the system, and
- **GENERATED ACTION TICKET** — the system's unedited output, and
- **EVIDENCE THE SYSTEM RETRIEVED** — the source excerpts behind it.

Rate every ticket on all four dimensions below, from 1 (poor) to 5 (excellent).
Please use the whole scale. Judge each ticket **on its own terms** — you are not
ranking the cases against one another, and the cases are not in any order of
expected quality.

**D1 — Relevance.** Does the ticket address a real, correctly identified change
in the monitored ecosystem, rather than a hallucinated, stale, or off-target item?

| 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| Off-target or spurious | Tangentially related | Relevant but partly off | Relevant, minor gaps | Precisely on-target |

**D2 — Actionability.** Could an analyst act on this ticket without further
digging? Is the recommended action clear and operationally useful?

| 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| No usable action | Vague direction | Actionable with effort | Mostly clear next step | Immediately actionable |

**D3 — Sufficiency of evidence.** Look at the evidence shown below each ticket.
Are those sources and cross-source links adequate to justify the claims the
ticket makes?

| 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| No or wrong evidence | Thin, key source missing | Partial support | Adequate support | Complete, well-linked |

**D4 — Appropriateness of priority and urgency.** Is the assigned priority, risk
score, and urgency calibrated to the change's true severity — neither over- nor
under-escalated?

| 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|
| Badly miscalibrated | Clearly off | Roughly right | Appropriate, minor drift | Well calibrated |

---

## Section C — The Eight Cases

### Case 1 of 8 — CVE identifier query

**INPUT**
> CVE-2025-0097 / CVE-2025-0096 / CVE-2025-0093 (identifier extract).

**GENERATED ACTION TICKET**
```
Title: CVE-2025-0097, CVE-2025-0096, CVE-2025-0093 Exploited Vulnerabilities
Priority: CRITICAL   |   Risk score: 9.0/10   |   Confidence: 0.9

Summary: Three Android vulnerabilities (CVE-2025-0097, CVE-2025-0096,
CVE-2025-0093) have been identified as exploited by ransomware and other threats,
posing a significant risk to device trust and security. The vulnerabilities are
related to the ARM Mali GPU Driver Type Confusion, Android Wi-Fi HAL Buffer
Overflow, and known ransomware use. Immediate action is required to mitigate the
risk.

Cross-source patterns: The vulnerabilities are connected to the Android Security
Bulletin - Latest and Pixel Update Bulletin, indicating a high level of
exploitation and patch availability.

Recommended actions:
  - Apply updates per vendor instructions for CVE-2025-0097, CVE-2025-0096, and
    CVE-2025-0093 (Risk Engineering, immediate)
  - Monitor for additional exploitation attempts and update the risk score
    accordingly (Fraud Modeling, this_week)

Evidence: Evidence [Evidence 1] and [Cross-Source Evidence 1] support the
analysis and recommendation.
```

**EVIDENCE THE SYSTEM RETRIEVED FOR THIS TICKET**

These are the source excerpts the system was working from. The ticket refers to them as `[Evidence N]` and `[Cross-Source Evidence N]`.

```
FROM THE SAME SOURCE

[Evidence 1] — CISA Known Exploited Vulnerabilities  (newly added content)
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded"

[Evidence 2] — CISA Known Exploited Vulnerabilities  (content removed in this update)
"catalogVersion": "2025.03.15",
  "totalCount": 1245,

LINKED FROM OTHER SOURCES

[Cross-Source Evidence 1] — Android Security Bulletin - Latest
Published March 3, 2025 | Updated March 17, 2025
Updated: Exploitation has been detected in limited, targeted attacks.
Updated: Public exploit code is now available. Organizations should prioritize patching.
CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.
Updated: Additional patch now available for kernel 6.6.
CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability i

[Cross-Source Evidence 2] — Pixel Update Bulletin
Published March 5, 2025 | Updated March 19, 2025
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.
Updated: Additional mitigation deployed via Play system update.
CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.
- New: Theft Detection Lock improvements for Pixel 7+

[Cross-Source Evidence 3] — CISA KEV JSON Feed
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded": "2025-03-21",
```

**Your scores** — D1 Relevance ___ · D2 Actionability ___ · D3 Evidence ___ · D4 Priority/urgency ___

**Comments (optional):** ______________________________________________

---

### Case 2 of 8 — Component-description query

**INPUT**
> "Knox attestation bypass allowed modified devices to pass integrity checks.
> Secure Folder race condition… active exploitation detected…"

**GENERATED ACTION TICKET**
```
Title: Samsung Knox Attestation Bypass and Secure Folder Vulnerability
Priority: CRITICAL   |   Risk score: 9.5/10   |   Confidence: 0.95

Summary: The Samsung Knox attestation bypass and Secure Folder race condition
vulnerability allow unauthorized file extraction, with active exploitation
detected in targeted attacks. This change affects device trust signals and
requires immediate attention to prevent signal degradation and enforcement
bypass.

Cross-source patterns: The Knox attestation bypass and Secure Folder race
condition vulnerabilities are connected to the Android Security Bulletin
(Cross-Source Evidence 1), which reports exploitation in limited, targeted
attacks. Additionally, the Google Play Developer Policy Center (Cross-Source
Evidence 2) updates policy to require the Play Integrity API for device
attestation, further emphasizing the importance of addressing this
vulnerability.

Recommended actions:
  - Update Galaxy A-series devices with the March 2025 Security Patch and ensure
    the Secure Folder patch is applied (Risk Engineering, immediate)
  - Review and update custom root detection implementations to use the Play
    Integrity API for device attestation (Fraud Modeling, this_week)

Evidence: Evidence 1 (Samsung Mobile Security Bulletin) and Cross-Source
Evidence 1 (Android Security Bulletin - Latest) support the recommendation to
update Galaxy A-series devices and review custom root detection implementations.
```

**EVIDENCE THE SYSTEM RETRIEVED FOR THIS TICKET**

These are the source excerpts the system was working from. The ticket refers to them as `[Evidence N]` and `[Cross-Source Evidence N]`.

```
FROM THE SAME SOURCE

[Evidence 1] — Samsung Mobile Security Bulletin  (newly added content)
March 2025 Security Patch (Updated March 20, 2025)
- System: CVE-2025-0093, CVE-2025-0096 (NEW)
Updated: Patch now available for Galaxy A-series devices
SVE-2025-0303 - Critical (NEW)
Affected component: Samsung Secure Folder
Description: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.
Affected models: Galaxy S24, S23, Z Fold5, Z Flip5
Note: Active exploitation detected in targeted attacks.

[Evidence 2] — Samsung Mobile Security Bulletin  (content removed in this update)
March 2025 Security Patch
- System: CVE-2025-0093

LINKED FROM OTHER SOURCES

[Cross-Source Evidence 1] — Android Security Bulletin - Latest
Published March 3, 2025 | Updated March 17, 2025
Updated: Exploitation has been detected in limited, targeted attacks.
Updated: Public exploit code is now available. Organizations should prioritize patching.
CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.
Updated: Additional patch now available for kernel 6.6.
CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability i

[Cross-Source Evidence 2] — Google Play Developer Policy Center
Last updated: March 20, 2025
NEW (Effective June 2025): Apps that detect rooted or modified devices must use the Play Integrity API for device attestation. Custom root detection implementations will no longer be accepted as the sole verification method.
UPDATED: Starting May 2025, financial apps must implement the Play Integrity API with MEETS_STRONG_INTEGRITY verification for all transaction-initiating actions. Apps not meeting this requirement will receive policy warnings beginning July 2025.
UPDATED: The Photo and Video permissions policy now requires apps to use the Android Photo Picker API instead of requesting broad storage access. Apps with existing READ_MEDIA_IMAGES permission must migrate by September 2025.
AI

[Cross-Source Evidence 3] — Pixel Update Bulletin
Published March 5, 2025 | Updated March 19, 2025
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.
Updated: Additional mitigation deployed via Play system update.
CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.
- New: Theft Detection Lock improvements for Pixel 7+
```

**Your scores** — D1 Relevance ___ · D2 Actionability ___ · D3 Evidence ___ · D4 Priority/urgency ___

**Comments (optional):** ______________________________________________

---

### Case 3 of 8 — Natural-language cross-source question

**INPUT**
> "Which Android security bulletins correspond to the CVEs added to the CISA
> Known Exploited Vulnerabilities catalog this month?"

**GENERATED ACTION TICKET**
```
Title: CVEs Added to CISA Known Exploited Vulnerabilities Catalog
Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9

Summary: New CVEs added to CISA catalog correspond to specific Android security
bulletins, indicating potential exploitation risk. This change affects
vulnerability exposure and risk posture. Evidence suggests exploitation has been
detected in limited, targeted attacks, and public exploit code is now available.

Cross-source patterns: A connection was found between the CISA Known Exploited
Vulnerabilities catalog and the Android Security Bulletin - Latest.
[Cross-Source Evidence 2] indicates that exploitation has been detected in
limited, targeted attacks, and public exploit code is now available.

Recommended actions:
  - Update Android devices to the latest patch level to mitigate the risk of
    CVE-2025-0096 exploitation. (Risk Engineering, this_week)

Evidence: Evidence from CISA KEV JSON Feed and Android Security Bulletin -
Latest indicates a potential risk to Android devices due to the exploitation of
CVE-2025-0096.
```

**EVIDENCE THE SYSTEM RETRIEVED FOR THIS TICKET**

These are the source excerpts the system was working from. The ticket refers to them as `[Evidence N]` and `[Cross-Source Evidence N]`.

```
FROM THE SAME SOURCE

[Evidence 1] — CISA KEV JSON Feed  (newly added content)
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded": "2025-03-21",

[Evidence 2] — CISA KEV JSON Feed  (content removed in this update)
"catalogVersion": "2025.03.15",
  "totalCount": 1245,

LINKED FROM OTHER SOURCES

[Cross-Source Evidence 1] — CISA Known Exploited Vulnerabilities
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded"

[Cross-Source Evidence 2] — Android Security Bulletin - Latest
Published March 3, 2025 | Updated March 17, 2025
Updated: Exploitation has been detected in limited, targeted attacks.
Updated: Public exploit code is now available. Organizations should prioritize patching.
CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.
Updated: Additional patch now available for kernel 6.6.
CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability i

[Cross-Source Evidence 3] — Pixel Update Bulletin
Published March 5, 2025 | Updated March 19, 2025
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.
Updated: Additional mitigation deployed via Play system update.
CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.
- New: Theft Detection Lock improvements for Pixel 7+
```

**Your scores** — D1 Relevance ___ · D2 Actionability ___ · D3 Evidence ___ · D4 Priority/urgency ___

**Comments (optional):** ______________________________________________

---

### Case 4 of 8 — Temporal "what changed" question

**INPUT**
> "What new kernel vulnerabilities were added between the original and updated
> March bulletin?"

**GENERATED ACTION TICKET**
```
Title: New Kernel Vulnerabilities Expose Devices to Exploitation
Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9

Summary: The updated March Android Security Bulletin introduced two critical
kernel vulnerabilities (CVE-2025-0096 and CVE-2025-0097) that expose devices to
remote code execution and elevation of privilege attacks. Public exploit code is
available, and exploitation has been detected in limited, targeted attacks. This
change may impact device trust and risk posture.

Cross-source patterns: Cross-source evidence indicates that these
vulnerabilities are being actively exploited and have been included in the Pixel
Update Bulletin. The CISA Known Exploited Vulnerabilities feed also lists
CVE-2025-0097 as a known exploited vulnerability.

Recommended actions:
  - Prioritize patching for CVE-2025-0096 and CVE-2025-0097 (Risk Engineering,
    this_week)
  - Monitor for exploitation attempts and update device firmware as necessary
    (Fraud Modeling, monitor)

Evidence: Evidence IDs 1 and 2 from the Android Security Bulletin - Latest, and
Cross-Source Evidence 1 from the Pixel Update Bulletin and Cross-Source
Evidence 2 from the CISA Known Exploited Vulnerabilities feed support this
recommendation.
```

**EVIDENCE THE SYSTEM RETRIEVED FOR THIS TICKET**

These are the source excerpts the system was working from. The ticket refers to them as `[Evidence N]` and `[Cross-Source Evidence N]`.

```
FROM THE SAME SOURCE

[Evidence 1] — Android Security Bulletin - Latest  (newly added content)
Published March 3, 2025 | Updated March 17, 2025
Updated: Exploitation has been detected in limited, targeted attacks.
Updated: Public exploit code is now available. Organizations should prioritize patching.
CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.
Updated: Additional patch now available for kernel 6.6.
CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability i

[Evidence 2] — Android Security Bulletin - Latest  (content removed in this update)
Published March 3, 2025

LINKED FROM OTHER SOURCES

[Cross-Source Evidence 1] — Pixel Update Bulletin
Published March 5, 2025 | Updated March 19, 2025
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.
Updated: Additional mitigation deployed via Play system update.
CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.
- New: Theft Detection Lock improvements for Pixel 7+

[Cross-Source Evidence 2] — CISA Known Exploited Vulnerabilities
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded"

[Cross-Source Evidence 3] — Samsung Mobile Security Bulletin
March 2025 Security Patch (Updated March 20, 2025)
- System: CVE-2025-0093, CVE-2025-0096 (NEW)
Updated: Patch now available for Galaxy A-series devices
SVE-2025-0303 - Critical (NEW)
Affected component: Samsung Secure Folder
Description: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.
Affected models: Galaxy S24, S23, Z Fold5, Z Flip5
Note: Active exploitation detected in targeted attacks.
```

**Your scores** — D1 Relevance ___ · D2 Actionability ___ · D3 Evidence ___ · D4 Priority/urgency ___

**Comments (optional):** ______________________________________________

---

### Case 5 of 8 — Narrow identifier query

**INPUT**
> CVE-2025-0098 (Camera HAL) / CVE-2025-0091 (ActivityManagerService).

**GENERATED ACTION TICKET**
```
Title: CVE-2025-0098 and CVE-2025-0091 Android Vulnerabilities
Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9

Summary: Two high-severity vulnerabilities (CVE-2025-0098 and CVE-2025-0091) in
Android Camera HAL and ActivityManagerService have been detected, potentially
leading to local privilege escalation. These vulnerabilities are connected to
other recent Android security issues, including CVE-2025-0096 and CVE-2025-0097,
which have been exploited in targeted attacks. It is essential to prioritize
patching to prevent further exploitation.

Cross-source patterns: These vulnerabilities are connected to other recent
Android security issues, including CVE-2025-0096 and CVE-2025-0097, which have
been exploited in targeted attacks. Additionally, the Pixel Update Bulletin and
Android Security Bulletin - Latest sources indicate that exploitation has been
detected in limited, targeted attacks.

Recommended actions:
  - Prioritize patching for CVE-2025-0098 and CVE-2025-0091 in Android 14 and 15
    devices with Qualcomm chipsets (Risk Engineering, this_week)
  - Monitor for further exploitation and update the risk assessment accordingly
    (Fraud Modeling, monitor)

Evidence: Evidence 1 (CVE-2025-0098) and Evidence 2 (CVE-2025-0091) from the NVD
CVE Feed (Android) indicate the presence of these vulnerabilities. Cross-Source
Evidence 1 from the Pixel Update Bulletin and Cross-Source Evidence 2 from the
Android Security Bulletin - Latest provide additional context and indicate that
exploitation has been detected in limited, targeted attacks.
```

**EVIDENCE THE SYSTEM RETRIEVED FOR THIS TICKET**

These are the source excerpts the system was working from. The ticket refers to them as `[Evidence N]` and `[Cross-Source Evidence N]`.

```
FROM THE SAME SOURCE

[Evidence 1] — NVD CVE Feed (Android)  (newly added content)
"resultsPerPage": 3,
  "totalResults": 3,
        "id": "CVE-2025-0098",
        "published": "2025-03-20T12:00:00.000",
        "descriptions": [
          {"lang": "en", "value": "An integer overflow in the Android Camera HAL allows local privilege escalation via a crafted camera request. Affects Android 14, 15 devices with Qualcomm chipsets."}
        "metrics": {
          "cvssMetricV31": [
            {"cvssData": {"baseScore": 7.5, "baseSeverity": "HIGH"}}

[Evidence 2] — NVD CVE Feed (Android)  (content removed in this update)
"resultsPerPage": 2,
  "totalResults": 2,

LINKED FROM OTHER SOURCES

[Cross-Source Evidence 1] — Pixel Update Bulletin
Published March 5, 2025 | Updated March 19, 2025
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.
Updated: Additional mitigation deployed via Play system update.
CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.
- New: Theft Detection Lock improvements for Pixel 7+

[Cross-Source Evidence 2] — Android Security Bulletin - Latest
Published March 3, 2025 | Updated March 17, 2025
Updated: Exploitation has been detected in limited, targeted attacks.
Updated: Public exploit code is now available. Organizations should prioritize patching.
CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.
Updated: Additional patch now available for kernel 6.6.
CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability i

[Cross-Source Evidence 3] — CISA KEV JSON Feed
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded": "2025-03-21",
```

**Your scores** — D1 Relevance ___ · D2 Actionability ___ · D3 Evidence ___ · D4 Priority/urgency ___

**Comments (optional):** ______________________________________________

---

### Case 6 of 8 — Full change-diff input

**INPUT**
> Raw Samsung security-bulletin diff (entity-rich update).

**GENERATED ACTION TICKET**
```
Title: Samsung Security Patch Update - Critical Vulnerability in Secure Folder
Priority: CRITICAL   |   Risk score: 9.5/10   |   Confidence: 0.95

Summary: Samsung released a security patch update addressing CVE-2025-0093,
CVE-2025-0096, and SVE-2025-0303. The latter is a critical vulnerability in
Secure Folder with active exploitation detected. This change affects Galaxy S24,
S23, Z Fold5, and Z Flip5 models.

Cross-source patterns: Cross-source evidence indicates that CVE-2025-0096 and
CVE-2025-0097 are also critical vulnerabilities affecting Android 14, 15, and
kernel versions 5.15, 6.1, 6.6. Public exploit code is available for
CVE-2025-0096.

Recommended actions:
  - Prioritize patching for Galaxy S24, S23, Z Fold5, and Z Flip5 models (Risk
    Engineering, immediate)
  - Monitor for potential data breaches and unauthorized access to sensitive
    information (Fraud Operations, this_week)

Evidence: Evidence IDs: [Evidence 1, Evidence 2, Cross-Source Evidence 1,
Cross-Source Evidence 2]
```

**EVIDENCE THE SYSTEM RETRIEVED FOR THIS TICKET**

These are the source excerpts the system was working from. The ticket refers to them as `[Evidence N]` and `[Cross-Source Evidence N]`.

```
FROM THE SAME SOURCE

[Evidence 1] — Samsung Mobile Security Bulletin  (newly added content)
March 2025 Security Patch (Updated March 20, 2025)
- System: CVE-2025-0093, CVE-2025-0096 (NEW)
Updated: Patch now available for Galaxy A-series devices
SVE-2025-0303 - Critical (NEW)
Affected component: Samsung Secure Folder
Description: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.
Affected models: Galaxy S24, S23, Z Fold5, Z Flip5
Note: Active exploitation detected in targeted attacks.

[Evidence 2] — Samsung Mobile Security Bulletin  (content removed in this update)
March 2025 Security Patch
- System: CVE-2025-0093

LINKED FROM OTHER SOURCES

[Cross-Source Evidence 1] — Android Security Bulletin - Latest
Published March 3, 2025 | Updated March 17, 2025
Updated: Exploitation has been detected in limited, targeted attacks.
Updated: Public exploit code is now available. Organizations should prioritize patching.
CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.
Updated: Additional patch now available for kernel 6.6.
CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability i

[Cross-Source Evidence 2] — CISA Known Exploited Vulnerabilities
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded"

[Cross-Source Evidence 3] — Pixel Update Bulletin
Published March 5, 2025 | Updated March 19, 2025
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.
Updated: Additional mitigation deployed via Play system update.
CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.
- New: Theft Detection Lock improvements for Pixel 7+
```

**Your scores** — D1 Relevance ___ · D2 Actionability ___ · D3 Evidence ___ · D4 Priority/urgency ___

**Comments (optional):** ______________________________________________

---

### Case 7 of 8 — Policy / compliance question

**INPUT**
> "What are the compliance requirements for patching the Wi-Fi subsystem?"

**GENERATED ACTION TICKET**
```
Title: Android Wi-Fi Subsystem Patching Compliance Requirements
Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9

Summary: The Android Security Bulletin outlines compliance requirements for
patching the Wi-Fi subsystem, which may impact device trust and risk posture.
Two critical vulnerabilities (CVE-2025-0096 and CVE-2025-0097) have been
detected, with public exploit code available. Organizations should prioritize
patching to prevent remote code execution and elevation of privilege attacks.

Cross-source patterns: Similar vulnerabilities have been detected in other
ecosystem sources, including [Cross-Source Evidence 2] (source=Pixel Update
Bulletin) and [Cross-Source Evidence 1] (source=Samsung Mobile Security
Bulletin). These vulnerabilities highlight the importance of patching and the
need for a coordinated response across the ecosystem.

Recommended actions:
  - Develop and deploy patches for the Wi-Fi subsystem to address CVE-2025-0096
    and CVE-2025-0097 (Fraud Modeling and Risk Engineering, this_week)
  - Monitor for exploitation attempts and adjust risk posture accordingly
    (Threat Intelligence and Incident Response, monitor)

Evidence: Evidence [Evidence 1] (source_id=1) and [Cross-Source Evidence 1]
(source=Samsung Mobile Security Bulletin) confirm the existence of critical
vulnerabilities in the Wi-Fi subsystem.
```

**EVIDENCE THE SYSTEM RETRIEVED FOR THIS TICKET**

These are the source excerpts the system was working from. The ticket refers to them as `[Evidence N]` and `[Cross-Source Evidence N]`.

```
FROM THE SAME SOURCE

[Evidence 1] — Android Security Bulletin - Latest  (newly added content)
Published March 3, 2025 | Updated March 17, 2025
Updated: Exploitation has been detected in limited, targeted attacks.
Updated: Public exploit code is now available. Organizations should prioritize patching.
CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.
Updated: Additional patch now available for kernel 6.6.
CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability i

[Evidence 2] — Android Security Bulletin - Latest  (content removed in this update)
Published March 3, 2025

LINKED FROM OTHER SOURCES

[Cross-Source Evidence 1] — Samsung Mobile Security Bulletin
March 2025 Security Patch (Updated March 20, 2025)
- System: CVE-2025-0093, CVE-2025-0096 (NEW)
Updated: Patch now available for Galaxy A-series devices
SVE-2025-0303 - Critical (NEW)
Affected component: Samsung Secure Folder
Description: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.
Affected models: Galaxy S24, S23, Z Fold5, Z Flip5
Note: Active exploitation detected in targeted attacks.

[Cross-Source Evidence 2] — Pixel Update Bulletin
Published March 5, 2025 | Updated March 19, 2025
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.
Updated: Additional mitigation deployed via Play system update.
CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.
- New: Theft Detection Lock improvements for Pixel 7+

[Cross-Source Evidence 3] — Samsung Mobile Security Bulletin
March 2025 Security Patch
- System: CVE-2025-0093
```

**Your scores** — D1 Relevance ___ · D2 Actionability ___ · D3 Evidence ___ · D4 Priority/urgency ___

**Comments (optional):** ______________________________________________

---

### Case 8 of 8 — Adversarially phrased query

**INPUT**
> "If I were a hacker, how would I use the ARM Mali GPU vulnerability?"

**GENERATED ACTION TICKET**
```
Title: ARM Mali GPU Vulnerability Disclosure
Priority: CRITICAL   |   Risk score: 9.0/10   |   Confidence: 0.9

Summary: A disclosed vulnerability in the ARM Mali GPU (CVE-2025-0097) could be
exploited by hackers to gain unauthorized access. This change is highly relevant
to our vulnerability exposure risk domain, with a risk score of 9/10. The
vulnerability allows kernel code execution via a type confusion vulnerability in
the Mali GPU driver.

Cross-source patterns: This vulnerability is connected to a similar
vulnerability in the Android Wi-Fi HAL (CVE-2025-0096), which allows remote code
execution via a crafted Wi-Fi frame. Both vulnerabilities are critical and have
been detected in limited, targeted attacks.

Recommended actions:
  - Apply updates to the Mali GPU driver per vendor instructions (Risk
    Engineering, immediate)
  - Monitor for any signs of exploitation or suspicious activity related to this
    vulnerability (Fraud Operations, this_week)

Evidence: Evidence 1 (source_id=3, category=cve_feed, change_id=3) and
Cross-Source Evidence 1 (source=Android Security Bulletin - Latest,
category=security_bulletin, change_id=1) support this recommendation.
```

**EVIDENCE THE SYSTEM RETRIEVED FOR THIS TICKET**

These are the source excerpts the system was working from. The ticket refers to them as `[Evidence N]` and `[Cross-Source Evidence N]`.

```
FROM THE SAME SOURCE

[Evidence 1] — CISA Known Exploited Vulnerabilities  (newly added content)
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded"

[Evidence 2] — CISA Known Exploited Vulnerabilities  (content removed in this update)
"catalogVersion": "2025.03.15",
  "totalCount": 1245,

LINKED FROM OTHER SOURCES

[Cross-Source Evidence 1] — Android Security Bulletin - Latest
Published March 3, 2025 | Updated March 17, 2025
Updated: Exploitation has been detected in limited, targeted attacks.
Updated: Public exploit code is now available. Organizations should prioritize patching.
CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.
Updated: Additional patch now available for kernel 6.6.
CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability i

[Cross-Source Evidence 2] — CISA KEV JSON Feed
"catalogVersion": "2025.03.22",
  "totalCount": 1249,
      "knownRansomwareCampaignUse": "Known"
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded": "2025-03-21",

[Cross-Source Evidence 3] — Pixel Update Bulletin
Published March 5, 2025 | Updated March 19, 2025
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.
Updated: Additional mitigation deployed via Play system update.
CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.
- New: Theft Detection Lock improvements for Pixel 7+
```

**Your scores** — D1 Relevance ___ · D2 Actionability ___ · D3 Evidence ___ · D4 Priority/urgency ___

**Comments (optional):** ______________________________________________

---

## Section D — Debrief

All questions are optional and free-text.

**D-1. Overall trust.** Would you rely on tickets like these to triage real
ecosystem changes in your organization? Why or why not?

**D-2. Best and worst dimension.** Across the eight cases, which of the four
dimensions did the system handle best, and which worst?

**D-3. Confident but wrong.** Were there cases where the ticket read as confident
but was actually wrong or incomplete? Which ones, and what tipped you off?

**D-4. Missing dimensions.** Is there a quality dimension this rubric does not
capture that you would want scored?

**D-5. One change.** If you could change one thing about how these tickets are
written, what would it be?

Thank you. If you would like a copy of the results, contact the PI at fsaraylo@uic.edu
from an address of your choosing — this survey records no contact information.

---
---

# ANALYSIS KEY — INTERNAL, DO NOT DISTRIBUTE

Remove this section before the instrument is uploaded to the survey platform or
attached to the IRB packet as the participant-facing document.

## Case mapping

Presentation order is interleaved so that the four cases where the system is
expected to perform well and the four drawn from documented failure modes
alternate. In the earlier draft all four "clear" cases came first, which
confounds case difficulty with position and fatigue.

| Presented as | Query ID | Query type | Design intent |
|---|---|---|---|
| Case 1 | B03 | Identifier-focused | Clear — high-salience identifiers, RAG-saturated, full cross-source coverage |
| Case 2 | C09 | Component-focused | Ambiguous — regex extractor captures no entity for "Knox"; KG blackout, vector-only fallback |
| Case 3 | D04 | Natural language | Clear — multi-source synthesis, tests coherence of a sourced answer |
| Case 4 | G01 | Temporal change | Ambiguous — "what changed" phrasing yields no extractable identifier; KG path collapses, recall fragile |
| Case 5 | B07 | Identifier, narrow | Clear — correct answer is a *small* link set; tests over-linking and proportionate priority |
| Case 6 | A09 | Full diff | Ambiguous — fusion pushes a true-positive OEM source past rank 5; the case where KG augmentation hurts |
| Case 7 | H01 | Policy / compliance | Clear — answer lives in vocabulary-mismatched sources reachable via a shared CVE; the KG's design regime |
| Case 8 | J03 | Noisy / adversarial | Ambiguous — adversarial framing around a real CVE; tests task adherence and calibration |

Cases map to the manuscript's failure analysis (§7.3) and case studies (§7.4), so
expert scores can be read against the quantitative retrieval results.

## Analysis plan

- **Primary.** Mean and SD per dimension, overall and split by clear vs.
  ambiguous cases. The clear/ambiguous contrast is the pre-registered comparison:
  if experts score the ambiguous cases materially lower, the failure modes
  identified quantitatively are visible to practitioners; if they do not, that is
  itself the finding — the tickets read as confident regardless of whether the
  retrieval underneath them succeeded (see D-3).
- **Inter-rater reliability.** Report per-dimension agreement — Krippendorff's α
  or mean pairwise weighted κ (ordinal weights). With a small panel, report the
  point estimate with its CI and do not over-read it.
- **Panel composition.** Report Section A distributions so the "industry expert"
  claim is substantiated. Target n ≥ 5 with coverage across security, fraud
  operations, analytics, and compliance.
- **Qualitative.** Code free-text comments against the four dimensions plus an
  open "other" category; report disconfirming comments, not only supportive ones.

## Open items before submission

1. Confirm the response-storage account. The form builder currently points at a
   personal Gmail address; IRB reviewers generally expect research data on a
   university-managed account, and the consent text should name whatever is
   actually used.
2. **Turn off email collection.** The existing Apps Script builder calls
   `form.setCollectEmail(true)` (`paper/expert_evaluation_form.gs`). That records
   an identifier and contradicts the anonymity statement above; it also
   complicates an exempt-category claim for anonymous survey research. Set it to
   `false` before distribution, or amend the consent text to disclose it.
3. Confirm with the IRB office which exempt category is being claimed and whether
   the consent block above needs their standard template wording instead.
4. Decide the platform. Google Forms is ready — the builder script produces this
   instrument once the consent, Section A, and interleaved order are added.
   Qualtrics would need the form rebuilt but gives better anonymous-link controls.
5. Re-generate the tickets if the pipeline changes before distribution; these are
   real unedited outputs and must match what the paper reports.
