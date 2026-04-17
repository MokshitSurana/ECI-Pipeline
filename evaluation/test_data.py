"""Seed realistic test data for pipeline validation.

Creates synthetic but realistic snapshots and changes based on
actual Android Security Bulletin and CISA KEV patterns.
Run this instead of scraper.py when testing locally.
"""
from datetime import datetime, timezone, timedelta
from utils.db import get_session, init_db, Source, Snapshot, Change
from scripts.seed_sources import seed_sources
from scripts.diff_detector import compute_diff, build_diff_text

# ── Synthetic Snapshot Content ────────────────────────────────────

BULLETIN_V1 = """Android Security Bulletin - March 2025
Published March 3, 2025

The Android Security Bulletin contains details of security vulnerabilities affecting Android devices. Security patch levels of 2025-03-05 or later address all of these issues.

Framework
The most severe vulnerability in this section could lead to local escalation of privilege with no additional execution privileges needed.

CVE-2025-0091 - Elevation of Privilege - High
Affected component: ActivityManagerService
Affected versions: Android 13, 14, 15
Description: A logic error in ActivityManagerService could allow a local attacker to escalate privileges. This issue is rated as High severity because it could be used to gain elevated capabilities within the system process.

CVE-2025-0092 - Information Disclosure - Moderate
Affected component: PackageManagerService
Affected versions: Android 14, 15
Description: An issue in PackageManagerService could lead to local information disclosure with no additional execution privileges needed.

System
The most severe vulnerability in this section could lead to remote code execution with no additional execution privileges needed.

CVE-2025-0093 - Remote Code Execution - Critical
Affected component: Bluetooth
Affected versions: Android 13, 14, 15
Description: A use-after-free vulnerability in the Bluetooth stack could allow a remote attacker within Bluetooth range to execute arbitrary code. This issue is rated as Critical.

Kernel
CVE-2025-0094 - Elevation of Privilege - High
Affected component: binder driver
Affected versions: Android kernel versions 5.15, 6.1
Description: A race condition in the binder driver could allow local privilege escalation.

Google Play system updates
The following issues are resolved through Google Play system updates (Project Mainline).

CVE-2025-0095 - Elevation of Privilege - High
Affected component: Media Framework
Affected versions: Android 13, 14, 15"""

BULLETIN_V2 = """Android Security Bulletin - March 2025
Published March 3, 2025 | Updated March 17, 2025

The Android Security Bulletin contains details of security vulnerabilities affecting Android devices. Security patch levels of 2025-03-05 or later address all of these issues.

Framework
The most severe vulnerability in this section could lead to local escalation of privilege with no additional execution privileges needed.

CVE-2025-0091 - Elevation of Privilege - High
Affected component: ActivityManagerService
Affected versions: Android 13, 14, 15
Description: A logic error in ActivityManagerService could allow a local attacker to escalate privileges. This issue is rated as High severity because it could be used to gain elevated capabilities within the system process.
Updated: Exploitation has been detected in limited, targeted attacks.

CVE-2025-0092 - Information Disclosure - Moderate
Affected component: PackageManagerService
Affected versions: Android 14, 15
Description: An issue in PackageManagerService could lead to local information disclosure with no additional execution privileges needed.

System
The most severe vulnerability in this section could lead to remote code execution with no additional execution privileges needed.

CVE-2025-0093 - Remote Code Execution - Critical
Affected component: Bluetooth
Affected versions: Android 13, 14, 15
Description: A use-after-free vulnerability in the Bluetooth stack could allow a remote attacker within Bluetooth range to execute arbitrary code. This issue is rated as Critical.
Updated: Public exploit code is now available. Organizations should prioritize patching.

CVE-2025-0096 - Remote Code Execution - Critical (NEW)
Affected component: Wi-Fi subsystem
Affected versions: Android 14, 15
Description: A buffer overflow in the Wi-Fi HAL could allow remote code execution via a crafted Wi-Fi frame. No user interaction required.

Kernel
CVE-2025-0094 - Elevation of Privilege - High
Affected component: binder driver
Affected versions: Android kernel versions 5.15, 6.1
Description: A race condition in the binder driver could allow local privilege escalation.
Updated: Additional patch now available for kernel 6.6.

CVE-2025-0097 - Elevation of Privilege - Critical (NEW)
Affected component: GPU driver (Mali)
Affected versions: Android kernel versions 5.15, 6.1, 6.6
Description: A type confusion vulnerability in the Mali GPU driver allows kernel code execution from an unprivileged process.

Google Play system updates
The following issues are resolved through Google Play system updates (Project Mainline).

CVE-2025-0095 - Elevation of Privilege - High
Affected component: Media Framework
Affected versions: Android 13, 14, 15"""

