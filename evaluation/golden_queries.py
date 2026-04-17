"""Golden evaluation queries for the ECI retrieval ablation study.

50 queries across 10 sources × 5 query types, each with deterministic
cross-source ground truth based on shared entity overlap.

Query Types:
    A - Full Diff:           The raw diff_text from the change (pipeline input)
    B - Identifier-Focused:  CVE/SVE/API identifiers extracted from the diff
    C - Component-Focused:   Component/product descriptions without identifiers
    D - Natural Language:    Analyst-style questions (chat interface simulation)
    E - Entity-Only:         Bare entity strings concatenated (minimum context)
"""

# ── Source Names (must match config/sources.json) ─────────────────

SRC_BULLETIN  = "Android Security Bulletin - Latest"
SRC_INTEGRITY = "Play Integrity API Overview"
SRC_CISA_HTML = "CISA Known Exploited Vulnerabilities"
SRC_CISA_JSON = "CISA KEV JSON Feed"
SRC_POLICY    = "Google Play Developer Policy Center"
SRC_API_DIFF  = "Android API Differences Report"
SRC_NVD       = "NVD CVE Feed (Android)"
SRC_CTS       = "Android CTS/CDD Changes"
SRC_SAMSUNG   = "Samsung Mobile Security Bulletin"
SRC_PIXEL     = "Pixel Update Bulletin"

# ── Cross-Source Ground Truth Matrix ──────────────────────────────
# For each source, which OTHER sources should be retrieved?
# Derived from entity co-occurrence in the synthetic test data.

GROUND_TRUTH = {
    SRC_BULLETIN:  {SRC_CISA_HTML, SRC_CISA_JSON, SRC_NVD, SRC_SAMSUNG, SRC_PIXEL},
    SRC_INTEGRITY: {SRC_POLICY},
    SRC_CISA_HTML: {SRC_BULLETIN, SRC_CISA_JSON, SRC_NVD, SRC_SAMSUNG, SRC_PIXEL},
    SRC_CISA_JSON: {SRC_BULLETIN, SRC_CISA_HTML, SRC_NVD, SRC_SAMSUNG, SRC_PIXEL},
    SRC_POLICY:    {SRC_INTEGRITY, SRC_API_DIFF, SRC_CTS},
    SRC_API_DIFF:  {SRC_POLICY, SRC_CTS},
    SRC_NVD:       {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG},
    SRC_CTS:       {SRC_API_DIFF, SRC_POLICY},
    SRC_SAMSUNG:   {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_NVD, SRC_PIXEL},
    SRC_PIXEL:     {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG},
}

# ── 50 Golden Queries ─────────────────────────────────────────────

