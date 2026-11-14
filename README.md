# Documentation claim auditor

An offline static audit tool comparing documentation promises with recognized source calls. It never executes project code. Requires CPython 3.9 or newer and has no runtime dependencies.

## Installation and usage

```sh
python3 -m pip install .
bill-of-lading-extraction-claim-audit audit .
bill-of-lading-extraction-claim-audit audit . --json --verbose --ignore build --ignore dist --fail-on medium
python3 -m bill_of_lading_extraction_claim_audit audit .
bill-of-lading-extraction-claim-audit --version
```

The repository defaults to the current directory. Ignore prefixes are repeatable relative paths. Exit 0 means PASS at the threshold; 2 means findings at that threshold; 1 means usage or I/O error. The default threshold is high; medium also fails on test-only evidence. JSON reports verdict, findings with rule, severity, message and locations, and production and test evidence paths. Verbose text lists evidence paths.

## Matching rules

Root README.md and Markdown files with a docs path component are scanned. Fenced code blocks using backticks or tildes with up to three leading spaces are excluded; inline code counts. Paragraphs split on blank lines. Matching lowercases, expands contractions, replaces hyphens with spaces and collapses whitespace. Boundary matches prefer longest phrases with alphabetical ties. Denial spans are removed first. Each family produces at most one finding.

Source is parsed with AST. Symlinks are excluded. Files under fixtures, docs and examples supply no evidence; tests count separately. Invalid syntax supplies no evidence. Routes require a single module. Local function, method and class definitions shadow route names; assignment, annotated assignment and context manager bindings shadow imports. Generic attribute calls allow any base, while bare names require an imported recognized name. A positive promise without source fails; a denial without source passes.

## Reference data

