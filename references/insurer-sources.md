# Official insurer source map

Last checked: 2026-08-20 (full roster/source-map re-audit, with live upload-route checks performed 2026-08-19 to 2026-08-20).

This is a dated research map for reimbursement-document preparation. It is not an exhaustive list of every Indian insurer, product, group-policy administrator, TPA, or portal. Always verify the claimant's exact product/UIN and authenticated submission route.

IRDAI's current rosters list 25 ordinary general insurers and 7 standalone health insurers that may offer indemnity health cover. This map has a routing section for that 32-insurer universe as checked above; Agriculture Insurance Company and ECGC are specialised insurers outside this hospital-reimbursement scope. Company names, licences, products, and portals can change, so re-check the [IRDAI general-insurer roster](https://irdai.gov.in/list-of-general-insurers) and [standalone health-insurer roster](https://irdai.gov.in/health-insurers1).

## Precedence

Use this order when instructions differ:

1. Current authenticated portal or written claim query for this claim.
2. Exact policy wording, schedule/customer information sheet, and current product/UIN claim form.
3. Current official insurer/TPA claim page.
4. This dated source map.
5. Common baseline checklist.

Record conflicts. Never silently choose a longer coverage window or later filing deadline.

## What the PDF re-audit found

Across the reviewed insurers, the PDF is only a delivery container. The recurring substantive expectation is readable, complete, unaltered evidence: patient/episode identity; medical advice or necessity; service/result; itemized charge; and proof of payment. Most insurers do not publish a universal DPI, page-size, filename, merge order, page-count, OCR, PDF/A, or encryption specification.

Portal limits are route-specific. A rule may apply per file, to the whole submission, to one category, or only to an additional-document/query screen. Record the exact journey in `verification.portal.rule_scope`; never transplant a number or extension list between initial, supplementary, query, app, TPA, email, and physical-original routes.

## Public upload-rule snapshot

Only use `verification.portal.max_file_mb` (or a pack-specific `max_file_mb`) when the current official source or live portal confirms it.

| Insurer | Publicly confirmed rule at last check | Important caveat |
|---|---|---|
| HDFC ERGO | 10 MB per uploaded document | Public page does not state page count, DPI, filename, or encryption rules |
| Niva Bupa | Initial uploader: 5 MB per file; JPG/JPEG/GIF/PDF/PNG | Additional-document screen separately says up to 7 files and shows variant extension wording; do not apply that count to the initial route |
| ICICI Lombard | PDF/JPG/PNG, 10 MB per file | No public combined-file/page/DPI rule |
| Aditya Birla Health | Initial digital reimbursement screen: PDF/PNG/JPG/JPEG, 10 MB; PDF minimum 10 KB | Its query route can be PDF-only; image-minimum text is internally inconsistent and another official view says under 5 MB, so record the exact screen |
| IndusInd General (formerly Reliance General) | 5 MB per file | Public health flow does not state an extension list |
| Generali Central (formerly Future Generali) | PDF/JPG/JPEG/DOC/DOCS/XLS/XLSX; 5 MB total upload | The 5 MB figure is a total, not a per-file limit |
| Go Digit | Photos or PDFs; a current FAQ says JPG/JPEG/PDF | No public numeric health-claim limit found |
| Other reviewed insurers | No reliable public claim-upload limit found | Check the authenticated portal/TPA; do not reuse another insurer's limit |

## HDFC ERGO

Official sources:

