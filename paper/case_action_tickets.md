# Generated Action Tickets (expert-evaluation cases)

Produced by the real Sentinel + Coordinator pipeline on the isolated eval DB. Paste-ready copies are embedded in `expert_evaluation_form.gs`.

## H01
```
Title: Android Wi-Fi Subsystem Patching Compliance Requirements
Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9

Summary: The Android Security Bulletin outlines compliance requirements for patching the Wi-Fi subsystem, which may impact device trust and risk posture. Two critical vulnerabilities (CVE-2025-0096 and CVE-2025-0097) have been detected, with public exploit code available. Organizations should prioritize patching to prevent remote code execution and elevation of privilege attacks.
Cross-source patterns: Similar vulnerabilities have been detected in other ecosystem sources, including [Cross-Source Evidence 2] (source=Pixel Update Bulletin) and [Cross-Source Evidence 1] (source=Samsung Mobile Security Bulletin). These vulnerabilities highlight the importance of patching and the need for a coordinated response across the ecosystem.
Recommended actions:
  - Develop and deploy patches for the Wi-Fi subsystem to address CVE-2025-0096 and CVE-2025-0097 (Fraud Modeling and Risk Engineering, this_week)
  - Monitor for exploitation attempts and adjust risk posture accordingly (Threat Intelligence and Incident Response, monitor)
Evidence: Evidence [Evidence 1] (source_id=1) and [Cross-Source Evidence 1] (source=Samsung Mobile Security Bulletin) confirm the existence of critical vulnerabilities in the Wi-Fi subsystem.
```

## B03
```
Title: CVE-2025-0097, CVE-2025-0096, CVE-2025-0093 Exploited Vulnerabilities
Priority: CRITICAL   |   Risk score: 9.0/10   |   Confidence: 0.9

Summary: Three Android vulnerabilities (CVE-2025-0097, CVE-2025-0096, CVE-2025-0093) have been identified as exploited by ransomware and other threats, posing a significant risk to device trust and security. The vulnerabilities are related to the ARM Mali GPU Driver Type Confusion, Android Wi-Fi HAL Buffer Overflow, and known ransomware use. Immediate action is required to mitigate the risk.
Cross-source patterns: The vulnerabilities are connected to the Android Security Bulletin - Latest and Pixel Update Bulletin, indicating a high level of exploitation and patch availability.
Recommended actions:
  - Apply updates per vendor instructions for CVE-2025-0097, CVE-2025-0096, and CVE-2025-0093 (Risk Engineering, immediate)
  - Monitor for additional exploitation attempts and update the risk score accordingly (Fraud Modeling, this_week)
Evidence: Evidence [Evidence 1] and [Cross-Source Evidence 1] support the analysis and recommendation.
```

## D04
```
Title: CVEs Added to CISA Known Exploited Vulnerabilities Catalog
Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9

Summary: New CVEs added to CISA catalog correspond to specific Android security bulletins, indicating potential exploitation risk. This change affects vulnerability exposure and risk posture. Evidence suggests exploitation has been detected in limited, targeted attacks, and public exploit code is now available.
Cross-source patterns: A connection was found between the CISA Known Exploited Vulnerabilities catalog and the Android Security Bulletin - Latest. [Cross-Source Evidence 2] indicates that exploitation has been detected in limited, targeted attacks, and public exploit code is now available.
Recommended actions:
  - Update Android devices to the latest patch level to mitigate the risk of CVE-2025-0096 exploitation. (Risk Engineering, this_week)
Evidence: Evidence from CISA KEV JSON Feed and Android Security Bulletin - Latest indicates a potential risk to Android devices due to the exploitation of CVE-2025-0096.
```

## B07
```
Title: CVE-2025-0098 and CVE-2025-0091 Android Vulnerabilities
Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9

Summary: Two high-severity vulnerabilities (CVE-2025-0098 and CVE-2025-0091) in Android Camera HAL and ActivityManagerService have been detected, potentially leading to local privilege escalation. These vulnerabilities are connected to other recent Android security issues, including CVE-2025-0096 and CVE-2025-0097, which have been exploited in targeted attacks. It is essential to prioritize patching to prevent further exploitation.
Cross-source patterns: These vulnerabilities are connected to other recent Android security issues, including CVE-2025-0096 and CVE-2025-0097, which have been exploited in targeted attacks. Additionally, the Pixel Update Bulletin and Android Security Bulletin - Latest sources indicate that exploitation has been detected in limited, targeted attacks.
Recommended actions:
  - Prioritize patching for CVE-2025-0098 and CVE-2025-0091 in Android 14 and 15 devices with Qualcomm chipsets (Risk Engineering, this_week)
  - Monitor for further exploitation and update the risk assessment accordingly (Fraud Modeling, monitor)
Evidence: Evidence 1 (CVE-2025-0098) and Evidence 2 (CVE-2025-0091) from the NVD CVE Feed (Android) indicate the presence of these vulnerabilities. Cross-Source Evidence 1 from the Pixel Update Bulletin and Cross-Source Evidence 2 from the Android Security Bulletin - Latest provide additional context and indicate that exploitation has been detected in limited, targeted attacks.
```