```text
bill of lading extraction
extract bills of lading
extracts bills of lading
extracting bills of lading
extract bill of lading
extracts bill of lading
extracting bill of lading
bill of lading parsing
bill of lading parser
parse bills of lading
parses bills of lading
parse bill of lading
parses bill of lading
bill of lading scanning
bill of lading scanner
scan bills of lading
scans bills of lading
scan bill of lading
scans bill of lading
bol extraction
extract bols
extracts bols
extracting bols
extract bol
extracts bol
extracting bol
bol parsing
bol parser
parse bols
parses bols
parse bol
parses bol
bol scanning
bol scanner
scan bols
scans bols
scan bol
scans bol
bill of lading data extraction
extract bill of lading data
bill of lading field extraction
extract bill of lading fields
bol data extraction
extract bol data
bol field extraction
extract bol fields
ocean bill of lading extraction
extract ocean bills of lading
house bill of lading extraction
extract house bills of lading
no bill of lading extraction
does not extract bills of lading
does not extract bill of lading
does not support bill of lading extraction
without bill of lading extraction
no bol extraction
does not extract bols
does not extract bol
does not support bol extraction
without bol extraction
no bill of lading parser
does not parse bills of lading
does not parse bill of lading
no bill of lading scanner
does not scan bills of lading
does not scan bill of lading
no bol parser
does not parse bols
does not parse bol
no bol scanner
does not scan bols
does not scan bol
no bill of lading data extraction
bill of lading extraction not supported
extract_bill_of_lading
extract_bills_of_lading
parse_bill_of_lading
parse_bills_of_lading
extract_bol
extract_bols
parse_bol
parse_bols
extract_bill_of_lading_data
parse_bill_of_lading_data
bill_of_lading_extraction
bill_of_lading_extractor
bill_of_lading_parser
bol_extraction
bol_extractor
bol_parser
extract_bill_of_lading_info
parse_bill_of_lading_info
bill_of_lading_scan
bill_of_lading_scanner
scan_bill_of_lading
scan_bills_of_lading
extract_bol_data
parse_bol_data

documented-bill-of-lading-extraction-claim-false HIGH (MEDIUM for test-only evidence)
documented-no-bill-of-lading-extraction-claim-false HIGH

mindee Client construction + parse call passing BillOfLadingV1 (Name
exactly BillOfLadingV1, or Attribute with attr exactly BillOfLadingV1 such
as product.BillOfLadingV1 / mindee.product.BillOfLadingV1 /
mindee.v1.product.BillOfLadingV1) as any argument; import gate
mindee. BillOfLadingV1 exists in mindee 4.x only (4.22.0 wheel
inspected 2026-11-14); mindee 5.4.0 removed it (wheel inspected
2026-11-14: no bill_of_lading product directory; the only "lading"
hit in any .py file is OCR fixture text inside
tests/v2/product/ocr/test_ocr_response.py, not a product). The tool detects the
call in source, not the installed SDK version. A parse call passing any other product
(InvoiceV4, ReceiptV5, PassportV1, FinancialDocumentV1,
BankCheckV1, BankAccountDetailsV2, PayslipV2, PayslipV3,
HealthcareCardV1, BusinessCardV1, CustomV1, GeneratedV1,
DeliveryNoteV1, ResumeV1, or any other) is NOT evidence.

## veryfi names (implementation MUST match exactly)

NO veryfi route: veryfi has no bill of lading method in the Python SDK.
The 5.1.0 wheel, inspected 2026-11-14, contains zero hits for
"lading" across all .py files, so a veryfi call of ANY kind is
NOT evidence. A call to the non-existent
process_bill_of_lading_document / process_bill_of_lading_document_url counts as
nothing. A raw HTTP call to
"https://api.veryfi.com/api/v8/partner/documents" is NOT evidence
either: it is Veryfi's generic documents endpoint, shared by
receipts, invoices, and bills of lading alike.

## azure names (implementation MUST match exactly)

NO azure route: Azure Document Intelligence has no bill of lading model.
The Microsoft Learn v4.0 (GA) page, opened and searched
2026-11-14, contains zero hits for "bill of lading". A
begin_analyze_document call with ANY model id is NOT evidence.

## google document ai names (implementation MUST match exactly)

NO Google Document AI route: the Document AI processors list page,
opened and searched 2026-11-14, contains zero hits for
"Bill of Lading" — there is no bill of lading processor, so a
process_document call with ANY processor is NOT evidence.

## eden ai / nanonets / docsumo / other vendor names (implementation MUST match exactly)

NO Eden AI route: Eden AI documents no bill-of-lading parser
model, so a universal-ai call with ANY model id is NOT evidence.
NO Nanonets route: Nanonets bill of lading calls carry an opaque
model_id in the URL path (no fixed fingerprint — the model id is
user-configured, not a bill of lading product). NO Docsumo route:
Docsumo uploads go to a generic endpoint with the document type
configured in the dashboard, not in the call. NO ABBYY Vantage /
Rossum / Klippa / Parseur / Extend route: opaque skill / queue /
template / workflow IDs. NO CargoAI route: the AWB SCAN API
extracts air waybills, a different document from a bill of
lading. NO mindee v2 extraction API route: configurable model id,
no fixed fingerprint.


- The bare phrases "bill of lading extraction" / "extract bill of
  lading" / "extract bills of lading" are deliberately
  BILLOFLADINGEXTRACTION phrases: in document-tool docs they almost
  always name bill of lading extraction. But "bill of lading" can
  also name a bill of lading the tool merely stores, displays, or
  manages (a bill of lading archive, a bill of lading template
  library) without extracting fields from a bill of lading
  document: a doc that means storing, displaying, or templating
  bills of lading, not extracting fields from them, is a false
  positive; the tool flags the claim, only the code decides.
- "bill of lading parsing" / "bill of lading parser" are deliberately
  phrases: a doc can say "bill of lading parser" about a tool that
  only renders a bill of lading as formatted text, or a "bill of
  lading parser" that is really a keyword highlighter over plain
  text. The tool flags the claim; only the code decides.
- "bill of lading scanning" / "scan bill(s) of lading" are
  deliberately phrases: "scanning" a bill of lading can mean merely
  photographing it or OCRing it into raw text, with no structured
  field extraction. The tool flags the claim; only the code decides.
- "bol extraction" / "extract bol(s)" / "bol parsing" / "bol parser"
  are deliberately phrases: "BOL" is also an abbreviation in other
  domains (beginning of life in insurance, for example). A doc that
  means a different "BOL" is a false positive; the tool flags the
  claim, only the code decides.
- "ocean bill of lading extraction" / "house bill of lading
  extraction" are deliberately phrases: an ocean bill of lading and
  a house bill of lading are both bills of lading (master vs house),
  so both name the same extraction operation. A doc that merely
  mentions ocean or house bills of lading as document types it
  stores is a false positive; the tool flags the claim, only the
  code decides.
- "bill of lading data extraction" / "extract bill of lading data" /
  "bill of lading field extraction" are deliberately phrases: a doc
  can mean extracting plain text from a bill of lading, not
  structured fields. The tool flags the claim; only the code
  decides.
- A generic `extract_bill_of_lading(` / `parse_bill_of_lading(` /
  `extract_bol(` call can name a string parser for text the user
  typed in rather than a document extractor: the tool counts the
  call, the claim plus the code decide — and a subprocess call
  invoking an external CLI is NOT evidence by design, so a thin
  wrapper that only calls subprocess fails.
- Mindee `parse` with BillOfLadingV1 counts as evidence:
  BillOfLadingV1 exists in mindee 4.x (4.22.0 wheel inspected
  2026-11-14). The tool detects the call in source, not whether
  the call succeeds against a current API version.
- Mindee `parse` with BillOfLadingV1 is a 4.x-only fingerprint:
  mindee 5.4.0 removed the off-the-shelf bill of lading product
  (wheel inspected 2026-11-14 — no bill_of_lading product
  directory; the only "lading" hit is OCR fixture text in a test
  file). Code written against mindee 5.x cannot use this route.
 
- Mindee `parse` with InvoiceV4 / ReceiptV5 / PassportV1 /
  FinancialDocumentV1 / BankCheckV1 / BankAccountDetailsV2 /
  PayslipV2 / PayslipV3 / HealthcareCardV1 / BusinessCardV1 /
  CustomV1 / GeneratedV1 / DeliveryNoteV1 / ResumeV1 is NOT
  detected: those are other document types, and mindee 5.x has no
  bill of lading product at all.
- Mindee `parse` with DeliveryNoteV1 is NOT detected: a delivery
  note is a different document from a bill of lading. Say so in
  the README.
- Azure `begin_analyze_document` with ANY model id is NOT
  detected: Azure Document Intelligence has no bill of lading
  model (the Learn v4.0 GA page contains zero hits for "bill of
  lading", verified 2026-11-14).
- Veryfi calls of ANY kind are NOT detected: veryfi has no bill of
  lading method (5.1.0 wheel inspected 2026-11-14 — the word
  "lading" does not appear anywhere in the wheel), and its bill of
  lading API posts to the same generic documents endpoint as its
  receipt and invoice APIs.
- Google Document AI `process_document` / `batch_process_documents`
  with ANY processor is NOT detected: Document AI has no bill of
  lading processor (the processors list page contains zero hits
  for "Bill of Lading", verified 2026-11-14).
- Eden AI universal-ai calls with ANY model id are NOT detected:
  Eden AI documents no bill-of-lading parser model.
- Nanonets / Docsumo / ABBYY Vantage / Rossum / Klippa / Parseur /
  Extend calls are NOT detected: opaque model / skill / queue /
  template / workflow IDs, or a generic upload endpoint with the
  document type configured outside the call — no fixed fingerprint.
 
- CargoAI AWB SCAN API calls are NOT detected: that API extracts
  air waybills, a different document from a bill of lading. Say so
  in the README.
- Mindee v2 extraction API calls with a configurable model id are
  NOT detected: the model id is user-configured, not a fixed
  bill of lading product fingerprint.
- Textract `analyze_document` / `analyze_expense` /
  `start_document_analysis` / `get_expense_analysis` are NOT
  detected: generic document and expense analysis are not
  bill of lading extraction, and Textract has no bill of lading
  operation.
- A hand-rolled extraction from OCR text (`re.search` /
  `re.findall` on extracted text plus manual field assembly, no
  listed call) is NOT detected: the tool requires a listed call.
 
- The mindee CLI, the veryfi CLI, and any other external bill of
  lading tool invoked through subprocess are NOT detected:
  subprocess calls invoking an external CLI are NOT evidence by
  design.
- Azure Document Intelligence, Mindee, and Veryfi are cloud APIs:
  the tool detects the client call in source, not whether
  credentials are configured or the call succeeds.
- "extract bill of lading text" / "extract text from bill of
  lading" claims are NOT in the phrase lists: extracting plain text
  from a bill of lading is text extraction, not bill of lading
  field extraction.
- "bill of lading template" / "bill of lading form" claims are NOT
  in the phrase lists: templating or form-filling a bill of lading
  is creating one, not extracting fields from one.
- "bill of lading tracking" / "bill of lading status" claims are
  NOT in the phrase lists: tracking a shipment by its bill of
  lading number is downstream of extraction, not extraction
  itself.
- "air waybill extraction" / "air waybill parsing" claims are NOT
  in the phrase lists: an air waybill is a different document from
  a bill of lading.
- "delivery note extraction" / "packing list extraction" /
  "proof of delivery extraction" claims are NOT in the phrase
  lists: delivery notes, packing lists, and proofs of delivery are
  different documents from bills of lading.
- Invoice extraction claims ("extract invoices", "invoice
  extraction"), receipt extraction claims ("extract receipts",
  "receipt extraction"), ID document extraction claims ("extract
  passports", "passport extraction"), bank check extraction claims
  ("extract bank checks", "check extraction"), bank statement
  extraction claims ("extract bank statements", "statement
  extraction"), tax form extraction claims ("extract tax forms",
  "extract w2 forms", "1099 extraction"), pay stub extraction
  claims ("extract pay stubs", "payslip extraction"), health
  insurance card extraction claims ("extract health insurance
  cards", "health insurance card extraction"), business card
  extraction claims ("extract business cards", "business card
  extraction"), credit card extraction claims ("extract credit
  cards", "credit card extraction"), contract extraction claims
  ("extract contracts", "contract extraction"), mortgage
  extraction claims ("extract mortgages", "mortgage extraction"),
  and resume extraction claims ("extract resumes", "resume
  extraction") are NOT in the phrase lists: this family covers
  bills of lading only.
- As with every family: static pattern matching, not semantic
  judgement; dead code counts; alias chains the tracer cannot follow
  are missed; exact phrases only, not semantics; denial handling
  depends on the denial phrase list; each route must sit in a single
  module.

```

## Development

```sh
python3 -m unittest discover
python3 -m venv .venv
.venv/bin/python3 -m pip install build
.venv/bin/python3 -m build
```

Both distributions bundle the tests. Only the standard library is used at runtime. No project code is executed and no network calls are made.
