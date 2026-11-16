# Radio / regulatory hurdles to replacing radio firmware — the LibrePhone hurdle map

**Status:** full documentation session (2026-11-16/17), expanding the stub in
[upstream-contribution/blob-database/recon.md](blob-database/recon.md) §"Radio /
regulatory stub" (the stub's six enumerated dimensions are filled below, one
section each, plus the queried sources).

**⚠ This document is a hurdle map for the campaign, NOT legal advice.**
Nothing here is a legal opinion or a legal conclusion; every statutory/rule
question must go to qualified counsel before any action that depends on it.
What this document does: assemble the primary texts, the precedent record,
and the practical gate sequence, with citations and access dates, so the
campaign (and any counsel engaged later) starts from facts.

Method note: all primary texts below were fetched byte-exact on 2026-11-16
(eCFR versioner API, EUR-Lex HTML, fsf.org/librephone.fsf.org HTML, kernel
git trees); failures are recorded honestly in the RULE-0 query log at the
end. Search queries are recorded verbatim per lab RULE 0.

---

## a. Type-approval per radio — what a firmware change re-opens

Every radio in a phone (modem/cellular, WiFi, BT, GNSS, NFC) is certified as
part of a type-approved **unit**; radio firmware is inside the approved
boundary. A free-software replacement of any radio firmware therefore
re-opens the approval of the whole unit, in every jurisdiction where the
device is marketed. Per-jurisdiction picture (access date for all: 2026-11-16):

### FCC (US)

- **Statutory/rule base:** Part 15 rules for the unlicensed radios (WiFi/BT:
  §15.247, §15.407), Parts 22/24/27 for cellular licensed radios, SAR rules
  (§1.1307, §2.1093) (fetched: eCFR title 47, 2026-11-16).