PLAY_INTEGRITY_V1 = """Play Integrity API Overview
The Play Integrity API helps you check that interactions and server requests are coming from your genuine app binary, running on a genuine Android device, powered by Google Play.

Device Integrity Verdicts
MEETS_DEVICE_INTEGRITY: The app is running on a genuine Android device powered by Google Play services. The device passes system integrity checks and meets Android compatibility requirements.

MEETS_BASIC_INTEGRITY: The app is running on a device that passes basic system integrity checks. The device may not meet Android compatibility requirements and may not be approved to run Google Play services.

MEETS_STRONG_INTEGRITY: The app is running on a genuine Android device powered by Google Play services with a strong guarantee of system integrity such as a hardware-backed proof of boot integrity.

Recent Device Activity
The Play Integrity API provides a recent device activity level that tells you how many integrity tokens your app has requested on a specific device in the last hour.

API Requirements
- Minimum Android version: Android 5.0 (API level 21)
- Google Play services required
- Token validity: 10 minutes from generation"""

PLAY_INTEGRITY_V2 = """Play Integrity API Overview
The Play Integrity API helps you check that interactions and server requests are coming from your genuine app binary, running on a genuine Android device, powered by Google Play.

Device Integrity Verdicts
MEETS_DEVICE_INTEGRITY: The app is running on a genuine Android device powered by Google Play services. The device passes system integrity checks and meets Android compatibility requirements.

MEETS_BASIC_INTEGRITY: The app is running on a device that passes basic system integrity checks. The device may not meet Android compatibility requirements and may not be approved to run Google Play services.

MEETS_STRONG_INTEGRITY: The app is running on a genuine Android device powered by Google Play services with a strong guarantee of system integrity such as a hardware-backed proof of boot integrity.

MEETS_VIRTUAL_INTEGRITY (NEW): Starting May 2025, a new verdict category distinguishes virtual devices (emulators, cloud-hosted instances) from physical devices. Apps that currently treat MEETS_BASIC_INTEGRITY as physical device confirmation should update their logic.

Recent Device Activity
The Play Integrity API now provides enhanced recent device activity levels with granular tiers:
- LEVEL_1 (TYPICAL): Normal activity level
- LEVEL_2 (UNUSUAL): Higher than typical activity
- LEVEL_3 (VERY_UNUSUAL): Significantly abnormal activity patterns
- LEVEL_4 (UNEVALUATED): Not enough data to evaluate

The previous binary activity signal is deprecated as of April 2025.

API Requirements
- Minimum Android version: Android 5.0 (API level 21)
- Google Play services required
- Token validity: Reduced from 10 minutes to 5 minutes for enhanced security
- NEW: Standard API requests now require app linking to Play Console
- NEW: Classic API requests will be sunset on November 30, 2025"""

CISA_KEV_V1 = """{
  "title": "CISA Known Exploited Vulnerabilities Catalog",
  "catalogVersion": "2025.03.15",
  "totalCount": 1245,
  "vulnerabilities": [
    {
      "cveID": "CVE-2025-0093",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Bluetooth Remote Code Execution",
      "dateAdded": "2025-03-10",
      "shortDescription": "Android Bluetooth contains a use-after-free vulnerability that allows remote code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-03-31",
      "knownRansomwareCampaignUse": "Unknown"
    },
    {
      "cveID": "CVE-2024-53104",
      "vendorProject": "Linux",
      "product": "Kernel",
      "vulnerabilityName": "Linux Kernel USB Video Class Out-of-Bounds Write",
      "dateAdded": "2025-02-05",
      "shortDescription": "Linux kernel contains an out-of-bounds write vulnerability in USB Video Class driver.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-02-26",
      "knownRansomwareCampaignUse": "Unknown"
    }
  ]
}"""

