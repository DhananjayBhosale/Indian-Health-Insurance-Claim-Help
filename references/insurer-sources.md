# Official insurer source map

Last checked: 2026-10-19, link status only (every URL re-checked; pinned asset links replaced with stable pages where confirmed). Upload rules and caveats are from the 2026-08-20 audit (live upload-route checks 2026-08-19/20) unless a row says otherwise. "Not re-checked 2026-10-19" means automated checks could not reach the site.

This is a dated research map for reimbursement-document preparation. It is not an exhaustive list of every Indian insurer, product, group-policy administrator, TPA, or portal. Always verify the claimant's exact product/UIN and authenticated submission route.

IRDAI's current rosters list 25 ordinary general insurers and 7 standalone health insurers that may offer indemnity health cover. This map has a routing section for that 32-insurer universe as checked above; Agriculture Insurance Company and ECGC are specialised insurers outside this hospital-reimbursement scope. Company names, licences, products, and portals can change, so re-check the [IRDAI general-insurer roster](https://irdai.gov.in/list-of-general-insurers) and [standalone health-insurer roster](https://irdai.gov.in/health-insurers1).

## Precedence

IRDAI regulations bind both the policy and the portal. Within them, the policy wording decides what is covered and the portal decides how files are uploaded. Use this order when instructions differ:

1. Current authenticated portal or written claim query for this claim.
2. Exact policy wording, schedule/customer information sheet, and current product/UIN claim form.
3. Current official insurer/TPA claim page.
4. This dated source map.
5. Common baseline checklist.

Record conflicts. Never silently choose a longer coverage window or later filing deadline.

## Public upload-rule snapshot

The PDF is only a container. Insurers want readable, complete, unaltered evidence: identity, medical advice, service/result, itemized charge, proof of payment. Most publish no DPI, page-size, filename, merge-order, page-count, OCR, PDF/A, or encryption rule.

Set `verification.portal.max_file_mb` (or a pack-specific `max_file_mb`) only when the current official source or live portal confirms it. Limits are route-specific (per file, total, one category, or a query screen only). Record the journey in `verification.portal.rule_scope`; never carry a number or extension list between routes or insurers. The "Known upload rule" column is the public snapshot.

## Insurer table

