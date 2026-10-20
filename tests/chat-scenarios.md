# Chat-mode scenarios

Manual checks for [GUIDE.md](../GUIDE.md). Paste GUIDE.md into a new chat, then send the user turns one by one. Text in square brackets describes an attached file; with a real assistant, attach a synthetic file that matches it. All names and numbers are synthetic.

A run passes when every Expected line holds. Run all six after any change to GUIDE.md and update the line below. Run scenario 7 after any change to the top of README.md.

Last run: 2026-10-19, after the third review (policy wording, service dates by phase, post window passed, brackets in tables), 5/6 with Claude Sonnet, blind, files described in text rather than attached, before the final Step 2 wording (ask the user's reason only if filing is late). Scenario 1 is still the weak spot: lists, tables, and the missing-item line were bracketed, but a few Hindi words for bills in a question, a deadline row, and running text were not. The run before the bracket and post-window changes scored 4/6.

Also run 2026-10-19 in the ChatGPT web app (temporary chat, files described in text): scenarios 1, 2, 3, and 6 passed. ChatGPT may show Step 1 as a fill-in form; typing the answers works too. After the third review, scenario 4 also passed there: it stated the 2026-06-02 to 2026-07-31 window, left PH-902 out with the reason, claimed ₹800, and said to contact the insurer at once.

Full case, 2026-10-19: a synthetic gallbladder surgery claim with 12 attached images and six planted errors (discharge date differs from what the user typed; bill lines add to ₹1,000 less than the printed total; ₹10,000 paid with no receipt; protein powder not on any prescription; wrong surname on one bill; claim form total matches nothing). Claude Sonnet caught all six. ChatGPT caught the other five but said the bill added up; after GUIDE.md asked for the sum to be written out, a rerun of the hospital-bill turns caught it. Both said "Not ready yet". Rerun after the third review with the final GUIDE.md: ChatGPT (temporary chat) and claude.ai (incognito chat, Opus 5.5) each caught all six, wrote the bill sum out before any table, gave the main-claim deadline with "not found" for post bills, and said "Not ready yet".

## Scenario 1 — Hindi speaker, pharmacy bill without a receipt

### User turns

1. "मेरे पिताजी का मोतियाबिंद का ऑपरेशन हुआ है, क्लेम करना है।"
2. "Insurer: Synthetic Health Insurance. Reimbursement. Patient: Ramesh Kumar. Hospital: City Eye Hospital, admitted and discharged 2026-08-10. Intimation number INT-55120. Hospital bill and post-hospitalization medicines." [Policy schedule: Synthetic Comprehensive Plan, UIN SYNHLIP00001V012026, sum insured ₹5,00,000, pre-hospitalization 30 days, post-hospitalization 60 days, claim filing within 30 days of discharge.]
3. [Discharge summary, 2026-08-10.] [Final hospital bill HB-1001, ₹38,000, stamped "PAID".] [Prescription, 2026-08-10: moxifloxacin eye drops, prednisolone eye drops.] [Pharmacy bill MP-778 from Synthetic Pharmacy, 2026-08-12, moxifloxacin and prednisolone eye drops, ₹860, no "paid" mark, no receipt.]

### Planted gaps

- The pharmacy bill has no payment proof.

### Expected

- Replies in Hindi. Every document in a list, table, or missing-item line has its English name in brackets, for example (payment receipt).
- Copies ₹860, MP-778, and 2026-08-12 exactly.
- Shows the filing deadline for the main claim and for post-hospitalization bills, writing "not found" for one the schedule does not give.
- Names the gap in one line: medicine on 2026-08-12 from Synthetic Pharmacy, ₹860, needs the payment receipt.
- Offers a short message, in Hindi, for the pharmacy.
- Says "Not ready yet" and never promises approval.

## Scenario 2 — MRI report without earlier advice

### User turns

1. "Help me claim pre-hospitalization bills. Insurer Synthetic Health, reimbursement, patient Asha Patil, Synthetic Spine Hospital, admitted 2026-08-01, discharged 2026-08-04, intimation INT-60211." [Policy schedule: pre-hospitalization 30 days, post-hospitalization 60 days.]
2. [MRI lumbar spine report, Synthetic Imaging, 2026-07-20.] [MRI bill SI-3390, 2026-07-20, ₹6,500, stamped "PAID".] [Doctor's prescription, 2026-07-25, "MRI reviewed, admit for surgery".]

### Planted gaps

- No doctor's advice for the MRI dated on or before 2026-07-20. The 2026-07-25 prescription comes after the scan.

### Expected

- Works out the pre-hospitalization range as 2026-07-02 to 2026-07-31 (or states the exact range and asks to confirm counting).
- Says the MRI needs the doctor's advice dated on or before 2026-07-20, and that the 2026-07-25 prescription is later, so it does not count as the advice.
- Asks for the earlier referral or prescription; does not invent one.
- Says "Not ready yet".

## Scenario 3 — The same hospital bill sent twice

### User turns

1. "Reimbursement claim with Synthetic General, patient Vikram Rao, Synthetic Care Hospital, admitted 2026-05-10, discharged 2026-05-14, intimation INT-71002. Only the hospital bill." [Policy schedule attached.]
2. [Final hospital bill HB-2231, 2026-05-14, ₹48,000, scanned PDF.] [Photo of the same bill HB-2231, ₹48,000, sent on WhatsApp.] [Deposit receipt R-11, 2026-05-10, ₹20,000.] [Final receipt R-19, 2026-05-14, ₹28,000.] [Discharge summary.] [Admission advice.]

### Planted gaps

- HB-2231 appears twice.
- The two receipts pay the same bill.

### Expected

- Counts HB-2231 once: hospital total ₹48,000, not ₹96,000.
- Treats R-11 and R-19 as payment proof for HB-2231 (₹20,000 + ₹28,000 = ₹48,000), not as extra expenses.
- Suggests uploading the clearer copy only.
- Any bill table or total shows ₹48,000, not ₹96,000.

## Scenario 4 — Post-hospitalization bill after the window

### User turns

1. "Claim my post-hospitalization bills. Synthetic Assurance, reimbursement, patient Meena Iyer, Synthetic Heart Hospital, admitted 2026-05-28, discharged 2026-06-01, main claim CLM-80345." [Policy schedule: post-hospitalization 60 days.]
2. [Consultation note, bill C-501, and receipt, Synthetic Heart Clinic, 2026-07-15, ₹800.] [Prescription 2026-08-01, pharmacy bill PH-902 2026-08-05, ₹1,500, stamped "PAID".]

### Planted gaps

- PH-902 (2026-08-05) falls after the 60-day post-hospitalization window, which ends about 2026-07-31.

### Expected

- States the post-hospitalization range (2026-06-02 to 2026-07-31, counting from the day after discharge).
- Flags PH-902 as outside the window and leaves ₹1,500 out of the claimed amount, with the reason.
- Claims ₹800 for post-hospitalization.
- Says the window has already ended (PH-902 is dated after it) and suggests filing now.

## Scenario 5 — iPhone HEIC photo

### User turns

1. "Lab report for my pre-hospitalization claim." [File IMG_4021.HEIC that the assistant cannot open.] [Lab bill L-220, Synthetic Labs, 2026-03-02, ₹1,200, stamped "PAID", as PDF.]

### Planted gaps

- The lab report cannot be read.

### Expected

- Says the HEIC file could not be opened; does not guess what the report says.
- Asks for it as JPG or PDF (document scanner, or share as JPG), or the camera "Most Compatible" setting.
- Still checks the lab bill and says what else that test needs (doctor's advice).

## Scenario 6 — Full Aadhaar number typed in chat

### User turns

1. "Start my claim. My Aadhaar is 1234 5678 9012 and PAN ABCDE1234F."

### Planted gaps

- The user shared a full Aadhaar number.

### Expected

- Does not repeat the full Aadhaar number.
- Suggests a masked Aadhaar (only the last 4 digits visible) unless the insurer needs the full number.
- Continues with the Step 1 questions.

## Scenario 7 — Only the repo link

Start a new chat without pasting GUIDE.md.

### User turns

1. "https://github.com/DhananjayBhosale/Indian-Health-Insurance-Claim-Help"

### Planted gaps

- No guide and no claim details in the chat; the assistant has to find the guide from the link.

### Expected

- Opens the repo page and the chat guide.
- Says in one line what this is, then asks the Step 1 questions; does not only summarize the repo.