## C09
```
Title: Samsung Knox Attestation Bypass and Secure Folder Vulnerability
Priority: CRITICAL   |   Risk score: 9.5/10   |   Confidence: 0.95

Summary: The Samsung Knox attestation bypass and Secure Folder race condition vulnerability allow unauthorized file extraction, with active exploitation detected in targeted attacks. This change affects device trust signals and requires immediate attention to prevent signal degradation and enforcement bypass.
Cross-source patterns: The Knox attestation bypass and Secure Folder race condition vulnerabilities are connected to the Android Security Bulletin (Cross-Source Evidence 1), which reports exploitation in limited, targeted attacks. Additionally, the Google Play Developer Policy Center (Cross-Source Evidence 2) updates policy to require the Play Integrity API for device attestation, further emphasizing the importance of addressing this vulnerability.
Recommended actions:
  - Update Galaxy A-series devices with the March 2025 Security Patch and ensure the Secure Folder patch is applied (Risk Engineering, immediate)
  - Review and update custom root detection implementations to use the Play Integrity API for device attestation (Fraud Modeling, this_week)
Evidence: Evidence 1 (Samsung Mobile Security Bulletin) and Cross-Source Evidence 1 (Android Security Bulletin - Latest) support the recommendation to update Galaxy A-series devices and review custom root detection implementations.
```

## A09
```
Title: Samsung Security Patch Update - Critical Vulnerability in Secure Folder
Priority: CRITICAL   |   Risk score: 9.5/10   |   Confidence: 0.95

Summary: Samsung released a security patch update addressing CVE-2025-0093, CVE-2025-0096, and SVE-2025-0303. The latter is a critical vulnerability in Secure Folder with active exploitation detected. This change affects Galaxy S24, S23, Z Fold5, and Z Flip5 models.
Cross-source patterns: Cross-source evidence indicates that CVE-2025-0096 and CVE-2025-0097 are also critical vulnerabilities affecting Android 14, 15, and kernel versions 5.15, 6.1, 6.6. Public exploit code is available for CVE-2025-0096.
Recommended actions:
  - Prioritize patching for Galaxy S24, S23, Z Fold5, and Z Flip5 models (Risk Engineering, immediate)
  - Monitor for potential data breaches and unauthorized access to sensitive information (Fraud Operations, this_week)
Evidence: Evidence IDs: [Evidence 1, Evidence 2, Cross-Source Evidence 1, Cross-Source Evidence 2]
```

## G01
```
Title: New Kernel Vulnerabilities Expose Devices to Exploitation
Priority: HIGH   |   Risk score: 8.5/10   |   Confidence: 0.9

Summary: The updated March Android Security Bulletin introduced two critical kernel vulnerabilities (CVE-2025-0096 and CVE-2025-0097) that expose devices to remote code execution and elevation of privilege attacks. Public exploit code is available, and exploitation has been detected in limited, targeted attacks. This change may impact device trust and risk posture.
Cross-source patterns: Cross-source evidence indicates that these vulnerabilities are being actively exploited and have been included in the Pixel Update Bulletin. The CISA Known Exploited Vulnerabilities feed also lists CVE-2025-0097 as a known exploited vulnerability.
Recommended actions:
  - Prioritize patching for CVE-2025-0096 and CVE-2025-0097 (Risk Engineering, this_week)
  - Monitor for exploitation attempts and update device firmware as necessary (Fraud Modeling, monitor)
Evidence: Evidence IDs 1 and 2 from the Android Security Bulletin - Latest, and Cross-Source Evidence 1 from the Pixel Update Bulletin and Cross-Source Evidence 2 from the CISA Known Exploited Vulnerabilities feed support this recommendation.
```

## J03
```
Title: ARM Mali GPU Vulnerability Disclosure
Priority: CRITICAL   |   Risk score: 9.0/10   |   Confidence: 0.9

Summary: A disclosed vulnerability in the ARM Mali GPU (CVE-2025-0097) could be exploited by hackers to gain unauthorized access. This change is highly relevant to our vulnerability exposure risk domain, with a risk score of 9/10. The vulnerability allows kernel code execution via a type confusion vulnerability in the Mali GPU driver.
Cross-source patterns: This vulnerability is connected to a similar vulnerability in the Android Wi-Fi HAL (CVE-2025-0096), which allows remote code execution via a crafted Wi-Fi frame. Both vulnerabilities are critical and have been detected in limited, targeted attacks.
Recommended actions:
  - Apply updates to the Mali GPU driver per vendor instructions (Risk Engineering, immediate)
  - Monitor for any signs of exploitation or suspicious activity related to this vulnerability (Fraud Operations, this_week)
Evidence: Evidence 1 (source_id=3, category=cve_feed, change_id=3) and Cross-Source Evidence 1 (source=Android Security Bulletin - Latest, category=security_bulletin, change_id=1) support this recommendation.
```