- **What a firmware change triggers:** equipment authorization is granted per
  FCC ID; §2.933(a) — "A new application for certification shall be filed
  whenever there is a change in the FCC Identifier for the equipment with or
  without a change in design, circuitry or construction." Changes *within*
  the same FCC ID are governed by §2.1043 permissive changes (Class I = no
  degradation of reported characteristics, Class II = requires FCC acceptance
  **before marketing**, per KDB 178919 D01 Permissive Change Policy; guides:
  <https://www.fcc.gov/engineering-technology/laboratory-division/general/equipment-authorization>,
  <https://www.metlabs.com/wireless/rf-product-modifications-may-be-eligible-for-an-fcc-permissive-change>).
- **The killer detail (economic):** a permissive change can only be filed by
  the **original grantee** — for modular-approval radio modules
  (§15.212: "Single modular transmitters consist of a completely
  self-contained radiofrequency transmitter device …"), the module maker
  (Qualcomm, etc.) holds the grant. A third party replacing the firmware
  cannot file a permissive change on someone else's grant; its only routes
  are (i) convincing the grantee, or (ii) a **new** certification under its
  own FCC ID (full test sweep: RF conformance + SAR + EMC). Source query:
  "FCC KDB 178919 permissive change Class II firmware change re-certification
  modular approval" (2026-11-16; Spilma guide: only the original grantee can
  request a permissive change on a certified modular transmitter).
- **SDR rule — the direct anti-free-radio-firmware rule:** 47 CFR §2.944(a)
  (fetched verbatim 2026-11-16): *"Manufacturers must take steps to ensure
  that only software that has been approved with a software defined radio can
  be loaded into the radio. The software must not allow the user to operate
  the transmitter with operating frequencies, output power, modulation types
  or other radio frequency parameters outside those that were approved."*
  §2.944(b): *"Any radio in which the software is designed or expected to be
  modified by a party other than the manufacturer and would affect the
  operating parameters of frequency range, modulation type or maximum output
  power … must comply with the requirements in paragraph (a) of this section
  and must be certified as a software defined radio."* §2.944(c) requires a
  high-level operational description/flow diagram of the radio-control
  software in the application. I.e. the FCC *anticipates* third-party
  modification and locks it out (and the grantee is the entity that must
  implement the lock).
- **WiFi-specific hard lock:** 47 CFR §15.407(f) Device Security (fetched
  verbatim): *"All U-NII devices must contain security features to protect
  against modification of software by unauthorized parties"* and
  *"Manufacturers must implement security features in any digitally modulated
  devices capable of operating in any of the U-NII bands, so that third
  parties are not able to reprogram the device to operate outside the
  parameters for which the device was certified."*
- **Free-software precedent path:** none at the FCC. The SDR authorization
  framework (FCC 05-57, First Report and Order on SDRs, 2005; codified in
  §2.944) was designed to allow *grantee-controlled* software updates, never
  user-modifiable radio parameters. No FCC grant has ever covered
  user-replaceable radio firmware that changes RF parameters.

### EU — Radio Equipment Directive 2014/53/EU (RED)

- **Base text fetched** (EUR-Lex CELEX:32014L0053, 2026-11-16). Essential
  requirements Art 3(1)(a) safety, 3(1)(b) EMC, 3(2) spectrum (efficient use +
  avoidance of harmful interference); conformity via internal production
  control (Module A) **where harmonised standards are applied**, else
  EU-type examination (Module B+C) with a notified body (Art 17, Annexes II-V).
- **Software recitals (verbatim, fetched 2026-11-16):** recital (16): *"The
  compliance of some categories of radio equipment with the essential
  requirements set out in this Directive may be affected by the inclusion of
  software or modification of its existing software. The user, the radio
  equipment or a third party should only be able to load software into the
  radio equipment where this does not compromise the subsequent compliance of
  that radio equipment with the applicable essential requirements."*
  Recital (19) is the free-software counterweight: *"Verification by radio
  equipment of the compliance of its combination with software should not be
  abused in order to prevent its use with software provided by independent
  parties."* Art 10(8)-related text: where a delegated act requires it,
  information shall "precisely identify the radio equipment and the software
  which have been assessed, and it shall be continuously updated."
- **What a firmware change triggers:** re-assessment of the declaration of
  conformity (self-declared). The Commission's *Guide to the Radio Equipment
  Directive 2014/53/EU* (2022 edition, first update since 2018 — adds a
  dedicated software-updates chapter) states that an update modifying
  hardware-software interaction or radio parameters may require renewed
  conformity assessment, and where conformity can no longer be demonstrated
  under harmonised standards, **notified-body involvement** becomes mandatory
  (Guide §4.1.2.6; sources: <https://single-market-economy.ec.europa.eu/sectors/electrical-and-electronic-engineering-industries-eei/radio-equipment-directive-red_en>;
  "European Commission publishes updated Radio Equipment Directive guide,"
  iotapproval.com, 2022). EN 300 328 (2.4 GHz WiFi/BT) is the relevant
  harmonised standard for the BT fleet this lab targets first.
- **Economics:** the EU is the cheapest regime for the campaign —
  self-declaration against harmonised standards, no per-device filing fee —
  but a third-party firmware replacement voids the OEM's DoC and puts the
  *new* placing-on-market obligation on whoever re-markets the device.

### UKCA

Radio Equipment Regulations 2017 (SI 2017/1206) mirror the RED essential
requirements and modules (fetch of legislation.gov.uk failed twice this
session — recorded below; the mirroring is the standard published summary,
e.g. UK gov guidance page). Post-Brexit the UK accepts its own marking;
regime economics are close to RED's.

### India — TEC / MTCTE

- Mandatory Testing and Certification of Telecom Equipment (TEC, DoT):
  <https://www.tec.gov.in/mandatory-testing-and-certification-of-telecom-equipments-mtcte>
  (fetched with SSL workaround 2026-11-16; the site's TLS chain fails
  verification from this box — honest note), portal
  <https://eservices.dot.gov.in/mtcte>. Mobile handsets are covered in phases;
  Essential Requirements include EMI/EMC, safety, interface requirements and
  **SAR for mobile handsets** (<https://tec.gov.in/essential-requirements-2>).
- A firmware change to a certified handset re-opens the MTCTE certificate;
  testing happens at TEC-designated labs. Regime is per-device (no true
  modular-approval path for handsets; radio modules are folded into the
  product certificate).

### Japan — TELEC / MIC

- Radio Law technical-regulations conformance certification by **registered
  certification bodies** (Art 38-4/38-5; specified radio equipment = low-power
  stations get conformity certification; base stations get construction-type
  approval). The Telecom Engineering Center (TELEC) is the largest such body:
  <https://www.telec.or.jp/eng/> (fetched 2026-11-16 — page confirms the
  registered-certification-body scheme for Specified Radio Equipment and the
  "modified" module concepts). Certification is per-construction-type;
  firmware is inside the certified type.

### China — SRRC

- State Radio Regulation Committee type approval under MIIT: radio
  transmission equipment needs SRRC approval and a **CMIIT ID** printed on the
  device (12-character code); mobile phones need SRRC alongside CCC
  (overview: spilma.com SRRC/CMIIT guide, china-srrc.com; MIIT Order 57 /
  Notice 129 govern limits; older certificates had a 2025 transition).
  Per-device approval; a radio-firmware change requires a new SRRC filing
  through an approved test house.

### Brazil — ANATEL

- Homologation under Federal Law 9472/97 (Art 58: certificate of conformity
  issued by ANATEL at no charge once requirements are met, via an OCD —
  Organismo de Certificação Designado). **Act No. 77** (5 Jan 2021) adds
  cyber-security requirements for internet-connected terminal equipment
  (CSA Group/IB-Lenhardt summaries; ANATEL publication 306743). Per-device
  homologation; firmware change re-opens it.

### Modular-approval vs per-device economics (cross-jurisdiction)

| Regime | Module path | Firmware-change consequence |
|---|---|---|
| FCC | §15.212 modular (shielded, self-contained, own regulation) | permissive change **grantee-only**; third party = new full grant |
| EU RED | self-declaration per product against harmonised standards | re-assess + re-DoC; NB only if harmonised-standard presumption lost |
| UKCA | mirror of RED | same as RED |
| India MTCTE | per-device | new certificate |
| Japan TELEC | per-construction-type (module certification exists for specified radio equipment) | re-certification of the type |
| China SRRC | per-device | new SRRC filing |
| Brazil ANATEL | per-device (OCD route) | new homologation |

The structural point for LibrePhone: **in every regime the approval-holder is
the OEM or chip vendor, not the user.** Free-software radio firmware has no
"post-approval modification" lane anywhere; the closest thing to one (FCC SDR
§2.944) explicitly requires the grantee to prevent it.

### The practical bring-up gate beyond legality (stub dimension 6)

Safety/EMC liability and spectrum coexistence: SAR re-test (regulatory SAR
limits: FCC §1.1307/§2.1093; India ER-SAR; EU EN 62209 / EN 50566 path),
EMC re-test per regime, and **coexistence testing** (WiFi/BT/modem antenna
sharing — BT/WiFi coex behavior is largely *in the radio firmware and its
NVRAM configuration*, which is exactly what the lab's QCA BT fleet patch
files carry). Until those tests are re-run (hardware certification labs,
Section f), a re-flashed device is a research object, not a product.

---

## b. Legality of RE-ing radio firmware (statutes and triennial exemptions)

### US — DMCA §1201

- **Statutory interoperability exemption (no rulemaking needed),
  17 USC §1201(f)** (fetched verbatim from Cornell LII,
  <https://www.law.cornell.edu/uscode/text/17/1201>, 2026-11-16; the official
  uscode.house.gov granule page 404'd during its "temporary format" state —
  recorded in the log): §1201(f)(1): *"Notwithstanding the provisions of
  subsection (a)(1)(A), a person who has lawfully obtained the right to use a
  copy of a computer program may circumvent a technological measure that
  effectively controls access to a particular portion of that program for the
  sole purpose of identifying and analyzing those elements of the program
  that are necessary to achieve interoperability of an independently created
  computer program with other programs, and that have not previously been
  readily available to the person engaging in the circumvention, to the
  extent any such acts of identification and analysis do not constitute
  infringement under this title."* §1201(f)(2) additionally permits
  developing/employing circumvention means for that purpose; §1201(f)(3)
  permits making the acquired information available to others **solely for
  interoperability**; §1201(f)(4) defines interoperability ("the ability of
  computer programs to exchange information, and of such programs mutually to
  use the information which has been exchanged").
- **Encryption research:** §1201(g) (fetched verbatim) permits circumvention
  in good-faith encryption research subject to factors (dissemination mode,
  expertise, etc.).
- **Triennial rulemaking exemptions, 37 CFR §201.40(b)** (fetched verbatim via
  eCFR versioner API, issue date 2026-10-26, on 2026-11-16):
  - **(b)(8) wireless devices:** *"Computer programs that enable wireless
    devices to connect to a wireless telecommunications network, when
    circumvention is undertaken solely in order to connect to a wireless
    telecommunications network and such connection is authorized by the
    operator of such network."* — this is the current form of the
    **wireless-device unlocking** exemption carried through the 2015 (80 FR
    65961, Oct. 28, 2015), 2018 (83 FR 54028, Oct. 26, 2018) and 2021 (86 FR
    59637, Oct. 28, 2021) rulemakings, current as of the 2024 rule (89 FR
    85446, Oct. 28, 2024). Its scope is **connection to a network,
    grantee/operator-authorized** — it does *not* reach firmware
    reverse-engineering for replacement.
  - **(b)(9) smartphone app interoperability:** *"Computer programs that
    enable smartphones and portable all-purpose mobile computing devices to
    execute lawfully obtained software applications, where circumvention is
    accomplished for the sole purpose of enabling interoperability of such
    applications with computer programs on the smartphone or device, or to
    permit removal of software from the smartphone or device."* —
    user-level, not firmware.
  - **(b)(18) good-faith security research:** circumvention *"solely for the
    purpose of good-faith testing, investigation, and/or correction of a
    security flaw or vulnerability,"* in an environment designed to avoid
    harm, with information used primarily to promote security of the class of
    devices — this is the exemption under which modem-security RE
    (e.g. the Project Zero Exynos work, Section e) is regularly conducted.
  - **(b)(22) FOSS-investigation (2024 rule):** *"Computer programs, solely
    for the purpose of investigating a potential infringement of free and
    open source computer programs where: (i) The circumvention is undertaken
    on a lawfully acquired device or machine other than a video game console
    …"* — directly relevant to a lab investigating whether a blob embeds
    GPL-covered code.
- **Honest scope note:** the *statutory* §1201(f) interoperability exemption
  covers RE of a lawfully-used program to interoperate — the natural home for
  RE-ing a radio chip's firmware **interface** (what btqca.c does). Whether
  wholesale firmware *replacement* ("interoperate with" what — the host
  stack? the network?) stays inside §1201(f) is a counsel question, not a
  doc conclusion. Also note §1201(a)(2)/(b) anti-trafficking is not lifted by
  the (b)(1) rulemaking exemptions — distribution of circumvention tools is
  a separate line.

### EU — Software Directive 2009/24/EC Art 6 (fetched verbatim, EUR-Lex,
2026-11-16)

*"The authorisation of the rightholder shall not be required where
reproduction of the code and translation of its form within the meaning of
points (a) and (b) of Article 4(1) are indispensable to obtain the
information necessary to achieve the interoperability of an independently
created computer program with other programs, provided that the following
conditions are met: (a) those acts are performed by the licensee or by
another person having a right to use a copy of a program, or on their behalf
by a person authorised to do so; (b) the information necessary to achieve
interoperability has not previously been readily available to the persons
referred to in point (a); and (c) those acts are confined to the parts of the
original program which are necessary in order to achieve interoperability."*
Art 6(2) restricts use of the obtained information to interoperability goals;
Art 6(3) Berne-proportionality. The **InfoSoc/DRM layer** (Art 6 of Directive
2001/29, mirrored by member-state implementations) is the open flank: decomp
rights do not automatically override TPMs — a counsel question per member
state.

### UK

Copyright, Designs and Patents Act 1988 s.50B (decompilation for
interoperability — the direct UK mirror of the EU Art 6 conditions, enacted
post-Software-Directive 2009/24 implementation) and s.50C (observation and
study); the DRM counterweight is s.296 (as amended, incl. s.296ZE public-interest
exception). **Fetch failure, recorded honestly:** legislation.gov.uk returned
zero-byte responses to both curl attempts and an empty body to WebFetch on
2026-11-16, so the verbatim statutory text is NOT quoted here; the s.50B
conditions-parity with EU Art 6 is from secondary sources and should be
re-verified from the primary text when legislation.gov.uk is reachable.

### India

Copyright Act 1957, s.65A (inserted by the 2012 amendment) criminalizes
circumvention of effective TPMs *intended to infringe*; s.65A(2) carve-outs
(legal 500/JGU summaries; CIS analysis) cover personal use, education,
research, security testing, encryption research — i.e. RE for study or
security sits in carve-out territory, while s.52 fair dealing itself is *not*
fully incorporated into the TPM exceptions (documented tension in the CIS and
IJIRL analyses). A firmware-RE-for-replacement program in India needs a
jurisdiction-specific reading by counsel.

### GCF / PTCRB — the non-statutory hurdle

GCF (globalcertificationforum.org) and PTCRB (ptcrb.com) certification is
**contract-based**, not statutory: 3GPP conformance test campaigns (GCF-CC;
PTCRB NAPRD03 — test plan PDFs fetched-indexed 2026-11-16), executed at
authorized ITLs on locked-down test platforms; test cases and platform access
are member/NDA-gated (the contractual texts sit behind the GCF member portal
— the search could not and did not retrieve their clauses). For the campaign
the practical meaning: a modified modem firmware invalidates the certification
file behind the device, carriers reference PTCRB/GCF certification in purchase
requirements (see e.g. Verizon Open Development certification process, PDF
v39), and re-certification requires membership + ITL bookings. This is an
economics/contract layer on top of statutory law, and it is where the
*carrier* approvals (not just state approvals) bite.

---

## c. Export controls — crypto in modem firmware, RE tooling, published specs

- **The controlled items:** EAR Category 5, Part 2 ("information security")
  — ECCNs 5A002/5D002 for cryptographic commodities/software; since the 2016
  Wassenaar restructuring, **cryptanalytic functionality** (defeating crypto,
  extracting keys/credentials) sits in separate entries (5A004/5D004
  territory) and cannot be mass-market-exempted (BIS encryption-controls
  overview, <https://www.bis.gov/learn-support/encryption-controls>; Venable
  and Steptoe analyses of the 2016 Cat 5 Pt 2 restructuring, 2026-11-16
  search). Wassenaar Arrangement Cat 5 Pt 2 is the origin list; EU
  **Regulation 2021/1080** (dual-use recast, Annex I Category 5 Part 2;
  fetched: EUR-Lex CELEX:32021R1080, 2026-11-16 — note the EUR-Lex HTML
  fetch carries the regulation body, not the full Annex I list text; item
  numbers cited from the BIS/analysis sources above).
- **The release valve the lab actually publishes under:** EAR §734.7(a)
  (fetched verbatim): *"unclassified 'technology' or 'software' is
  'published,' and is thus not 'technology' or 'software' subject to the EAR,
  when it has been made available to the public without restrictions upon its
  further dissemination … (4) Public dissemination (i.e., unlimited
  distribution) in any form …, including posting on the Internet on sites
  available to the public."* Mass-market crypto: §740.17(b)(1) (fetched
  verbatim): *"Mass market encryption software that would be considered
  publicly available under § 734.3(b)(3) of the EAR, and is authorized for
  export under this paragraph (b), remains subject to the EAR until all
  applicable classification or self-classification requirements set forth in
  this section are fulfilled"* (self-classification report per §740.17(e)(3);
  Note 3 "mass market" items → 5A992/5D992, removed from EI/NS controls).