CISA_KEV_V2 = """{
  "title": "CISA Known Exploited Vulnerabilities Catalog",
  "catalogVersion": "2025.03.22",
  "totalCount": 1249,
  "vulnerabilities": [
    {
      "cveID": "CVE-2025-0093",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Bluetooth Remote Code Execution",
      "dateAdded": "2025-03-10",
      "shortDescription": "Android Bluetooth contains a use-after-free vulnerability that allows remote code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-03-31",
      "knownRansomwareCampaignUse": "Known"
    },
    {
      "cveID": "CVE-2025-0097",
      "vendorProject": "ARM",
      "product": "Mali GPU Driver",
      "vulnerabilityName": "ARM Mali GPU Driver Type Confusion",
      "dateAdded": "2025-03-20",
      "shortDescription": "ARM Mali GPU driver contains a type confusion vulnerability allowing kernel code execution.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-10",
      "knownRansomwareCampaignUse": "Unknown"
    },
    {
      "cveID": "CVE-2025-0096",
      "vendorProject": "Google",
      "product": "Android",
      "vulnerabilityName": "Android Wi-Fi HAL Buffer Overflow",
      "dateAdded": "2025-03-21",
      "shortDescription": "Android Wi-Fi HAL contains a buffer overflow allowing remote code execution via crafted frames.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-04-11",
      "knownRansomwareCampaignUse": "Unknown"
    },
    {
      "cveID": "CVE-2024-53104",
      "vendorProject": "Linux",
      "product": "Kernel",
      "vulnerabilityName": "Linux Kernel USB Video Class Out-of-Bounds Write",
      "dateAdded": "2025-02-05",
      "shortDescription": "Linux kernel contains an out-of-bounds write vulnerability in USB Video Class driver.",
      "requiredAction": "Apply updates per vendor instructions.",
      "dueDate": "2025-02-26",
      "knownRansomwareCampaignUse": "Unknown"
    }
  ]
}"""

POLICY_V1 = """Google Play Developer Program Policy
Last updated: February 15, 2025

Data Safety
Apps must provide accurate information about their data collection and sharing practices in the Data Safety section. Developers must complete the Data Safety form and keep it up to date.

Device and Network Abuse
Apps must not facilitate or provide instructions for disabling or circumventing device security features, including but not limited to: rooting, bootloader unlocking, or installing custom firmware.

Financial Services
Apps offering financial services must comply with applicable regulations and licensing requirements in the jurisdictions where they operate. Apps must clearly disclose fees, terms, and risks.

Permissions Policy
Apps must request only the minimum permissions necessary for their functionality. Access to sensitive permissions such as SMS, Call Log, and Location must be justified through a Permissions Declaration Form."""

POLICY_V2 = """Google Play Developer Program Policy
Last updated: March 20, 2025

Data Safety
Apps must provide accurate information about their data collection and sharing practices in the Data Safety section. Developers must complete the Data Safety form and keep it up to date.

Device and Network Abuse
Apps must not facilitate or provide instructions for disabling or circumventing device security features, including but not limited to: rooting, bootloader unlocking, or installing custom firmware.
NEW (Effective June 2025): Apps that detect rooted or modified devices must use the Play Integrity API for device attestation. Custom root detection implementations will no longer be accepted as the sole verification method.

Financial Services
Apps offering financial services must comply with applicable regulations and licensing requirements in the jurisdictions where they operate. Apps must clearly disclose fees, terms, and risks.
UPDATED: Starting May 2025, financial apps must implement the Play Integrity API with MEETS_STRONG_INTEGRITY verification for all transaction-initiating actions. Apps not meeting this requirement will receive policy warnings beginning July 2025.

Permissions Policy
Apps must request only the minimum permissions necessary for their functionality. Access to sensitive permissions such as SMS, Call Log, and Location must be justified through a Permissions Declaration Form.
UPDATED: The Photo and Video permissions policy now requires apps to use the Android Photo Picker API instead of requesting broad storage access. Apps with existing READ_MEDIA_IMAGES permission must migrate by September 2025.

AI-Generated Content (NEW)
Apps that generate or significantly modify content using AI must clearly label AI-generated content visible to users. This applies to text, images, audio, and video content. Apps must provide mechanisms for users to report potentially harmful AI-generated content."""
NVD_V1 = """{
  "resultsPerPage": 2,
  "startIndex": 0,
  "totalResults": 2,
  "vulnerabilities": [
    {
      "cve": {
        "id": "CVE-2025-0091",
        "published": "2025-03-03T18:00:00.000",
        "descriptions": [
          {"lang": "en", "value": "A logic error in ActivityManagerService could allow a local attacker to escalate privileges on Android 13, 14, 15."}
        ],
        "metrics": {
          "cvssMetricV31": [
            {"cvssData": {"baseScore": 7.8, "baseSeverity": "HIGH"}}
          ]
        }
      }
    },
    {
      "cve": {
        "id": "CVE-2025-0093",
        "published": "2025-03-03T18:00:00.000",
        "descriptions": [
          {"lang": "en", "value": "A use-after-free vulnerability in the Android Bluetooth stack could allow a remote attacker within Bluetooth range to execute arbitrary code."}
        ],
        "metrics": {
          "cvssMetricV31": [
            {"cvssData": {"baseScore": 9.8, "baseSeverity": "CRITICAL"}}
          ]
        }
      }
    }
  ]
}"""