GOLDEN_QUERIES = [
    # ================================================================
    #  TYPE A: Full Diff (uses change.diff_text at runtime)
    # ================================================================
    {"id": "A01", "type": "A", "source": SRC_BULLETIN,  "query": None, "expected": GROUND_TRUTH[SRC_BULLETIN]},
    {"id": "A02", "type": "A", "source": SRC_INTEGRITY, "query": None, "expected": GROUND_TRUTH[SRC_INTEGRITY]},
    {"id": "A03", "type": "A", "source": SRC_CISA_HTML, "query": None, "expected": GROUND_TRUTH[SRC_CISA_HTML]},
    {"id": "A04", "type": "A", "source": SRC_CISA_JSON, "query": None, "expected": GROUND_TRUTH[SRC_CISA_JSON]},
    {"id": "A05", "type": "A", "source": SRC_POLICY,    "query": None, "expected": GROUND_TRUTH[SRC_POLICY]},
    {"id": "A06", "type": "A", "source": SRC_API_DIFF,  "query": None, "expected": GROUND_TRUTH[SRC_API_DIFF]},
    {"id": "A07", "type": "A", "source": SRC_NVD,       "query": None, "expected": GROUND_TRUTH[SRC_NVD]},
    {"id": "A08", "type": "A", "source": SRC_CTS,       "query": None, "expected": GROUND_TRUTH[SRC_CTS]},
    {"id": "A09", "type": "A", "source": SRC_SAMSUNG,   "query": None, "expected": GROUND_TRUTH[SRC_SAMSUNG]},
    {"id": "A10", "type": "A", "source": SRC_PIXEL,     "query": None, "expected": GROUND_TRUTH[SRC_PIXEL]},

    # ================================================================
    #  TYPE B: Identifier-Focused (CVE/SVE/API-specific extracts)
    # ================================================================
    {
        "id": "B01", "type": "B", "source": SRC_BULLETIN,
        "query": "CVE-2025-0096 Remote Code Execution Critical Wi-Fi HAL buffer overflow. CVE-2025-0097 Elevation of Privilege Critical GPU driver Mali type confusion kernel code execution.",
        "expected": {SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "B02", "type": "B", "source": SRC_INTEGRITY,
        "query": "MEETS_VIRTUAL_INTEGRITY new verdict category distinguishes virtual devices emulators from physical devices. Classic API requests sunset November 2025.",
        "expected": {SRC_POLICY},
    },
    {
        "id": "B03", "type": "B", "source": SRC_CISA_HTML,
        "query": "CVE-2025-0097 ARM Mali GPU Driver Type Confusion kernel code execution. CVE-2025-0096 Android Wi-Fi HAL Buffer Overflow remote code execution. CVE-2025-0093 ransomware use Known.",
        "expected": {SRC_BULLETIN, SRC_CISA_JSON, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "B04", "type": "B", "source": SRC_CISA_JSON,
        "query": "CVE-2025-0096 Google Android Wi-Fi HAL Buffer Overflow. CVE-2025-0097 ARM Mali GPU Driver Type Confusion. CVE-2025-0093 Known ransomware campaign use.",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "B05", "type": "B", "source": SRC_POLICY,
        "query": "Play Integrity API MEETS_STRONG_INTEGRITY verification required for financial apps transaction-initiating actions. Photo Picker API READ_MEDIA_IMAGES migration September 2025.",
        "expected": {SRC_INTEGRITY, SRC_API_DIFF, SRC_CTS},
    },
    {
        "id": "B06", "type": "B", "source": SRC_API_DIFF,
        "query": "SDK 35 new permission READ_MEDIA_VISUAL_USER_SELECTED. READ_MEDIA_IMAGES requires Photo Picker migration. MediaStore.getPhotoPickerIntent() new API.",
        "expected": {SRC_POLICY, SRC_CTS},
    },
    {
        "id": "B07", "type": "B", "source": SRC_NVD,
        "query": "CVE-2025-0098 integer overflow Android Camera HAL local privilege escalation Qualcomm CVSS 7.5 HIGH. CVE-2025-0091 ActivityManagerService CVSS 7.8 HIGH.",
        "expected": {SRC_BULLETIN, SRC_SAMSUNG},
    },
    {
        "id": "B08", "type": "B", "source": SRC_CTS,
        "query": "SDK 35 apps requesting READ_MEDIA_IMAGES must integrate Photo Picker API. CTS R17 CtsCameraXTestCases 156 new tests. CameraX conformance test module.",
        "expected": {SRC_API_DIFF, SRC_POLICY},
    },
    {
        "id": "B09", "type": "B", "source": SRC_SAMSUNG,
        "query": "CVE-2025-0096 system patch. SVE-2025-0303 Critical Secure Folder race condition unauthorized file extraction. SVE-2025-0301 Knox Attestation bypass.",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_PIXEL},
    },
    {
        "id": "B10", "type": "B", "source": SRC_PIXEL,
        "query": "CVE-2025-0096 CVE-2025-0097 supplementary patches. CVE-2025-P003 Critical Pixel Modem firmware heap overflow baseband RRC remote code execution Exynos.",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG},
    },

    # ================================================================
    #  TYPE C: Component-Focused (descriptions without CVE/SVE IDs)
    # ================================================================
    {
        "id": "C01", "type": "C", "source": SRC_BULLETIN,
        "query": "Buffer overflow in the Wi-Fi subsystem and Wi-Fi HAL allows remote code execution via crafted Wi-Fi frame. Type confusion vulnerability in GPU driver Mali allows kernel code execution from unprivileged process. Additional patch for kernel 6.6.",
        "expected": {SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "C02", "type": "C", "source": SRC_INTEGRITY,
        "query": "New verdict category for virtual devices and emulators. Enhanced recent device activity levels with granular tiers typical unusual very unusual. Token validity reduced from 10 to 5 minutes. Standard API requests require app linking to Play Console.",
        "expected": {SRC_POLICY},
    },
    {
        "id": "C03", "type": "C", "source": SRC_CISA_HTML,
        "query": "ARM Mali GPU driver type confusion vulnerability allowing kernel code execution. Android Wi-Fi HAL buffer overflow allowing remote code execution via crafted frames. Android Bluetooth use-after-free ransomware campaign use confirmed.",
        "expected": {SRC_BULLETIN, SRC_CISA_JSON, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "C04", "type": "C", "source": SRC_CISA_JSON,
        "query": "Known exploited vulnerabilities catalog updated total count 1249. Mali GPU driver type confusion allowing kernel code execution due date April 2025. Wi-Fi HAL buffer overflow remote code execution via crafted frames.",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "C05", "type": "C", "source": SRC_POLICY,
        "query": "Device attestation required for apps detecting rooted or modified devices. Custom root detection no longer accepted as sole verification method. Financial apps must implement strong integrity verification for transactions. Photo Picker API migration required for media access permissions.",
        "expected": {SRC_INTEGRITY, SRC_API_DIFF, SRC_CTS},
    },
    {
        "id": "C06", "type": "C", "source": SRC_API_DIFF,
        "query": "Camera capture session now supports multi-stream HDR. CameraX external USB camera lens facing added. Photo Picker intent added to MediaStore. MediaStore DATA column deprecated. Granular photo picker access permission added.",
        "expected": {SRC_CTS, SRC_POLICY},
    },
    {
        "id": "C07", "type": "C", "source": SRC_NVD,
        "query": "Integer overflow in Android Camera HAL allows local privilege escalation via crafted camera request affecting Qualcomm chipsets. Logic error in ActivityManagerService allows local attacker to escalate privileges. Bluetooth use-after-free remote code execution.",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG},
    },
    {
        "id": "C08", "type": "C", "source": SRC_CTS,
        "query": "Under-display cameras for face unlock must pass liveness detection test suite. CameraX conformance test module for USB external cameras. Apps requesting broad media access must integrate with Photo Picker. New security test cases added for permissions compliance.",
        "expected": {SRC_API_DIFF, SRC_POLICY},
    },
    {
        "id": "C09", "type": "C", "source": SRC_SAMSUNG,
        "query": "Knox attestation bypass allowed modified devices to pass integrity checks. Secure Folder race condition allows unauthorized file extraction when device unlocked. Active exploitation detected in targeted attacks. Patch now available for Galaxy A-series.",
        "expected": {SRC_BULLETIN, SRC_PIXEL},
    },
    {
        "id": "C10", "type": "C", "source": SRC_PIXEL,
        "query": "Titan M2 firmware fault injection vulnerability bypass secure boot. Pixel modem firmware heap overflow baseband remote code execution via crafted RRC messages. Commercial spyware vendors confirmed exploitation. Theft Detection Lock improvements.",
        "expected": {SRC_BULLETIN, SRC_SAMSUNG},
    },

    # ================================================================
    #  TYPE D: Natural Language (analyst-style questions)
    # ================================================================
    {
        "id": "D01", "type": "D", "source": SRC_BULLETIN,
        "query": "Which OEM devices have released patches for the new Wi-Fi HAL buffer overflow and Mali GPU driver vulnerabilities from the March 2025 Android Security Bulletin?",
        "expected": {SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "D02", "type": "D", "source": SRC_INTEGRITY,
        "query": "What policy changes have been made that require apps to implement Play Integrity API with strong integrity verdicts?",
        "expected": {SRC_POLICY},
    },
    {
        "id": "D03", "type": "D", "source": SRC_CISA_HTML,
        "query": "Are the CISA KEV Android vulnerabilities for Wi-Fi HAL and Mali GPU being actively patched by Samsung and Google Pixel?",
        "expected": {SRC_SAMSUNG, SRC_PIXEL, SRC_BULLETIN},
    },
    {
        "id": "D04", "type": "D", "source": SRC_CISA_JSON,
        "query": "Which Android security bulletins correspond to the CVEs added to the CISA Known Exploited Vulnerabilities catalog this month?",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "D05", "type": "D", "source": SRC_POLICY,
        "query": "How does the new Google Play policy on mandatory Play Integrity API for financial apps affect existing developer documentation and API requirements?",
        "expected": {SRC_INTEGRITY},
    },
    {
        "id": "D06", "type": "D", "source": SRC_API_DIFF,
        "query": "What compatibility and compliance testing changes were introduced alongside the SDK 35 Photo Picker and CameraX API updates?",
        "expected": {SRC_CTS, SRC_POLICY},
    },
    {
        "id": "D07", "type": "D", "source": SRC_NVD,
        "query": "Have the high-severity NVD vulnerabilities for ActivityManagerService and Bluetooth in Android been addressed in any OEM security updates?",
        "expected": {SRC_BULLETIN, SRC_SAMSUNG},
    },
    {
        "id": "D08", "type": "D", "source": SRC_CTS,
        "query": "What new API surface changes in SDK 35 triggered the addition of CameraX and Photo Picker test modules in CTS R17?",
        "expected": {SRC_API_DIFF, SRC_POLICY},
    },
    {
        "id": "D09", "type": "D", "source": SRC_SAMSUNG,
        "query": "Is the Samsung Knox attestation bypass vulnerability related to any changes in the Google Play Integrity API or Android security bulletins?",
        "expected": {SRC_BULLETIN, SRC_INTEGRITY},
    },
    {
        "id": "D10", "type": "D", "source": SRC_PIXEL,
        "query": "Are the Pixel modem and Titan M2 firmware vulnerabilities tracked in any national vulnerability database or CISA catalog?",
        "expected": {SRC_CISA_HTML, SRC_CISA_JSON, SRC_BULLETIN},
    },

    # ================================================================
    #  TYPE E: Entity-Only (bare identifiers, minimal context)
    # ================================================================
    {
        "id": "E01", "type": "E", "source": SRC_BULLETIN,
        "query": "CVE-2025-0096 CVE-2025-0097 wi-fi_hal gpu_driver mali kernel_6.6",
        "expected": {SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "E02", "type": "E", "source": SRC_INTEGRITY,
        "query": "play_integrity_api meets_strong_integrity meets_virtual_integrity",
        "expected": {SRC_POLICY},
    },
    {
        "id": "E03", "type": "E", "source": SRC_CISA_HTML,
        "query": "CVE-2025-0096 CVE-2025-0097 CVE-2025-0093 mali wi-fi_hal ransomware",
        "expected": {SRC_BULLETIN, SRC_CISA_JSON, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "E04", "type": "E", "source": SRC_CISA_JSON,
        "query": "CVE-2025-0096 CVE-2025-0097 CVE-2025-0093 ARM Mali Google Android",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_SAMSUNG, SRC_PIXEL},
    },
    {
        "id": "E05", "type": "E", "source": SRC_POLICY,
        "query": "play_integrity_api meets_strong_integrity read_media_images photo_picker",
        "expected": {SRC_INTEGRITY, SRC_API_DIFF, SRC_CTS},
    },
    {
        "id": "E06", "type": "E", "source": SRC_API_DIFF,
        "query": "sdk_35 read_media_images photo_picker CameraX MediaStore",
        "expected": {SRC_CTS, SRC_POLICY},
    },
    {
        "id": "E07", "type": "E", "source": SRC_NVD,
        "query": "CVE-2025-0091 CVE-2025-0093 CVE-2025-0098 ActivityManagerService Bluetooth Camera HAL",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG},
    },
    {
        "id": "E08", "type": "E", "source": SRC_CTS,
        "query": "sdk_35 CameraX photo_picker read_media_images biometric_face liveness",
        "expected": {SRC_API_DIFF, SRC_POLICY},
    },
    {
        "id": "E09", "type": "E", "source": SRC_SAMSUNG,
        "query": "CVE-2025-0096 SVE-2025-0303 SVE-2025-0301 knox secure_folder",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_PIXEL},
    },
    {
        "id": "E10", "type": "E", "source": SRC_PIXEL,
        "query": "CVE-2025-0096 CVE-2025-0097 CVE-2025-P003 titan_m2 modem baseband",
        "expected": {SRC_BULLETIN, SRC_CISA_HTML, SRC_CISA_JSON, SRC_SAMSUNG},
    },
]

# ── Query Type Labels ─────────────────────────────────────────────

QUERY_TYPE_LABELS = {
    "A": "Full Diff",
    "B": "Identifier-Focused",
    "C": "Component-Focused",
    "D": "Natural Language",
    "E": "Entity-Only",
}