- **As applied to the lab's targets:** the GSM/GPRS A5/3 cipher (KASUMI) is
  publicly specified and published by 3GPP/GSMA (TS 35.202 et seq.) —
  published-algorithm status is the *input* to §734.7 publishing analysis,
  not something the lab must keep secret; SIM/network-auth RSA/ECDH usage is
  likewise public protocol (3GPP TS 33.102/33.402 families). What would cross
  into 5A004/5D004 territory: tooling whose *function* is defeating crypto or
  extracting key material from devices.
- **Charter intersection (lab F-14 policy note):** the lab's no-keys / no-
  bypass charter — publish structure and protocol facts, never key material,
  never working bypass — keeps lab outputs on the "published interoperability
  specification" side of the line and out of the cryptanalytic-functionality
  entries. The RE of *file structure* (Stream B: QCA TLV container walking)
  is pure format documentation, the least-controlled category imaginable;
  the modem's own firmware bytes (as shipped, e.g. the .tlv patch payloads)
  are published-spec-adjacent analysis, but the charter forbids shipping
  anything that functions as an auth bypass.

---

## d. The FSF's own position (exact citations, fetched 2026-11-16)

1. **librephone.fsf.org/freedom** ("Phones and Your Freedom"; fetched,
   48,904 B):
   - *"Librephone is the FSF's project to close this 'last gap' in the stack,
     reverse-engineering the necessary system components to bring cell phones
     into the free world."*
   - *"While it is possible to run a fully free distribution of Android
     called Replicant, doing so means sacrificing critical functionality:
     placing calls, taking photos, and connecting to the internet."* — i.e.
     the FSF itself frames the radio stack as the reason a "fully free"
     Android loses phone functionality.
   - *"reverse-engineering the blobs on even one of these devices is an
     enormous task"* and the project is limiting scope to *"one or two
     devices that need the least amount of work to be fully free."*