NVD_V2 = """{
  "resultsPerPage": 3,
  "startIndex": 0,
  "totalResults": 3,
  "vulnerabilities": [
    {
      "cve": {
        "id": "CVE-2025-0091",
        "published": "2025-03-03T18:00:00.000",
        "descriptions": [
          {"lang": "en", "value": "A logic error in ActivityManagerService could allow a local attacker to escalate privileges on Android 13, 14, 15."}
        ],
        "metrics": {
          "cvssMetricV31": [
            {"cvssData": {"baseScore": 7.8, "baseSeverity": "HIGH"}}
          ]
        }
      }
    },
    {
      "cve": {
        "id": "CVE-2025-0093",
        "published": "2025-03-03T18:00:00.000",
        "descriptions": [
          {"lang": "en", "value": "A use-after-free vulnerability in the Android Bluetooth stack could allow a remote attacker within Bluetooth range to execute arbitrary code."}
        ],
        "metrics": {
          "cvssMetricV31": [
            {"cvssData": {"baseScore": 9.8, "baseSeverity": "CRITICAL"}}
          ]
        }
      }
    },
    {
      "cve": {
        "id": "CVE-2025-0098",
        "published": "2025-03-20T12:00:00.000",
        "descriptions": [
          {"lang": "en", "value": "An integer overflow in the Android Camera HAL allows local privilege escalation via a crafted camera request. Affects Android 14, 15 devices with Qualcomm chipsets."}
        ],
        "metrics": {
          "cvssMetricV31": [
            {"cvssData": {"baseScore": 7.5, "baseSeverity": "HIGH"}}
          ]
        }
      }
    }
  ]
}"""

SAMSUNG_BULLETIN_V1 = """Samsung Mobile Security Updates
March 2025 Security Patch

Samsung is releasing a maintenance update for major flagship models. This update includes patches from Google and Samsung.

Google patches included:
- Patches up to Android Security Bulletin March 2025 patch level
- Framework: CVE-2025-0091, CVE-2025-0092
- System: CVE-2025-0093

Samsung Vulnerabilities and Exposures (SVE):
SVE-2025-0301 - High
Affected component: Samsung Knox Attestation
Description: A bypass in Knox attestation API allowed modified devices to pass integrity checks under specific conditions.
Affected models: Galaxy S24, S23, Z Fold5, Z Flip5

SVE-2025-0302 - Moderate
Affected component: Samsung TrustZone
Description: Information disclosure in TrustZone could leak cryptographic key material through a side-channel attack.
Affected models: Exynos-based Galaxy devices"""

SAMSUNG_BULLETIN_V2 = """Samsung Mobile Security Updates
March 2025 Security Patch (Updated March 20, 2025)

Samsung is releasing a maintenance update for major flagship models. This update includes patches from Google and Samsung.

Google patches included:
- Patches up to Android Security Bulletin March 2025 patch level
- Framework: CVE-2025-0091, CVE-2025-0092
- System: CVE-2025-0093, CVE-2025-0096 (NEW)

Samsung Vulnerabilities and Exposures (SVE):
SVE-2025-0301 - High
Affected component: Samsung Knox Attestation
Description: A bypass in Knox attestation API allowed modified devices to pass integrity checks under specific conditions.
Affected models: Galaxy S24, S23, Z Fold5, Z Flip5
Updated: Patch now available for Galaxy A-series devices

SVE-2025-0302 - Moderate
Affected component: Samsung TrustZone
Description: Information disclosure in TrustZone could leak cryptographic key material through a side-channel attack.
Affected models: Exynos-based Galaxy devices

SVE-2025-0303 - Critical (NEW)
Affected component: Samsung Secure Folder
Description: A race condition in Secure Folder file access control allows unauthorized file extraction when device is unlocked.
Affected models: Galaxy S24, S23, Z Fold5, Z Flip5
Note: Active exploitation detected in targeted attacks."""