| Insurer | Official claim page | Claim form / download page | Known upload rule | Key caveat |
|---|---|---|---|---|
| HDFC ERGO | [Reimbursement](https://www.hdfcergo.com/claim/register-health-insurance-claim/reimbursement) · [Checklist](https://www.hdfcergo.com/claim/register-health-insurance-claim/document-check-list) | [Form selector](https://www.hdfcergo.com/download/claim-form/health) | 10 MB per uploaded document | No page-count, DPI, filename, or encryption rule published. See note below. |
| Star Health | [Claims](https://www.starhealth.in/claims/) · [Upload guide](https://www.starhealth.in/help/internal/health-upload-documents/) | [Form](https://d28c6jni2fmamz.cloudfront.net/CLAIMFORM_89ec9742bd.pdf) (snapshot, may move) | Not published — check portal | Not re-checked 2026-10-19 (site blocked checks). Mark uploads original/photocopy; sources conflict 15 vs 30 days. |
| Niva Bupa | [Claims FAQ](https://transactions.nivabupa.com/claims/pages/health-claim.aspx) | [Uploader](https://transactions.nivabupa.com/claims/pages/claimdocupload.aspx) | Initial uploader: 5 MB per file; JPG/JPEG/GIF/PDF/PNG | Additional-document screen says up to 7 files, variant extensions; not an initial-route limit. May request physical documents. |
| Care Health | [Claim center](https://www.careinsurance.com/health-insurance-claim-center.html) | [Forms](https://www.careinsurance.com/health-insurance-claim-forms.html) | Not published — check portal | Blocks automated fetch; forms page confirmed in a browser 2026-10-19, claim center not. |
| ICICI Lombard | [Support/FAQ](https://www.icicilombard.com/customer-support) · [Upload portal](https://ilhc.icicilombard.com/Customer/DocumentUpload) | Support page links "Download Health Insurance Claim Form" | PDF/JPG/PNG, 10 MB per file | Query route narrows to PDF/JPG; Part B may not be needed for a later pre/post claim. |
| Bajaj General (formerly Bajaj Allianz General) | [Claim process](https://www.bajajgeneralinsurance.com/health-insurance-plans/health-insurance-claim-process.html) | [Form A+B](https://www.bajajgeneralinsurance.com/download-documents/claim/health/ReimbursementFormA%2BB2016.pdf) | Not published — check portal | Part B is hospital-completed and sealed; form records pre/post separately; some routes still want originals. |
| Tata AIG | [Claims process](https://www.tataaig.com/claims-process) | [Downloads](https://www.tataaig.com/downloads) | Not published — check portal | Form asks for original financial documents; do not reuse old email limits from special programs. |
| Aditya Birla Health | [Reimbursement](https://www.adityabirlacapital.com/healthinsurance/reimbursement-claims) | [Digital form](https://www.adityabirlacapital.com/healthinsurance/claim/reimbursement-claim-form) | Initial digital screen: PDF/PNG/JPG/JPEG, 10 MB; PDF minimum 10 KB | Query route can be PDF-only; another official view says under 5 MB; record the exact screen. |
| ManipalCigna | [Claims](https://www.manipalcigna.com/claims/) | [Claim downloads](https://www.manipalcigna.com/downloads/claims) | Not published — check portal | Originals/certified-copy rules vary by product. |
| IndusInd General (formerly Reliance General) | Earlier pages all 404 on 2026-10-19; find the current health-claims page from the site home | None confirmed | 5 MB per file (2026-08-20; source page now 404, re-verify) | Not re-checked 2026-10-19 (pages gone). Scans accepted; physical originals may be requested. |
| SBI General | [Claim portal](https://www.sbigeneral.in/webportal/claim/claims-status-and-intimation) | [Forms](https://www.sbigeneral.in/claim/claims-form-download) | Not published — check portal | Product wordings vary on originals/KYC; some routes direct physical originals. |
| New India Assurance | [Mediclaim prospectus](https://www.newindia.co.in/assets/docs/know-more/health/new-india-mediclaim-policy/Prospectus%20New%20India%20Mediclaim%20Policy.pdf) (PDF) | [Claim form Part A](https://newindia.co.in/assets/docs/know-more/health/Claim_Form.pdf) | Not published — check portal | Originals required; deadlines differ by product; certified copies accepted with another insurer's settlement advice. |
| United India | [Individual Health product](https://uiic.co.in/web/product/health/Individual-Health-Insurance-Policy) | [Claim forms](https://uiic.co.in/web/claims/claim-forms) | Not published — check portal | Originals in patient's name; electronic collection does not waive originals. Prospectus PDF 404 on 2026-10-19. |
| Oriental Insurance | [Claims](https://orientalinsurance.org.in/claims) (HTTP 200, content not verified) · [Procedure](https://oicl-cms-media.s3.ap-south-1.amazonaws.com/Procedures_to_be_followed_by_the_policyholder_for_claim_settlement_under_178526dd5d.pdf) (snapshot, may move) | CSC e-claim page unreachable 2026-10-19 | Not published — check portal | Attested originals; an e-claim route does not waive originals. |
| National Insurance | [National Mediclaim](https://nationalinsurance.nic.co.in/products/all-products/health/national-mediclaim-policy-individual-plan) | Product page hosts claim form and prospectus | Not published — check portal | Form inventories main/pre/post/pharmacy bills; deadline summaries can conflict with prospectus; use earliest. |
| ACKO General | [Reimbursement](https://www.acko.com/health-insurance/reimbursement/) | [Downloads](https://www.acko.com/download/) | Not published — check portal | Generic and product pages conflict on filing dates; write-on-scan instructions are corporate-route only. |
| Go Digit General | [File a claim](https://www.godigit.com/health-insurance/file-a-claim) · [FAQ](https://www.godigit.com/health-insurance/frequently-asked-questions) | [Form](https://www.godigit.com/content/dam/godigit/directportal/en/downloads/health/claim-form-for-health-insurance-policies.pdf) | Photos or PDFs; FAQ says JPG/JPEG/PDF; no numeric limit found | Hard-copy exception for a named group route; deadlines conflict across products; ignore DigiLocker limits. |
| Cholamandalam MS General | [Health claims](https://www.cholainsurance.com/health-claims) | [Downloads](https://www.cholainsurance.com/downloads) | Not published — check portal | Public route is hard copy to a branch or the Chennai claims office. Older uportal pages 503 on 2026-10-19. |
| Generali Central (formerly Future Generali) | [Claim process](https://www.generalicentralinsurance.com/health-insurance/health-claim-process) | [Online form](https://www.generalicentralinsurance.com/health-insurance/health-claim-process/health-claim-form) | PDF/JPG/JPEG/DOC/DOCS/XLS/XLSX; 5 MB total upload | 5 MB is a total, not per file; corporate and individual routes differ; originals kept one year. |
| IFFCO Tokio General | [Claims](https://www.iffcotokio.co.in/health-insurance/claims) | [Claim forms](https://www.iffcotokio.co.in/claims/claim-forms) | Not published — check portal | QCS app photo route is full-and-final below its threshold, no pre/post; avoid when later expenses follow. |
| Zurich Kotak General (formerly Kotak Mahindra General) | [Health claim](https://one.zurichkotak.com/services/claims/health-insurance-claim) | [Claims and forms](https://www.zurichkotak.com/claims) (HTTP 200; content not read directly) | Not published — check portal | Form records pre/post separately; periods and deadlines are product-specific. |
| Narayana Health Insurance | [Reimbursement](https://www.narayanahealth.insurance/reimbursement-claim) | [Support and forms](https://www.narayanahealth.insurance/customer-support) | Not published — check portal | Originals go to the insurer; pre/post windows vary by product and network. |
| Galaxy Health Insurance | [Reimbursement](https://www.galaxyhealth.com/claims/reimbursement-claim) | [Products](https://www.galaxyhealth.com/our-product-list) | Not published — check portal | "Scan/Upload" wording is insurer-side handling, not a claimant spec; later post-expense filing unclear. |
| Liberty General | [Health claims](https://www.libertyinsurance.in/products/claims/health-claims) | [Forms](https://www.libertyinsurance.in/customer-support/download-forms.html) | Not published — check portal | Pre/post list pairs bill + receipt + prescription (+ report); general and product deadlines conflict. |
| Royal Sundaram General | [Health claims](https://www.royalsundaram.in/claims/health-insurance-claims) | [Forms](https://www.royalsundaram.in/forms-central-download) | Not published — check portal | Not re-checked 2026-10-19 (site blocked checks). Windows differ by plan, variant, add-on. |
| Universal Sompo General | [Claim status/upload](https://www.universalsompo.com/health-claim-status/) | [Forms](https://www.universalsompo.com/claims/claims-forms/) | Not published — check portal | Certified copies accepted with another insurer's settlement advice; extensions change pre/post periods. |
| Zuno General | [Health claim](https://www.hizuno.com/health-insurance/health-claim) | [Downloads](https://www.hizuno.com/downloads) | Not published — check portal | Covering letter plus expense schedule; use the UIN inside the wording, not the filename. |
| Navi General | [Health](https://navi.com/insurance/health) | [FAQ](https://navi.com/insurance/faq) | Not published — check portal | App route; windows and deadlines specific to the current Navi Health generation. |
| Raheja QBE General | [Health claims](https://rahejaqbe.com/claims/health-claims) | [Product/UIN register](https://www.rahejaqbe.com/compliance) | Not published — check portal | Live page says 30 days; wording says 15; use the earlier date. |
| Shriram General | [Claims](https://www.shriramgi.com/claims) | [Claim forms](https://www.shriramgi.com/download/claim) | Not published — check portal | Base and add-on windows differ; do not reuse limits from unrelated Shriram uploaders. |
| Magma General (formerly Magma HDI) | [Claim process](https://www.magmainsurance.com/claim-process) | [Downloads](https://www.magmainsurance.com/web/magmainsurance/downloads) | Not published — check portal | Retail route wants physical originals; linked wording may show different UIN generations. |
| Kshema General | [Claim intimation](https://kshema.co/claim-intimation/) | [Home](https://kshema.co/) links the dated product-list PDF | Not published — check portal | Fixed-benefit and PA products only; out of scope for this indemnity packet model. |

### HDFC ERGO note

The form and claim manual (both on the selector) give the strongest common pre/post rule: medicine = prescription + bill + receipt; investigation = advice/referral + report + bill + receipt; consultation = note/prescription + bill + receipt. The bill register records number, date, issuer, purpose, amount.

On 2026-08-20 the live site and the downloaded Optima Secure materials showed different UIN generations: use the selector and compare the claimant's UIN. Public pages mix online scans with requests for originals; keep paper originals. Windows and deadlines are product-specific.

## Regulator

- [IRDAI Health Department and FAQs](https://irdai.gov.in/health-dept)
- [IRDAI Master Circular on Health Insurance Business, 29 May 2024](https://irdai.gov.in/document-detail?documentId=4942918)
- [IRDAI Master Circular on Protection of Policyholders' Interests, 5 September 2024](https://irdai.gov.in/document-detail?documentId=5625747)

After claim intimation, the IRDAI health circular places responsibility on insurers/TPAs to collect required hospital-held records from the hospital. Do not misread this as permission to omit claimant-held pre/post prescriptions, pharmacy bills, reports, receipts, bank/KYC records, or other evidence requested for reimbursement.

The policyholder-protection circular gives a 15-day settlement turnaround for reimbursement claims from submission of the claim (Ch. V, 3(iii)(6)), with interest at 2% above the bank rate when late (Ch. V, 2(ii)). The 30/45-day figures still shown on some IRDAI FAQ pages come from repealed 2016/2017 regulations. That turnaround is not the claimant's filing deadline; product and claim-route deadlines still control. IRDAI guidance does not make one static PDF packet universally sufficient. See [after-submission.md](after-submission.md) for intimation, queries, rejection rights, and complaints.

## Unlisted insurer or TPA

Use the common evidence model and keep status `PORTAL_RULES_UNVERIFIED` until you have: insurer and TPA identity; exact product/UIN wording and schedule; current claim form/checklist; main versus supplementary pre/post route; exact portal screen with file types, limits, categories, and upload count; original/certified-copy/physical rules; deadlines and covered pre/post periods. Do not call an unverified common bundle insurer-approved.