2. **librephone.fsf.org/faq** (fetched, 39,697 B):
   - *"…documenting how these proprietary blobs get used by the kernel Linux,
     in order to understand what it would take to legally reverse-engineer
     them using clean room techniques."* — the FAQ's own phrase: **legally**
     RE, **clean room** techniques.
   - *"Once there is sufficient interest and funding, a detailed
     specification will be written so that programmers who are not bound by
     the DMCA can code free implementations."* — the FSF treats the DMCA as
     the named legal hurdle and jurisdiction-shifting (non-US programmers /
     clean-room isolation) as the response.
3. **fsf.org/campaigns** (fetched, 70,986 B): *"LibrePhone is an FSF
   initiative to research and reverse-engineer proprietary firmware used by
   common Android devices. LibrePhone's goal is not a new Android
   distribution, but a long-term project to understand and write free
   implementations for the binary blobs used in virtually all mobile phones
   today."*
4. **RYF certification criteria** (<https://ryf.fsf.org/about/criteria>;
   fetched verbatim 2026-11-16 — the old
   fsf.org/resources/hw-endorsement/criteria URL now 404s, recorded in log):
   - The secondary-processor exception, verbatim: *"However, there is one
     exception for secondary embedded processors. The exception applies to
     software delivered inside auxiliary and low-level processors and FPGAs,
     within which software installation is not intended after the user
     obtains the product. This can include, for instance, microcode inside a
     processor, firmware built into an I/O device, or the gate pattern of an
     FPGA. The software in such secondary processors does not count as
     product software."*
   - The sunset clause: *"If and when free software becomes available for use
     on a certain secondary processor, we will expect certified products to
     adopt it within a reasonable period of time. … If this is not done, we
     will eventually withdraw the certification."*
   - The BIOS line: *"The BIOS of a PC runs on the CPU, not on a separate
     secondary processor, so this exception does not apply to the BIOS."*
   - **Mapping to radio firmware:** a BT/WiFi/modem chip is a genuine
     secondary processor — under RYF as written, nonfree radio firmware does
     not bar certification, *but* the moment a free implementation exists,
     products are expected to adopt it and certification eventually
     withdraws. RYF has never certified a phone with free radio firmware —
     there is no precedent product on either side of the line.