PIXEL_BULLETIN_V1 = """Pixel Update Bulletin - March 2025
Published March 5, 2025

The Pixel Update Bulletin contains details of security vulnerabilities and functional improvements affecting supported Pixel devices.

Security patches:
All Google patches from the Android Security Bulletin March 2025 are included.

Pixel-specific fixes:
CVE-2025-P001 - High
Component: Titan M2 firmware
Description: A fault injection vulnerability in Titan M2 could allow physical attackers to bypass secure boot verification.
Affected: Pixel 7, 7a, 8, 8a, 9, 9 Pro

CVE-2025-P002 - Moderate
Component: Pixel Camera HAL
Description: Buffer over-read in camera preview processing could leak sensor metadata.
Affected: Pixel 8, 8a, 9, 9 Pro

Functional updates:
- Improved adaptive battery predictions
- Fixed intermittent Wi-Fi disconnections on Pixel 9 Pro"""

PIXEL_BULLETIN_V2 = """Pixel Update Bulletin - March 2025
Published March 5, 2025 | Updated March 19, 2025

The Pixel Update Bulletin contains details of security vulnerabilities and functional improvements affecting supported Pixel devices.

Security patches:
All Google patches from the Android Security Bulletin March 2025 are included, plus the supplementary patches for CVE-2025-0096 and CVE-2025-0097.

Pixel-specific fixes:
CVE-2025-P001 - High
Component: Titan M2 firmware
Description: A fault injection vulnerability in Titan M2 could allow physical attackers to bypass secure boot verification.
Affected: Pixel 7, 7a, 8, 8a, 9, 9 Pro
Updated: Additional mitigation deployed via Play system update.

CVE-2025-P002 - Moderate
Component: Pixel Camera HAL
Description: Buffer over-read in camera preview processing could leak sensor metadata.
Affected: Pixel 8, 8a, 9, 9 Pro

CVE-2025-P003 - High (NEW)
Component: Pixel Modem firmware
Description: A heap overflow in the Pixel baseband modem allows remote code execution via crafted RRC messages.
Affected: Pixel 8, 8a, 9, 9 Pro (Exynos modem variants)
Note: Google Threat Analysis Group confirms exploitation by commercial spyware vendors.

Functional updates:
- Improved adaptive battery predictions
- Fixed intermittent Wi-Fi disconnections on Pixel 9 Pro
- New: Theft Detection Lock improvements for Pixel 7+"""

API_DIFF_V1 = """Android API Differences Report — SDK 34 to SDK 35 (Preview)
Generated: February 2025

Package android.hardware.camera2
- No changes

Package android.provider
- Class MediaStore
  - No changes

Package android.security
- Class KeyGenParameterSpec
  - No changes

Package androidx.camera.core (CameraX)
- Class CameraSelector
  - No changes
- Class ImageCapture
  - No changes

New Permissions:
- No new permissions added in this preview."""

API_DIFF_V2 = """Android API Differences Report — SDK 34 to SDK 35 (Final)
Generated: March 2025

Package android.hardware.camera2
- NEW: CameraCharacteristics.FLASH_STRENGTH_LEVEL added
- CHANGED: CameraDevice.createCaptureSession now supports multi-stream HDR

Package android.provider
- Class MediaStore
  - DEPRECATED: MediaStore.Images.Media.DATA column
  - NEW: MediaStore.getPhotoPickerIntent() — apps should use the Photo Picker API instead of direct media access

Package android.security
- Class KeyGenParameterSpec
  - NEW: setUnlockedDeviceRequired(boolean) — keys can now require device to be unlocked

Package androidx.camera.core (CameraX)
- Class CameraSelector
  - NEW: LENS_FACING_EXTERNAL for USB cameras
- Class ImageCapture
  - NEW: setOutputFormat(OutputFormat.ULTRA_HDR)
- NEW Class: CameraX.getAvailableCameraInfos() for dynamic camera discovery

New Permissions:
- NEW: android.permission.READ_MEDIA_VISUAL_USER_SELECTED — granular photo picker access
- CHANGED: READ_MEDIA_IMAGES now requires Photo Picker migration by September 2025"""

