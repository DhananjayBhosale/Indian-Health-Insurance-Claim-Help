# PDF QA and submission gates

## Structural checks

For every built PDF:

- reopen it with an independent PDF reader;
- confirm it is not encrypted or password-protected;
- compare expected and actual page counts;
- verify source-page coverage, order, bookmarks, and page index;
- record byte size and SHA-256;
- confirm each file is below the verified portal limit with a safety margin;
- confirm filename, extension, category, and number of uploads match the live portal;
- confirm the recorded portal rule scope is the same journey being used now (initial, supplementary pre/post, query/additional documents, app, TPA, email, or physical route);
- keep digitally signed and interactive-form PDFs in `delivery_mode: standalone`; confirm the clean output hash exactly matches the source.

Do not auto-compress a file merely to pass a limit. Split on document boundaries or perform a deliberate quality-preserving compression pass followed by fresh visual QA.

## Visual checks

Render every page at a readable resolution. OCR/text extraction is not a visual check.

Inspect for:

- correct orientation and page order;
- complete corners, bill edges, stamps, signatures, barcodes, and handwritten notes;
- readable patient name, dates, invoice numbers, amounts, diagnosis/treatment linkage, and paid status;
- no clipping, overlap, black boxes, blank pages, corruption, excessive blur, glare, shadows, or tiny text;
- complete multi-page reports with headers/footers and continuity;
- no unrelated person, episode, invoice line, or duplicate page;
- generated cover/index confined to `REVIEW_ONLY`;
- clean `SUBMIT` pages unchanged apart from mechanical page assembly and safe image placement.

If a source is illegible, request a better scan or original digital copy. Do not upscale it and describe it as improved evidence.

## Reconciliation receipt before upload

Show the claimant:

- hospitalization, pre, post, and other subtotals;
- every invoice number/date/issuer/billed/requested amount;
- every excluded amount and reason;
- all missing or conditional records;
- upload filename, category, page count, byte size, and hash;
- whether originals/films must still be couriered or retained;
- any policy, UIN, deadline, coverage-window, or portal-rule uncertainty.

The CLI emits a pre-visual-QA status and intentionally keeps `VISUAL_QA_PENDING`. It never self-certifies a rendered page. After a human completes every visual check above, use only these final receipt labels:

- `READY`: all policy, evidence, structural, visual, and portal gates passed.
- `READY_WITH_WARNINGS`: no blocker, but the claimant accepts clearly stated non-material warnings.
- `NOT_READY`: evidence, amount, integrity, or PDF blocker remains.
- `PORTAL_RULES_UNVERIFIED`: the packet may be reviewable, but the live upload requirements are not confirmed.

`READY` is therefore a human, post-QA receipt decision; it is not an automatic builder status. Do not remove the pending warning merely to obtain that label.

Never say a packet "will be accepted."

## Submission boundary

Creating and reviewing files does not authorize an upload, declaration, or final submission. Pause for explicit claimant confirmation immediately before any external action.

Before upload, start a private receipt from [../assets/submission-receipt.template.md](../assets/submission-receipt.template.md) and complete its QA/approval section. After submission, finish the confirmation section. Record:

Hash the inventory-bearing `claim-audit.json`. After packet files exist, a later audit or refused rebuild is written as `claim-audit-attempt.json/.md` and must not replace the original PDF-bound inventory. Build a changed revision in a fresh output directory.

- insurer/TPA and claim reference;
- submission timestamp and channel;
- exact filenames/categories accepted by the portal;
- unique local upload count;
- portal-displayed document count;
- confirmation message/screenshot location;
- expected tracking availability and query channel;
- originals and query-response material retained.

Do not force the portal count to equal the local count. The insurer may generate its own claim document. Reconcile and explain the difference instead.