5. **Radio firmware as the acknowledged hard case:** the freedom page's
   "last gap" + Replicant-sacrifices-calls framing (item 1) is the FSF's
   standing acknowledgment that the radio stack is the component that has
   never been freed at scale. The campaign texts commit to RE-and-replace of
   "the necessary system components" without naming the regulatory stack
   above — which is precisely the gap this document maps.

---

## e. Precedents survey

### Openmoko / TI Calypso — the only fully-free modem attempt (achieved, stalled)

- OsmocomBB (<https://osmocom.org/projects/baseband/wiki>, fetched
  2026-11-16): free-software GSM Layer 1 firmware for phones built on TI's
  Calypso chipset (Motorola C123/C139/C155 class, Openmoko Neo1973/GTA01
  era); side result CalypsoBTS (a phone as micro GSM basestation). The lab's
  own fetch of the wiki plus the recorded project history: layer1 firmware +
  L2/3 host stack, running on 2006-era 2G silicon.
- FreeCalypso (<https://www.freecalypso.org/>, fetched 2026-11-16) continues
  the line (FCDEV3B board; firmware derived from TI reference sources).
- **Why it stopped:** the Calypso is GSM/2G-only by hardware; the silicon is
  discontinued; OsmocomBB mainline firmware work stagnated (items stalled on
  the tracker; FreeCalypso's FCDEV3B documentation notes mainline OsmocomBB
  does not properly support that board); and operators are shutting 2G down,
  so there is no network to run on. No Calypso path to 3G/4G/5G exists.
  (Search 2026-11-16: "OsmocomBB Calypso free GSM layer1 firmware Openmoko
  status why stopped 2G only FreeCalypso".)
- **Lesson for LibrePhone:** a fully-free modem is *proven possible* — but
  only on a self-contained, obsolete, single-protocol baseband. Modern
  Qualcomm/MediaTek modems are 100× the scope; nobody has publicly attempted
  them, which is exactly the recon.md point.

### Replicant — free host, nonfree modem (the honest current state)

- Replicant's modem strategy is free-software **around** the modem, not
  replacing it: `libsamsung-ipc` (free implementation of the Samsung modem
  IPC protocol) + `libsamsung-ril` (free RIL) talk to the **nonfree** modem
  firmware that ships on the device
  (redmine.replicant.us wiki: Samsung-ipc, Libsamsung-ril, ModemDisable
  pages; direct wiki fetch was blocked by an Anubis anti-bot challenge on
  2026-11-16 — content per the indexed pages and the 2019 contributors-meeting
  deck "Replicant and modems — Samsung IPC"). The ModemDisable page itself
  notes that even with the modem "disabled", the nonfree firmware keeps
  running.
- The 2014 FSF blog entry ("Replicant developers find and close Samsung
  Galaxy backdoor") is the concrete demonstration of why free host + nonfree
  modem matters: the free RIL simply did not implement the modem's remote
  file-access backdoor.

### Qualcomm mainline split — ath11k/ath10k: board data vs firmware blob

- linux-firmware WHENCE (kernel.org linux-firmware tree, fetched 2026-11-16):
  ath11k firmware ships as **separate files per chip dir** —
  `ath11k/WCN6855/hw2.0/{regdb.bin, board-2.bin, amss.bin, m3.bin}` — i.e.
  the *regulatory database* (regdb), the *board calibration data* (BDF), and
  the *firmware proper* (amss + m3) are separate artifacts, and only the
  last are truly opaque code; the board/regdb parts are data the host
  driver (ath11k, GPL) feeds over QMI. The WCN6750 (the FP6's WiFi chip)
  follows the same layout, and this lab has already built the free host-side
  counterparts (implementations/ wmi/tlv, ce/service-model, htc/frame-layer —
  see implementations/README.md).
- **What is precedent-setting for LibrePhone:** the industry already accepts
  a split where the *device-specific, non-executable* parts of the radio
  configuration are freely-visible data and the executable blob is separate.
  A free-BT-firmware strategy can inherit that split: ROM on chip, patch
  TLV, NVRAM config are three layers, and the third (NVRAM) is data, not
  code.

### MediaTek MOLY

- Public RE state: NCC Group / Fox-IT released a Ghidra loader for
  MediaTek modem images (`nccgroup/mtk_bp`, Kaitai format defs for
  md1img; MOLY main firmware runs on nanoMIPS cores, paired with their
  nanoMIPS Ghidra processor extension); TASZK "BugTales" documents CSN.1
  bug-hunting tooling for Helio basebands; `cyrozap/mediatek-lte-baseband-re`
  holds earlier LTE baseband notes (search 2026-11-16: "MediaTek MOLY modem
  firmware reverse engineering md1img open source"). Nobody publishes a free
  MOLY replacement.
- Cross-reference to the lab's own work: the rosemary census (mediatek/
  rosemary-census.md, F-31) identified the md1img container + MIPS32
  LE/MIPS16e modem regions on MT6785 — consistent with the NCC tooling's
  target family, and `implementations/mediatek/md1rom-taskmap` +
  `md32-interface` are the lab's structural counterparts.

### Google Tensor — Samsung Exynos modem (the cautionary tale)

- Pixel 6/7 Tensor phones carry Samsung Exynos modems (Exynos 5120/5300
  family). Google Project Zero, March 2023: 18 vulnerabilities in Samsung
  Exynos chipsets, including **four internet-to-baseband RCE** flaws
  (CVE-2023-26072/73/74/75 et al.) exploitable with no user interaction —
  attacker needs only the victim's phone number; tested on Pixel 7
  (<https://projectzero.google/2023/03/multiple-internet-to-baseband-remote-rce.html>,
  search 2026-11-16). Google's interim mitigation was to turn off the
  vulnerable radio paths (VoLTE/WiFi-calling off) — "shut in radio" is the
  phrase this program uses for the modem being sealed off from user repair.
- Aftermath: Google is reported to be moving Tensor modems off Samsung
  silicon (MediaTek-derived) starting Pixel 11-era (2026-11-16 search).
- **Lesson:** the opaque, vendor-sealed modem is both the security worst
  case and the component users cannot fix — the strongest campaign framing
  for why the RE work matters, and simultaneously the strongest regulator
  framing for why they want firmware locked.

---

## f. Pragmatic close — what the lab can do, in what order

**What the lab CAN document (now, legally benign, no counsel needed):**
- File/container **structure** and driver↔blob **interface** facts from GPL
  sources + device metadata: exactly what `implementations/qca-bt/`
  (shipped this session, next to this doc) does for the six-file QCA BT
  patch/NVRAM fleet (29 devices per file), what `implementations/mediatek/`
  did for MTK containers, what `qualcomm-fp6/docs/bt-firmware-census.md`
  did for the FP6 BT partition.
- Negative results, coverage matrices, protocol tables (btqca.c's documented
  download protocol is GPL-published fact, not lab RE).
- Everything above is published-interoperability-specification activity
  (§734.7 "published" analysis, Section c) and clean-room per the FSF's own
  stated method (Section d).

**What needs legal counsel (before action, not before documentation):**
- The exact reach of 17 USC 1201(f) for firmware *replacement* vs
  *interface interoperability* (Section b scope note) and any §1201
  anti-trafficking exposure for distributing tools.
- EU member-state TPM-vs-decompilation interactions; India s.65A carve-out
  applicability; UK s.50B primary-text verification (fetch failed this
  session).
- GCF/PTCRB contractual terms if the campaign ever seeks certification.
- Any jurisdiction where the campaign would *distribute flashed devices*
  (that is where RED/UKCA/MTCTE/SRRC/ANATEL/FCC per-device duties attach to
  the campaign as a "placing on market" actor).

**What needs hardware certification labs (not law, not documentation):**
- SAR re-test (FCC §2.1093 path / India ER-SAR / EU EN 62209), EMC re-test,
  RF conformance (GCF/PTCRB campaigns at ITLs), WiFi/BT/modem coexistence
  regression — the BT coex behavior partly *lives in* the NVRAM files the
  lab parses, so this is also the technical risk point for any free
  replacement.

**Recommended order of operations for LibrePhone (lowest regulatory heat
first):**
1. **Bluetooth (the fleet this session targets).** Short-range, unlicensed
   band (Part 15 / EN 300 328), no network-auth crypto, the *download
   protocol and file structure are already public* in btqca.c/h (GPL), and
   one RE pass frees up to 29 devices (recon.md top-20 rows 1-6). Regulatory
   path even for a flashed device is the lightest of all radios.
2. **WiFi.** Precedent split exists (ath11k BDF/regdb vs amss); free host
   stacks are mature; but U-NII device-security rules (§15.407(f)) and DFS
   make firmware replacement the first place the anti-modification rules
   bite — document structure first, replacement later.
3. **GNSS** (receive-only, minimal approval burden) and **NFC**.
4. **Cellular modem — last.** Every wall above stacks here: per-device
   re-approval in 7+ regimes, GCF/PTCRB contracts, the SDR lock, network
   crypto, safety/coex testing. The campaign documents structure and
   security (the P0-style findings are the public-interest case) while the
   replacement question goes to counsel + certification partners.

**One-paragraph status for the campaign:** the legal permission structure
for *documenting* radio firmware (US §1201(f), EU Art 6, India carve-outs)
is in decent shape; the permission structure for *shipping replacements* is
essentially absent, because every type-approval regime is built on
grantee-held authorizations with firmware inside the approved envelope; and
the FSF's own campaign acknowledges this by targeting RE/clean-room
specification first, with implementations to follow "once there is
sufficient interest and funding." The lab's charter (structure-only,
no-keys/no-bypass) is exactly on the documented-now side of every line
mapped above.

---

## RULE 0 — query log (all 2026-11-16, with outcomes)

Web/code searches (recorded verbatim):
1. `"crbtfw" OR "apbtfw" parser` (GitHub code search) → 84 hits; the only
   content-parsing prior art is CrimsonGlory/wairz `bt_firmware_banner.py` +
   `bt_qca_codenames.yaml` (banner/codename extraction, filename-prefix →
   CHE/APA/CMC mapping, banner-at-end finding); the rest is packaging
   manifests (vendor.mk/proprietary-files.txt) and a kernel backport patch.
   Delta built in implementations/qca-bt/ (structural TLV walking — no
   public structural parser exists).
2. `"radio firmware reverse engineering DMCA exemption"` (framing query for
   this doc; informed Sections a/b).
3. `"RED 2014/53/EU software update re-certification"` → RED Guide 2022
   software chapter (§4.1.2.6) located; Section a EU part.
4. `"FCC KDB 178919 permissive change Class II firmware change
   re-certification modular approval"` → grantee-only finding; Section a.
5. `"TEC MTCTE essential requirements mobile phone certification India
   procedure phases"` → Section a India.
6. `"China SRRC type approval CMIIT ID … Brazil ANATEL homologation Act 77"`
   → Section a China/Brazil.
7. `"RED Guide 2022 software updates conformity assessment … EN 300 328
   notified body"` → Section a EU.
8. `"GCF certification agreement NDA test platform PTCRB certification terms
   contract restrictions 3GPP conformance"` → Section b (contract texts
   themselves not publicly retrievable — stated as such).
9. `"Replicant modem status wiki samsung-ipc RIL modem firmware nonfree
   redmine"` → Section e.
10. `"OsmocomBB Calypso free GSM layer1 firmware Openmoko status why stopped
    2G only FreeCalypso"` → Section e.
11. `"MediaTek MOLY modem firmware reverse engineering md1img open source"`
    → Section e (nccgroup/mtk_bp et al.).
12. `"Google Project Zero Exynos baseband vulnerability 2023 Pixel Tensor
    Samsung modem shut in radio"` → Section e.
13. `"ECCN 5A002 cryptanalysis Wassenaar category 5 part 2 cryptanalytic
    functionality item"` → Section c (5A004/5D004 separation).
14. `"India Copyright Act section 65A technological protection measures
    circumvention exceptions 2012 amendment fair dealing section 52"` →
    Section b India.
15. `"RYF Respects Your Freedom certification criteria firmware secondary
    processors site:fsf.org"` → located the moved criteria page
    (ryf.fsf.org/about/criteria); Section d.

Primary-source fetches (byte-exact, 2026-11-16): eCFR versioner API
(37 CFR 201.40; 47 CFR 2.933/2.944/15.212/15.407; 15 CFR 740.17/734.7);
EUR-Lex (2009/24/EC, 2014/53/EU, 2021/1080); Cornell LII (17 USC 1201);
fsf.org/campaigns; librephone.fsf.org/{freedom,faq}; ryf.fsf.org/about/criteria;
osmocom.org/projects/baseband/wiki; freecalypso.org; telec.or.jp/eng/;
tec.gov.in/mtcte (TLS verification failed; fetched with certificate check
disabled — content used for scheme description only); kernel btqca.h/btqca.c/
hci_qca.c (raw.githubusercontent torvalds/linux master); linux-firmware
WHENCE (git.kernel.org) incl. qca/ and ath11k/ entries.

Fetch failures / workarounds, recorded honestly:
- librephone.fsf.org: WebFetch timed out twice; recovered with curl
  --retry 3 (bytes match the recon.md route-table sizes 48,904/39,697).
- legislation.gov.uk (CDPA s.50B, SI 2017/1206): zero-byte responses ×2
  (curl) and empty WebFetch body — UK statutory text NOT quoted verbatim;
  flagged for re-fetch.
- uscode.house.gov granule URL 404 (site "temporary format"); Cornell LII
  used as the fetched source instead.
- redmine.replicant.us: Anubis proof-of-work anti-bot challenge blocks
  non-JS fetches; content cited from indexed pages, flagged for manual
  re-verification.
- tec.gov.in: SSL certificate verification failure; fetched with `-k` for
  scheme description only.
- linux-firmware: `firmware/WHENCE` 404 in the linux tree; fetched from the
  linux-firmware git (git.kernel.org plain). kvalo/ath11k-firmware readme
  API 404 (repo moved/renamed) — WHENCE ath11k entries used instead.
- ath11k.rst: three candidate Documentation paths 404'd (doc moved across
  kernel versions); linux-firmware WHENCE per-chip file listing used as the
  fetched evidence of the split.

## Improvements to prior work (Rule 1)

- recon.md §"Radio / regulatory stub" — added a pointer to this document
  (the stub's flag said "dedicated documentation session required"; the
  session now exists).
- implementations/README.md — qca-bt row added to the component table when
  the parser lands (see the stream-B README for its RULE-0 delta record).