CTS_CDD_V1 = """Android Compatibility Test Suite (CTS) & Compatibility Definition Document (CDD)
Version: CTS R16 / CDD Android 14

Section 7: Hardware Compatibility

7.3.10 Biometric Sensors
- Devices implementing biometric authentication MUST meet Class 3 (Strong) requirements.
- Fingerprint sensors MUST have a false acceptance rate of less than 0.002%.
- Face unlock implementations MUST use depth sensing or IR verification.

Section 9: Security Model

9.1 Permissions
- Apps targeting SDK 34 must declare all permissions in the manifest.
- Runtime permissions MUST be revoked after 90 days of inactivity.

Section 10: Software Compatibility

10.1 WebView Compatibility
- WebView MUST be updatable via Google Play system updates.
- WebView MUST support HTTPS-only mode when enabled by the user.

CTS Test Modules (R16):
- CtsSecurityTestCases: 2,847 tests
- CtsBiometricsTestCases: 312 tests
- CtsPermissionTestCases: 1,203 tests"""

CTS_CDD_V2 = """Android Compatibility Test Suite (CTS) & Compatibility Definition Document (CDD)
Version: CTS R17 / CDD Android 15

Section 7: Hardware Compatibility

7.3.10 Biometric Sensors
- Devices implementing biometric authentication MUST meet Class 3 (Strong) requirements.
- Fingerprint sensors MUST have a false acceptance rate of less than 0.002%.
- Face unlock implementations MUST use depth sensing or IR verification.
- NEW: Devices with under-display cameras used for face unlock MUST pass the updated liveness detection test suite added in CTS R17.

Section 9: Security Model

9.1 Permissions
- Apps targeting SDK 35 must declare all permissions in the manifest.
- Runtime permissions MUST be revoked after 90 days of inactivity.
- NEW: Apps requesting READ_MEDIA_IMAGES MUST integrate with the Photo Picker API. Direct broad storage access is no longer CDD-compliant for apps targeting SDK 35.

Section 10: Software Compatibility

10.1 WebView Compatibility
- WebView MUST be updatable via Google Play system updates.
- WebView MUST support HTTPS-only mode when enabled by the user.

10.2 Camera Compatibility (NEW)
- Devices supporting CameraX MUST pass the new CameraX conformance test module.
- USB external cameras MUST be enumerable via CameraX.getAvailableCameraInfos().

CTS Test Modules (R17):
- CtsSecurityTestCases: 3,124 tests (+277 new)
- CtsBiometricsTestCases: 348 tests (+36 new, including liveness detection)
- CtsPermissionTestCases: 1,289 tests (+86 new, including Photo Picker compliance)
- CtsCameraXTestCases: 156 tests (NEW module)"""


