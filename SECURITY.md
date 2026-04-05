# Security Notice

We are aware of a public report alleging that **OneLiveRec** installs malware, including claims of persistence mechanisms, Windows Defender policy modification, and communication with known malicious infrastructure.

We take such claims seriously. After internal review and independent verification, we provide the following clarification.

---

## Reference

A public report making these claims:

* Original report:
  https://gist.github.com/KevinStreetCoder/db3e50746a25fc3b52a0a275abf0ce13

* Archived version (for integrity preservation):
  https://web.archive.org/web/20260405080548/https://gist.github.com/KevinStreetCoder/db3e50746a25fc3b52a0a275abf0ce13/revisions

This document addresses the claims made in that report.

---

## Project Nature

OneLiveRec has **never been advertised or claimed as open-source software**.
It is a proprietary application distributed via GitHub Releases for version management and distribution convenience.

---

## Independent Security Analysis

The latest release binary has been independently analyzed via VirusTotal:

**SHA-256**
`e2fa61fc225e12afa913679ee12f1b7a1f8f9854e83340eea41a851cb57cae06`

**Analysis Report**
https://www.virustotal.com/gui/file/e2fa61fc225e12afa913679ee12f1b7a1f8f9854e83340eea41a851cb57cae06

At the time of writing, the file is **not identified as malware by major antivirus engines**.

---

## Detection Breakdown

A small number of antivirus engines report heuristic or machine-learning-based detections:

| Engine     | Detection Name          | Type             | Interpretation                                                    |
| ---------- | ----------------------- | ---------------- | ----------------------------------------------------------------- |
| Gridinsoft | Trojan.Heur!.02056023   | Heuristic        | Generic heuristic detection; not tied to any known malware family |
| Trapmine   | Malicious.high.ml.score | Machine Learning | AI/ML-based classification based on similarity, not signature     |

### Interpretation

* These detections are **not signature-based** and do not indicate identification of any known malware.

* Heuristic and machine-learning detections are **prone to false positives**, especially for:

  * Newly released software
  * Unsigned binaries
  * Applications with network functionality

* No major antivirus vendors classify the file as malicious.

### Conclusion

The presence of a very small number of heuristic/ML detections, compared to the overwhelming number of clean results, is **consistent with false positives** and does not constitute evidence of malware.

---

## Response to Technical Claims

The behaviors described in the report are **not implemented in OneLiveRec**:

* No creation of scheduled tasks (including via `mshta.exe`)
* No modification of Windows Defender policies or exclusions
* No installation of persistence mechanisms or background services
* No communication with the domains referenced in the report

Such actions would require explicit implementation and elevated privileges, none of which exist in the application.

---

## Analysis of Reported Indicators

The indicators listed in the report — including:

* Randomly named DLL files in system directories
* System-wide Windows Defender exclusions
* Scheduled task persistence
* Known information-stealer infrastructure

— are consistent with **pre-existing malware infections** in compromised environments.

There is **no technical evidence provided** linking these behaviors to the OneLiveRec binary.

---

## Correlation vs. Causation

The report attributes the infection to OneLiveRec based on timing alone.

However:

* No reproducible steps are provided
* No process-level attribution (logs, parent processes) is shown
* No binary analysis connects the software to the described activity

Without such evidence, the conclusion is unsupported.

---

## Commitment to Transparency

We are committed to maintaining user trust and software integrity. We:

* Provide cryptographic hashes for verification
* Encourage independent analysis
* Welcome responsible disclosure of reproducible issues

If credible evidence is presented, we will investigate promptly.

---

## Final Statement

Based on all available evidence, there is **no indication that OneLiveRec contains malware or performs the behaviors described in the report**.

We remain open to constructive, evidence-based discussion.