- [Reimbursement process and 10 MB upload statement](https://www.hdfcergo.com/claim/register-health-insurance-claim/reimbursement)
- [General health claim document checklist](https://www.hdfcergo.com/claim/register-health-insurance-claim/document-check-list)
- [Live product/UIN claim-form selector](https://www.hdfcergo.com/download/claim-form/health)
- [Optima Secure claim form snapshot](https://customer-portal-assets.hdfcergo.com/assets/v2/docs/default-source/downloads/claim-forms/myoptima-secure---cf-58675432702.pdf)
- [Optima Secure claim manual snapshot](https://customer-portal-assets.hdfcergo.com/assets/v2/docs/default-source/downloads/claim-forms/my-optima-secure---cm-783226902747.pdf)
- [General pre/post explainer](https://www.hdfcergo.com/health-insurance/pre-and-post-hospitalization-expenses)

The form/manual supports the strongest common pre/post rule: medicine needs prescription + bill + receipt; investigation needs advice/referral + report + bill + receipt; consultation needs note/prescription + bill + receipt. The bill register records number, date, issuer, purpose, and amount.

Important: the live site and downloaded claim materials showed different Optima Secure UIN generations at the last check. Use the selector and compare the claimant's UIN. HDFC's public pages also mix online scans with requests for originals; preserve paper originals. Coverage windows and submission deadlines are product-specific.

## Star Health

Official sources:

- [Claims page](https://www.starhealth.in/claims/)
- [Current linked reimbursement form](https://d28c6jni2fmamz.cloudfront.net/CLAIMFORM_89ec9742bd.pdf)
- [Document-upload guide](https://www.starhealth.in/help/internal/health-upload-documents/)
- [Reimbursement intimation guide](https://www.starhealth.in/help/internal/health-claim-reimbursement/)
- [Pre/post guide](https://www.starhealth.in/health-insurance/pre-and-post-hospitalisation-cover-in-health-insurance/)
- [Current product list](https://www.starhealth.in/list-products/)

Star asks users to classify uploads as original or photocopy and give a reason for a photocopy. Its current checklist also includes a treating-doctor certificate. It may require the full original set after digital upload, and a PDF does not replace original imaging films. Official sources conflicted on 15 versus 30 days; verify the exact policy/UIN and act on the safer earlier deadline. No public claim upload-size/extension limit was found.

## Niva Bupa

Official sources:

- [Claims FAQ and process](https://transactions.nivabupa.com/claims/pages/health-claim.aspx)
- [Live claim-document uploader](https://transactions.nivabupa.com/claims/pages/claimdocupload.aspx)
- [Claim document checklist](https://transaction.nivabupa.com/claims/clientlibs/library/docs/Claim%20Document%20Checklist.pdf)
- [Pre/post explainer](https://www.nivabupa.com/health-insurance-articles/what-are-pre-and-post-hospitalization-expenses-in-health-insurance.html)

The initial uploader has distinct slots for discharge, consultation prescription, hospital bill/breakup with payment details, reports, personalized cheque, and KYC. It states 5 MB per file and accepts JPG/JPEG/GIF/PDF/PNG. The additional-document screen separately states up to seven files and shows variant extension wording; that is not an initial-claim limit. The route can still request physical documents, so preserve them. Pre/post claims must reference the main hospitalization claim. KYC threshold wording and live required fields can differ; follow the current route.

## Care Health

Official sources:

- [Claim center](https://www.careinsurance.com/health-insurance-claim-center.html)
- [Claims procedure PDF](https://cms.careinsurance.com/cms/public/uploads/claimsprocedurepdf/Claims_Procedure.pdf)
- [Current claim forms landing page](https://www.careinsurance.com/health-insurance-claim-forms.html)
- [Reimbursement-form guide](https://www.careinsurance.com/blog/health-insurance-articles/how-to-fill-health-insurance-reimbursement-form)

The common packet includes signed form where applicable, original discharge summary, itemized final bill, paid receipt, investigation reports, and indoor case papers when required. No reliable public claim-upload size or extension rule was found. Use the forms landing page rather than pinning a revision-token URL.

## ICICI Lombard

Official sources:

- [Customer support and claim FAQ](https://www.icicilombard.com/customer-support)
- [Current health claim form snapshot](https://www.icicilombard.com/docs/default-source/apps/healthclaims/assets/files/claim-form-less-then-1-lac.pdf)
- [Reimbursement guide](https://www.icicilombard.com/health-insurance/blogs/how-to-ensure-your-reimbursement-claim-on-health-insurance)
- [Document upload portal](https://ilhc.icicilombard.com/Customer/DocumentUpload)

The public route supports PDF/JPG/PNG up to 10 MB per file for the documented upload journey; one query-upload instruction narrows the list to PDF/JPG. Pre/post claims follow the main hospitalization claim, and Part B may not be required for that later claim. Product examples have materially different coverage periods; read the exact wording.

## Bajaj General Insurance

Former name: Bajaj Allianz General Insurance.

Official sources:

- [Health claim process](https://www.bajajgeneralinsurance.com/health-insurance-plans/health-insurance-claim-process.html)
- [Current reimbursement Form A + B](https://www.bajajgeneralinsurance.com/download-documents/claim/health/ReimbursementFormA%2BB2016.pdf)
- [Online health claim portal](https://www.bajajgeneralinsurance.com/claims/health-insurance/claim-process.html)

Part A is for the insured; Part B is hospital-completed, signed, and sealed. The form separately records pre and post amounts/bill counts and supports a later supplementary pre/post claim. No reliable public file size/extension rule was found, and current instructions still request originals for some routes.

## Tata AIG

Official sources:

- [Claims FAQ/process](https://www.tataaig.com/claims-process)
- [Current all-MediCare claim form](https://www.tataaig.com/s3/all_medicare_c73ac3dea5.pdf)
- [Pre/post guide](https://www.tataaig.com/knowledge-center/health-insurance/pre-post-hospitalisation-expense-under-medicare-select)
- [Reimbursement guide](https://www.tataaig.com/health-insurance/types-of-health-insurance-claims)

The form asks for original financial documents and separate claim handling for some pre/post routes, particularly after cashless hospitalization. No current general health upload-size/extension limit was found. Do not reuse old email limits from special claim programs.

## Aditya Birla Health Insurance

Official sources:

- [Reimbursement checklist](https://www.adityabirlacapital.com/healthinsurance/assets/pdf/checklist-reimbursement-claim.pdf)
- [Reimbursement process/document matrix](https://www.adityabirlacapital.com/healthinsurance/reimbursement-claims)
- [Dedicated pre/post page](https://www.adityabirlacapital.com/healthinsurance/pre-post-claim-details)
- [Digital reimbursement form](https://www.adityabirlacapital.com/healthinsurance/claim/reimbursement-claim-form)

The current matrix distinguishes online from offline claim-form requirements. The pre/post page requires direct linkage to the hospitalization and matching prescription, report, bill, and receipt. The current initial digital screen accepts PDF/PNG/JPG/JPEG up to 10 MB and requires PDFs to be at least 10 KB; its duplicated image-minimum text conflicts, its query route can be PDF-only, and another official view says under 5 MB. Target less than 5 MB when practical, but record the exact authenticated screen. Exact windows and deadlines vary by product.

## ManipalCigna

Official sources:

- [Claims page and current checklist](https://www.manipalcigna.com/claims/)
- [Current ProHealth Claim Form A snapshot](https://www.manipalcigna.com/documents/20124/0/ProHealth-V8-ClaimForm-A/f25fb47c-fa04-80e3-926f-74922d65aee8)
- [Hospitalization/pre-post guide](https://www.manipalcigna.com/hospitalization-cover)

Official guidance asks for the signed claim form, discharge, main/breakup bills, payment receipt, consultation/referral, prescriptions, reports, pharmacy bills, and bank proof, with originals/certified-copy rules varying by product. No public claim-upload size/extension limit was found.

## IndusInd General Insurance

Former name: Reliance General Insurance.

Official sources:

- [Mandatory health claim documents](https://www.indusindinsurance.com/Insurance/Claims/Health-Claims-Documents.aspx/1000)
- [Health claim/intimation flow](https://www.indusindinsurance.com/insurance/self-help/intimate-claim-health-flow.aspx)
- [Health Claim Form A snapshot](https://www.reliancegeneral.co.in/Downloads/Health_%28TPA%29_Claim_FormA.pdf)

The public health flow states a 5 MB per-file limit. The insurer may process scans but can request physical originals; retain them for the period stated by the current claim route. Some older upload-slot wording conflicts with the general mandatory checklist, so default to the signed form unless the authenticated route says otherwise.

## SBI General

Official sources:

- [Claims and forms download page](https://www.sbigeneral.in/claim/claims-form-download)
- [Claim portal](https://www.sbigeneral.in/webportal/claim/claims-status-and-intimation)
- [Standard health claim form/checklist](https://content.sbigeneral.in/uploads/6f05fdb469be41e9a69c9f861deb8a65.pdf)

The standard form covers main/breakup bill, hospital payment receipt, discharge, pharmacy, operation notes, investigation requests/reports, prescriptions, and bank proof. Product wordings vary on originals/certified copies and KYC. No public general health claim file-size/extension rule was found; some routes still direct physical originals.

## New India Assurance

Official sources:

- [Current New India Mediclaim prospectus](https://www.newindia.co.in/assets/docs/know-more/health/new-india-mediclaim-policy/Prospectus%20New%20India%20Mediclaim%20Policy.pdf)
- [Arogya Sanjeevani policy wording](https://www.newindia.co.in/assets/docs/know-more/health/arogya-sanjeevani/POLICY%20CLAUSES%20AJ-MASTERWef%2001102024.pdf)

Current product documents require original claim forms, consultation/history, numbered hospital bills and receipts, discharge, pharmacy cash memos with prescriptions, investigations with doctor advice, professional-fee evidence, and conditional surgery/implant/accident/bank/KYC papers. Filing deadlines differ materially between New India products. Certified copies plus another insurer's settlement advice may be accepted when that insurer holds originals. No common public PDF upload specification was found.

## United India Insurance

Official sources:

- [Individual Health Insurance product page](https://uiic.co.in/web/product/health/Individual-Health-Insurance-Policy)
- [Current Individual Health prospectus snapshot](https://www.uiic.co.in/web/sites/default/files/Policy-Document/20250708%20-%20Prospectus%20-%20IHIP.pdf)
- [Download/forms center](https://uiic.co.in/web/hi/downloadforms/downloads)

Current guidance asks for originals in the insured patient's name: completed form, diagnosis/admission/test advice, medical history, itemized bills and receipts, discharge, pharmacy/diagnostic records, professional-fee receipts, and implant evidence when applicable. Certified copies may be accepted with another insurer's settlement advice. Electronic collection by the insurer/TPA does not itself waive the stated original-document requirement. No common public claim-upload size/extension rule was found.

## Oriental Insurance

Official sources:

- [Reimbursement process PDF](https://oicl-cms-media.s3.ap-south-1.amazonaws.com/Procedures_to_be_followed_by_the_policyholder_for_claim_settlement_under_178526dd5d.pdf)
- [Oriental Mediclaim Individual prospectus](https://oicl-cms-media.s3.ap-south-1.amazonaws.com/2_Oriental_Mediclaim_Insurance_Policy_Individual_PROSPECTUS_8f07299075.pdf)
- [Claim form/e-claim page](https://csc.orientalinsurance.org.in/download-claim-form)

Oriental's process asks for attested originals covering the hospital bill/receipts, discharge, illness records from first detection, medical history, prescription-backed pharmacy and diagnostic records, reports/films, and professional-fee certificates/receipts. Accident, death, disability, organ-donation, and prior-policy records are conditional. An e-claim route is not proof that originals are waived. No public universal PDF limit was found.

## National Insurance

Official sources:

- [National Mediclaim product page](https://nationalinsurance.nic.co.in/products/all-products/health/national-mediclaim-policy-individual-plan)
- [Current National Mediclaim prospectus](https://nationalinsurance.nic.co.in/sites/default/files/2026-04/NMP%20Prospectus.pdf)
- [Current claim form](https://nationalinsurance.nic.co.in/sites/default/files/2026-04/NMP%20Claim%20Form.pdf)
- [Online claim registration](https://nicportal.nic.co.in/nicportal/claimlogin)

The current prospectus/form list admission prescription, hospital/pharmacy cash memos with prescriptions, receipts, investigation reports and physical media, diagnosis/surgeon records, implant invoice/receipt/sticker, history, discharge, and detailed final bill. The claim form separately inventories main, pre, post, pharmacy, and other bills, matching this skill's ledger. Public deadline summaries can conflict with the active prospectus; use the earliest visible date until the issued policy/CIS is checked. No common public PDF upload standard was found.

## ACKO General

Official sources:

- [Current downloads and product documents](https://www.acko.com/download/)
- [Health reimbursement checklist](https://www.acko.com/health-insurance/reimbursement/)
- [Current ACKO Health III wording snapshot](https://acko-cms.ackoassets.com/Policy_Wordings_ACKO_Health_III_de395d1997.pdf)

The current wording requires the exact schedule-defined pre/post period and an admissible related hospitalization/day-care claim. Its chain covers discharge, itemized hospital bill and receipts, prescription-backed diagnostics with report/invoice/receipt, pharmacy records, consultation/admission history, and applicable implant/accident/bank/KYC papers. Generic and product pages conflict on filing dates; use the exact UIN. Corporate instructions to write on scans are route-specific and must not be applied to retail originals. No public insurer-wide extension/size limit was found.

## Go Digit General

Official sources:

- [Health claim route](https://www.godigit.com/health-insurance/file-a-claim)
- [Health claim FAQ/checklist](https://www.godigit.com/health-insurance/frequently-asked-questions)
- [App upload guide](https://www.godigit.com/health-insurance/file-health-claims-on-digit-app)
- [Current standard health claim form](https://www.godigit.com/content/dam/godigit/directportal/en/downloads/health/claim-form-for-health-insurance-policies.pdf)

Digit supports paperless photo/PDF uploads and lists discharge, medical bills, consultation/lab/supporting papers, KYC, and bank proof. A current FAQ lists JPG/JPEG/PDF, but no numeric health-claim limit was found. Its live page also shows a hard-copy exception for a named group-policy route, so the generic paperless statement is not universal. Generic and product-specific deadlines conflict; never carry one website deadline or window across products, and do not reuse unrelated DigiLocker limits.

## Cholamandalam MS General

Official sources:

- [Arogya Sanjeevani product/claim route](https://uportal.cholainsurance.com/in/health-insurance/arogya-sanjeevani)
- [Official product document showing detailed evidence](https://uportal.cholainsurance.com/documents/20121/o/Chola%20Surrogate%20and%20Oocyte%20Donor%20Protector%20-%20CHOHLIP24093V012324%20%28Prospectus%29.pdf/203e4115-ab02-2272-0a26-721c4417bc23)

Current product material supports original discharge, itemized main bill, numbered payment receipt, prescribed investigations/reports, prescription-backed pharmacy bills, and conditional implant/accident papers. The public Arogya page's periods and deadline are product-specific, not a general Chola rule. No reliable generic upload format/size limit was found.

## Generali Central Insurance

Former name: Future Generali India Insurance.

Official sources:

- [Official rebrand FAQ](https://www.generalicentralinsurance.com/about-us/new-brand-faqs)
- [Health reimbursement process and checklist](https://www.generalicentralinsurance.com/health-insurance/health-claim-process)
- [Online health claim form](https://www.generalicentralinsurance.com/health-insurance/health-claim-process/health-claim-form)

The current checklist explicitly pairs medicines with prescription + chemist bill, consultations with prescription + doctor bill + receipt, and tests with prescription + report + diagnostic bill + receipt, alongside signed form, bank proof, health card, original discharge, itemized bill, paid receipt, and conditional records. The online form accepts PDF/JPG/JPEG/DOC/DOCS/XLS/XLSX with a 5 MB total upload. Route rules differ for corporate and individual claims; users declare originals retained for one year.

## IFFCO Tokio General

Official sources:

- [Health claims and reimbursement checklist](https://www.iffcotokio.co.in/health-insurance/claims)
- [Current Essential Health Protector wording snapshot](https://www.iffcotokio.co.in/content/dam/iffcotokio/iffco-pdf/wordings_EHP.pdf)
- [QCS app description](https://www.iffcotokio.co.in/about-us/customer-app)

The normal route requests originals covering claim form/doctor certificate, discharge, bills, prescriptions, advance/final receipts, and diagnostic records. Product windows and exceptions vary. QCS is a special full-and-final photo route for claims below its published threshold and does not allow pre/post or supplementary benefits; do not choose it when later expenses will be claimed. No normal health-portal size/extension limit was found.

## Zurich Kotak General

Former name: Kotak Mahindra General Insurance.

Official sources:

- [Current health claim route](https://one.zurichkotak.com/services/claims/health-insurance-claim)
- [Health checklist](https://www.zurichkotak.com/health-insurance)
- [Current Part A health claim form](https://cms.zurichkotak.com/uploads/Health_Insurance_Part_A_Claim_Form_ZK_26_27_v1_09042026_75fe95f01c.pdf)

The current flow emphasizes original claim documents: pharmacy bills, reports/prescriptions/hospital records, diagnostics, discharge, bills/payment receipts, identity, bank proof, and accident papers when applicable. The form separately records pre/post amounts. Exact periods and deadlines are product-specific; no reliable public health upload size/extension rule was found.

## Narayana Health Insurance

Official sources:

- [Reimbursement route and checklist](https://www.narayanahealth.insurance/reimbursement-claim)
- [Claims FAQ](https://www.narayanahealth.insurance/claims-faq)
- [Customer support, current forms, and wordings](https://www.narayanahealth.insurance/customer-support)
- [Current product/UIN list](https://www.narayanahealth.insurance/product)

Narayana asks for a signed/stamped form, identity/intimation, original discharge and itemized hospital bills/receipts, earlier consultation records, prescription-backed diagnostics with reports/bills/receipts, pharmacy bills with prescription, KYC, and bank proof, plus applicable implant/accident/death/indoor-case/legal-heir records. Public instructions route originals to the insurer and publish no claimant PDF format/size specification. Product and even network-specific pre/post windows vary materially; match the issued UIN and schedule.

## Galaxy Health Insurance

Official sources:

- [Reimbursement route and checklist](https://www.galaxyhealth.com/claims/reimbursement-claim)
- [Claims FAQ](https://www.galaxyhealth.com/claims/faq)
- [Current product/UIN list](https://www.galaxyhealth.com/our-product-list)

Galaxy lists a doctor-signed claim form, original hospital bills/receipts, discharge, pre/post treatment papers, reports and films, chemist/test/professional receipts, diagnosis certificate, KYC/PAN, and bank details. Its public "Scan/Upload" wording describes insurer-side handling after original submission, not a claimant PDF specification. Product windows differ substantially, and the public route does not clearly resolve later post-expense filing; keep portal rules unverified until the exact route confirms them.

## Liberty General Insurance

Official sources:

- [Health claims process and checklist](https://www.libertyinsurance.in/products/claims/health-claims)
- [Forms and current product documents](https://www.libertyinsurance.in/customer-support/download-forms.html)

Liberty requires original discharge, itemized hospital bill, paid receipt, prescriptions, prescription-backed investigations with reports/bills/receipts, medicine bills/receipts, and applicable professional/implant evidence. Its pre/post list explicitly uses medicine bill + receipt + prescription; investigation bill + receipt + prescription + report; and consultation bill + receipt + prescription, tied to the main discharge summary. General and current product deadlines conflict; exact UIN controls. No public health upload size/format rule was found.

## Royal Sundaram General Insurance

Official sources:

- [Health claims page](https://www.royalsundaram.in/claims/health-insurance-claims)
- [Forms and product/UIN register](https://www.royalsundaram.in/forms-central-download)

The common packet includes signed form, discharge, original itemized bill and paid receipt, reports, prescription-backed pharmacy bills, bank/KYC, treatment history, and conditional implant/accident papers. Coverage windows can differ by plan, variant, and add-on, and current marketing can conflict with wording. Use the issued schedule. No public health upload size/extension rule was found.

## Universal Sompo General Insurance

Official sources:

- [Claims process, forms, and original-document checklist](https://www.universalsompo.com/claims/claims-forms/)
- [Authenticated health claim status/upload entry](https://www.universalsompo.com/health-claim-status/)

Universal Sompo lists a signed form, first-symptom/treatment papers, original discharge, investigations, hospital bills/receipts, and prescription-backed chemist/doctor/investigation bills in the patient's name. Certified copies plus another insurer's settlement advice may be accepted when that insurer holds originals. Product extensions materially change pre/post periods. No public upload size/extension specification was found.

## Zuno General Insurance

Official sources:

- [Health claim process](https://www.hizuno.com/health-insurance/health-claim)
- [Current downloads catalog](https://www.hizuno.com/downloads)

Zuno's current route asks for a covering letter with contact details and a schedule of expenses, then explicitly pairs medicine bill + receipt + prescription; investigation bill + receipt + prescription + report; and consultation bill + receipt + prescription, plus the main discharge summary. Plan-level windows vary materially. Use the UIN printed inside the wording rather than inferring a version from the filename. No public health attachment-size/format limit was found.

## Navi General Insurance

Official sources:

- [Current Navi Health page](https://navi.com/insurance/health)
- [Official insurance FAQ](https://navi.com/insurance/faq)

Navi uses an app route and asks for signed claim form, original medical records, main/breakup bills and receipts, discharge/death summary, doctor referrals for investigations/pharmacy, original pharmacy bills, KYC, and bank proof. Public product windows and deadlines are specific to the current Navi Health generation. No public app file-size, extension, or resolution rule was found.

## Raheja QBE General Insurance

Official sources:

- [Live health claims page](https://rahejaqbe.com/claims/health-claims)
- [Current product/UIN register](https://www.rahejaqbe.com/compliance)

Raheja QBE requires originals covering signed form, hospitalization referral, consultation papers, prescriptions, itemized hospital/pharmacy bills and receipts, reports, discharge/indoor papers, and applicable implant/accident records. A live-page 30-day statement conflicts with current product wording using 15 days; use the earlier date until the exact insurer/TPA route confirms. Windows vary by product, plan, and sum insured. No insurer-wide PDF limit was found.

## Shriram General Insurance

Official sources:

- [Claims portal](https://www.shriramgi.com/claims)
- [Current reimbursement form](https://cdn.shriramgi.com/webassets/download/claim/47bafbd9-69a3-4ae8-8189-52d608574341_REIMBURSEMENT%20CLAIM%20FORM%20-%20INDEMNITY%20PRODUCTS%20%20%281%29.pdf)
- [Current Shri Health Suraksha wording snapshot](https://cdn.shriramgi.com/webassets/download_products/3f95122c-98df-4f84-b055-6d293dda12d1_Policy-Wording-Shri-Health-Suraksha-Insurance-Policy-Updated.pdf)

Current product material requests originals including claim form, admission prescription, itemized bill, receipt, discharge/history, prescription-backed investigations, and conditional surgery/implant/accident evidence. Base and add-on windows differ. No reliable public health upload limit was found; do not reuse limits from unrelated Shriram uploaders.

## Magma General Insurance

Former name: Magma HDI General Insurance.

Official sources:

- [Current claim process](https://www.magmainsurance.com/claim-process)
- [Downloads and product documents](https://www.magmainsurance.com/web/magmainsurance/downloads)

Magma asks for first/prior consultations, prescriptions, discharge, original bills/cash memos/receipts, doctor-requested investigation reports, and prescription-backed pharmacy bills. OneHealth windows differ by plan and option; currently linked wording and related materials can show different UIN generations, so match the issued schedule before selecting rules. The public retail route requests physical originals and publishes no health upload size/extension rule.

## Kshema General Insurance

Route out of this skill for the current health products.

Official sources:

- [Current dated product list](https://kshema.co/policy-documents/product-list/2026/22July2026/product-list.pdf?_t=1784693781)
- [Hospi DinDhan Suraksha retail page](https://kshema.co/kshema-hospi-dindhan-suraksha/)
- [Claim intimation and document checklist](https://kshema.co/claim-intimation/)

Kshema's current health entries are personal-accident or scheduled daily hospital-cash benefits rather than reimbursement of actual hospitalization/pre/post expenses. They therefore do not fit this indemnity packet model. Its benefit-claim route still asks for a form, identity, self-attested discharge/final bill/payment and diagnostic records, KYC, and bank proof, but the correct product-specific fixed-benefit workflow and deadlines must be used. The authenticated app/web upload route publishes no public file-size or extension rule. Do not invent pre/post reimbursement windows.

## Regulator

- [IRDAI Health Department and FAQs](https://irdai.gov.in/health-dept)
- [IRDAI Master Circular on Health Insurance Business, 29 May 2024](https://irdai.gov.in/document-detail?documentId=4942918)
- [IRDAI Master Circular on Protection of Policyholders' Interests, 5 September 2024](https://irdai.gov.in/document-detail?documentId=5625747)

After claim intimation, the IRDAI health circular places responsibility on insurers/TPAs to collect required hospital-held records from the hospital. Do not misread this as permission to omit claimant-held pre/post prescriptions, pharmacy bills, reports, receipts, bank/KYC records, or other evidence requested for reimbursement.

The policyholder-protection circular gives a 15-day settlement turnaround for reimbursement claims after submission. That is not the claimant's filing deadline; product and claim-route deadlines still control. IRDAI guidance does not make one static PDF packet universally sufficient.

## Unlisted insurer or TPA

Use the common evidence model, but keep status `PORTAL_RULES_UNVERIFIED` until you obtain:

- current insurer and TPA identity;
- exact product/UIN wording and schedule;
- current claim form/checklist;
- main versus supplementary pre/post claim route;
- exact portal journey/screen plus accepted file types, per-file/total limits, categories, and upload count;
- original/certified-copy/physical-submission rules;
- current filing deadlines and covered pre/post periods.

Do not describe an unverified common bundle as insurer-approved.