def seed_test_data():
    """Populate the database with realistic test snapshots and changes.
    
    This is a DETERMINISTIC seeder: it clears all prior test artifacts
    (snapshots, changes, embeddings, graph) before re-creating them,
    ensuring the ablation study runs on exactly this data every time.
    """
    from rag.chunker import chunk_change
    from rag.embedder import add_chunks
    from rag.entity_extractor import extract_from_change
    from rag.knowledge_graph import KnowledgeGraph
    from config.settings import USE_SUPABASE

    init_db()
    seed_sources()

    session = get_session()

    # ── Step 0: Reset — delete all prior test artifacts in FK-safe order ──
    print("[TEST DATA] Clearing prior test data...")
    from utils.db import Recommendation, AgentEvent
    session.query(Recommendation).delete()
    session.query(AgentEvent).delete()
    session.query(Change).delete()
    session.query(Snapshot).delete()
    session.commit()

    # Clear vector store
    if USE_SUPABASE:
        from sqlalchemy import text
        from utils.db import engine
        try:
            with engine.connect() as conn:
                conn.execute(text("DELETE FROM embeddings"))
                conn.commit()
            print("[TEST DATA] Cleared pgvector embeddings.")
        except Exception as e:
            print(f"[TEST DATA] Could not clear pgvector: {e}")
    else:
        import chromadb
        from config.settings import CHROMA_PERSIST_DIR
        try:
            client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
            try:
                client.delete_collection("eci_delta_chunks")
            except Exception:
                pass
            print("[TEST DATA] Cleared ChromaDB collection.")
        except Exception as e:
            print(f"[TEST DATA] Could not clear ChromaDB: {e}")

    # ── Step 1: Seed snapshots and changes ──
    sources = session.query(Source).all()

    # Map source categories to content pairs
    content_map = {
        "security_bulletin": (BULLETIN_V1, BULLETIN_V2),
        "developer_docs": (PLAY_INTEGRITY_V1, PLAY_INTEGRITY_V2),
        "cve_feed": (CISA_KEV_V1, CISA_KEV_V2),
        "policy_update": (POLICY_V1, POLICY_V2),
        "oem_bulletin": (SAMSUNG_BULLETIN_V1, SAMSUNG_BULLETIN_V2),
    }

    # Source-name-specific overrides for sources sharing a category
    name_content_map = {
        "NVD CVE Feed (Android)": (NVD_V1, NVD_V2),
        "Pixel Update Bulletin": (PIXEL_BULLETIN_V1, PIXEL_BULLETIN_V2),
        "Android API Differences Report": (API_DIFF_V1, API_DIFF_V2),
        "Android CTS/CDD Changes": (CTS_CDD_V1, CTS_CDD_V2),
    }

    now = datetime.now(timezone.utc)
    changes_created = 0

    for source in sources:
        # Prefer name-specific content, then fall back to category
        content_pair = name_content_map.get(source.name) or content_map.get(source.category)
        if not content_pair:
            continue

        v1_text, v2_text = content_pair

        # Create V1 snapshot (1 week ago)
        snap_v1 = Snapshot(
            source_id=source.id,
            raw_text=v1_text,
            clean_text=v1_text,
            fetched_at=now - timedelta(days=7),
        )
        snap_v1.compute_hash()
        session.add(snap_v1)
        session.flush()

        # Create V2 snapshot (today)
        snap_v2 = Snapshot(
            source_id=source.id,
            raw_text=v2_text,
            clean_text=v2_text,
            fetched_at=now,
        )
        snap_v2.compute_hash()
        session.add(snap_v2)
        session.flush()

        # Compute diff
        diff_data = compute_diff(v1_text, v2_text)
        diff_text = build_diff_text(diff_data)

        if diff_data["change_ratio"] > 0:
            change = Change(
                source_id=source.id,
                prev_snapshot_id=snap_v1.id,
                new_snapshot_id=snap_v2.id,
                diff_json=diff_data,
                diff_text=diff_text,
                status="pending",
            )
            session.add(change)
            changes_created += 1
            print(f"  {source.name}: {diff_data['summary']} (ratio: {diff_data['change_ratio']})")

    session.commit()
    print(f"\n[TEST DATA] Created {changes_created} change events from {len(sources)} sources.")

    # ── Step 2: Chunk + Embed all changes ──
    print("[TEST DATA] Embedding chunks into vector store...")
    changes = session.query(Change).all()
    total_chunks = 0

    for change in changes:
        source = session.query(Source).filter_by(id=change.source_id).first()
        source_category = source.category if source else ""
        source_name = source.name if source else ""

        chunks = chunk_change(
            change, change.source_id,
            source_category=source_category,
            source_name=source_name,
        )
        if chunks:
            added = add_chunks(chunks)
            total_chunks += added

    print(f"[TEST DATA] Embedded {total_chunks} chunks.")

    # ── Step 3: Build Knowledge Graph ──
    print("[TEST DATA] Building knowledge graph...")
    kg = KnowledgeGraph()  # Fresh graph — don't load stale file

    for change in changes:
        source = session.query(Source).filter_by(id=change.source_id).first()
        entities = extract_from_change(change)
        if entities.entity_count > 0:
            kg.add_change_entities(
                change_id=change.id,
                source_id=change.source_id,
                entity_set=entities,
                source_category=source.category if source else "",
                change_label=f"{source.name} Update" if source else None
            )

    graph_path = kg.save()
    stats = kg.stats()
    print(f"[TEST DATA] Graph: {stats['total_nodes']} nodes, {stats['total_edges']} edges -> {graph_path}")

    session.close()
    print("[TEST DATA] Deterministic test environment ready.\n")


if __name__ == "__main__":
    seed_test_data()

