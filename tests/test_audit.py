import ast
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from bill_of_lading_extraction_claim_audit.audit import audit, module_evidence, claims
from bill_of_lading_extraction_claim_audit.__main__ import main
from bill_of_lading_extraction_claim_audit import phrases

EXPECTED_POS = ('bill of lading extraction', 'extract bills of lading', 'extracts bills of lading', 'extracting bills of lading', 'extract bill of lading', 'extracts bill of lading', 'extracting bill of lading', 'bill of lading parsing', 'bill of lading parser', 'parse bills of lading', 'parses bills of lading', 'parse bill of lading', 'parses bill of lading', 'bill of lading scanning', 'bill of lading scanner', 'scan bills of lading', 'scans bills of lading', 'scan bill of lading', 'scans bill of lading', 'bol extraction', 'extract bols', 'extracts bols', 'extracting bols', 'extract bol', 'extracts bol', 'extracting bol', 'bol parsing', 'bol parser', 'parse bols', 'parses bols', 'parse bol', 'parses bol', 'bol scanning', 'bol scanner', 'scan bols', 'scans bols', 'scan bol', 'scans bol', 'bill of lading data extraction', 'extract bill of lading data', 'bill of lading field extraction', 'extract bill of lading fields', 'bol data extraction', 'extract bol data', 'bol field extraction', 'extract bol fields', 'ocean bill of lading extraction', 'extract ocean bills of lading', 'house bill of lading extraction', 'extract house bills of lading')
EXPECTED_NEG = ('no bill of lading extraction', 'does not extract bills of lading', 'does not extract bill of lading', 'does not support bill of lading extraction', 'without bill of lading extraction', 'no bol extraction', 'does not extract bols', 'does not extract bol', 'does not support bol extraction', 'without bol extraction', 'no bill of lading parser', 'does not parse bills of lading', 'does not parse bill of lading', 'no bill of lading scanner', 'does not scan bills of lading', 'does not scan bill of lading', 'no bol parser', 'does not parse bols', 'does not parse bol', 'no bol scanner', 'does not scan bols', 'does not scan bol', 'no bill of lading data extraction', 'bill of lading extraction not supported')
EXPECTED_GENERIC = ('extract_bill_of_lading', 'extract_bills_of_lading', 'parse_bill_of_lading', 'parse_bills_of_lading', 'extract_bol', 'extract_bols', 'parse_bol', 'parse_bols', 'extract_bill_of_lading_data', 'parse_bill_of_lading_data', 'bill_of_lading_extraction', 'bill_of_lading_extractor', 'bill_of_lading_parser', 'bol_extraction', 'bol_extractor', 'bol_parser', 'extract_bill_of_lading_info', 'parse_bill_of_lading_info', 'bill_of_lading_scan', 'bill_of_lading_scanner', 'scan_bill_of_lading', 'scan_bills_of_lading', 'extract_bol_data', 'parse_bol_data')

class AuditTests(unittest.TestCase):
    def fixture(self, doc='extract bills of lading', files=None):
        temporary = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / 'README.md').write_text(doc)
        for name, source in (files or {}).items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(source)
        return root

    def cli(self, root, *options):
        with contextlib.redirect_stdout(io.StringIO()) as output, contextlib.redirect_stderr(io.StringIO()):
            code = main(['audit', str(root), *options])
        return code, output.getvalue()

    def test_phrase_oracle(self):
        tree = ast.parse(Path(phrases.__file__).read_text())
        parsed = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)}
        self.assertEqual(parsed['BILLOFLADINGEXTRACTION'], EXPECTED_POS)
        self.assertEqual(parsed['NOBILLOFLADINGEXTRACTION'], EXPECTED_NEG)
        self.assertEqual(parsed['GENERIC_NAMES'], EXPECTED_GENERIC)
        self.assertEqual((len(EXPECTED_POS), len(EXPECTED_NEG), len(set(EXPECTED_GENERIC))), (50, 24, 24))

    def test_good(self):
        self.assertEqual(self.cli(self.fixture(files={'app.py': 'x.extract_bill_of_lading()'}))[0], 0)

    def test_bad(self):
        code, output = self.cli(self.fixture(), '--json')
        self.assertEqual(code, 2)
        result = json.loads(output)
        self.assertEqual(result['verdict'], 'FAIL')
        self.assertEqual(result['findings'][0]['rule'], 'documented-bill-of-lading-extraction-claim-false')
        self.assertEqual(result['findings'][0]['severity'], 'HIGH')
        self.assertTrue(result['findings'][0]['message'])

    def test_test_only(self):
        root = self.fixture(files={'tests/demo.py': 'x.extract_bill_of_lading()'})
        self.assertEqual(self.cli(root)[0], 0)
        self.assertEqual(audit(root)['findings'][0]['severity'], 'MEDIUM')
        self.assertEqual(self.cli(root, '--fail-on', 'medium')[0], 2)

    def test_denial(self):
        root = self.fixture('does not extract bills of lading', {'app.py': 'x.extract_bill_of_lading()'})
        self.assertEqual(self.cli(root)[0], 2)
        self.assertEqual(audit(root)['findings'][0]['rule'], 'documented-no-bill-of-lading-extraction-claim-false')
        self.assertEqual(audit(root)['findings'][0]['severity'], 'HIGH')

    def test_no_claim_and_asymmetry(self):
        self.assertEqual(audit(self.fixture('neutral'))['verdict'], 'PASS')
        self.assertEqual(audit(self.fixture())['verdict'], 'FAIL')
        self.assertEqual(audit(self.fixture('no bill of lading extraction'))['verdict'], 'PASS')

    def test_fences_inline_normalization(self):
        for delimiter in ('```', '~~~', '   ````'):
            self.assertEqual(claims(delimiter + '\nextract bills of lading\n' + delimiter), ([], []))
        self.assertEqual(claims('`extract bills of lading`')[0], ['extract bills of lading'])
        self.assertEqual(claims("Doesn't extract bills of lading"), ([], ['does not extract bills of lading']))
        self.assertEqual(claims('BILL-OF-LADING-EXTRACTION')[0], ['bill of lading extraction'])
        self.assertEqual(claims('extract bills of ladinguffix'), ([], []))
        self.assertEqual(claims('extract\n\nbills of lading'), ([], []))

    def test_all_phrases(self):
        for phrase in EXPECTED_POS:
            self.assertTrue(claims(phrase)[0], phrase)
        for phrase in EXPECTED_NEG:
            self.assertEqual(claims(phrase), ([], [phrase]))

    def test_exclusions_and_ignore(self):
        for name in ('tests/app.py', 'test_app.py', 'app_test.py', 'fixtures/app.py', 'docs/app.py', 'examples/app.py'):
            result = audit(self.fixture(files={name: 'x.extract_bill_of_lading()'}))
            self.assertFalse(result['production_evidence'], name)
        root = self.fixture(files={'src/app.py': 'x.extract_bill_of_lading()'})
        self.assertEqual(self.cli(root, '--ignore', 'src')[0], 2)
        self.assertEqual(self.cli(root, '--ignore', 'sr')[0], 0)

    def test_docs_selection(self):
        root = self.fixture('neutral', {'nested/docs/a.md': 'extract bills of lading', 'other.md': 'no bill of lading extraction'})
        self.assertEqual(audit(root)['verdict'], 'FAIL')
        self.assertEqual(len(audit(root)['findings']), 1)

    def test_symlinks(self):
        root = self.fixture('neutral', {'outside/app.py': 'x.extract_bill_of_lading()'})
        (root / 'link.py').symlink_to(root / 'outside/app.py')
        (root / 'linked').symlink_to(root / 'outside', target_is_directory=True)
        self.assertFalse(audit(root, ['outside'])['production_evidence'])
        (root / 'docs').symlink_to(root / 'outside', target_is_directory=True)
        self.assertEqual(audit(root, ['outside'])['verdict'], 'PASS')

    def test_split_modules(self):
        pairs = [('import mindee\nc=mindee.Client()', 'x.parse(product.BillOfLadingV1)')]
        for a, b in pairs:
            self.assertEqual(audit(self.fixture(files={'a.py': a, 'b.py': b}))['verdict'], 'FAIL')

    def test_shadowing(self):
        cases = ['from sdk import extract_bill_of_lading\ndef extract_bill_of_lading(): pass\nextract_bill_of_lading()', 'class C:\n def extract_bill_of_lading(self): pass\nx.extract_bill_of_lading()', 'from sdk import extract_bill_of_lading as er\ner = other\ner()', 'from sdk import extract_bill_of_lading as er\ner: object = other\ner()', 'from sdk import extract_bill_of_lading as er\nwith ctx() as er:\n er()', 'from sdk import extract_bill_of_lading as er\nasync def f():\n async with ctx() as er:\n  er()', 'import mindee\ndef Client(): pass\nmindee.Client()\nx.parse(product.BillOfLadingV1)']
        for source in cases:
            self.assertFalse(module_evidence(source), source)

    def test_usage_and_io(self):
        for args in ([], ['wrong'], ['audit', '--fail-on', 'HIGH'], ['audit', '--ignore'], ['audit', '/nonexistent-r201']):
            with contextlib.redirect_stderr(io.StringIO()):
                try:
                    code = main(args)
                except SystemExit as error:
                    code = error.code
            self.assertEqual(code, 1)

    def test_version_and_module(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            with self.assertRaises(SystemExit) as raised:
                main(['--version'])
        self.assertEqual(raised.exception.code, 0)
        self.assertEqual(output.getvalue().strip(), '0.1.0')
        result = subprocess.run([sys.executable, '-m', 'bill_of_lading_extraction_claim_audit', '--version'], capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout.strip()), (0, '0.1.0'))


POSITIVE_CASES = ['import mindee\nc=mindee.Client()\nc.parse(product.BillOfLadingV1)', 'from mindee import Client\nfrom mindee.product import BillOfLadingV1\nClient()\nx.parse(BillOfLadingV1)', 'import mindee\nmindee.Client()\nx.parse(product=mindee.product.BillOfLadingV1)', 'from mindee import Client as C\nC()\nx.parse(mindee.v1.product.BillOfLadingV1)', 'x.extract_bill_of_lading()', 'from sdk import extract_bill_of_lading as f\nf()', 'x.extract_bills_of_lading()', 'from sdk import extract_bills_of_lading as f\nf()', 'x.parse_bill_of_lading()', 'from sdk import parse_bill_of_lading as f\nf()', 'x.parse_bills_of_lading()', 'from sdk import parse_bills_of_lading as f\nf()', 'x.extract_bol()', 'from sdk import extract_bol as f\nf()', 'x.extract_bols()', 'from sdk import extract_bols as f\nf()', 'x.parse_bol()', 'from sdk import parse_bol as f\nf()', 'x.parse_bols()', 'from sdk import parse_bols as f\nf()', 'x.extract_bill_of_lading_data()', 'from sdk import extract_bill_of_lading_data as f\nf()', 'x.parse_bill_of_lading_data()', 'from sdk import parse_bill_of_lading_data as f\nf()', 'x.bill_of_lading_extraction()', 'from sdk import bill_of_lading_extraction as f\nf()', 'x.bill_of_lading_extractor()', 'from sdk import bill_of_lading_extractor as f\nf()', 'x.bill_of_lading_parser()', 'from sdk import bill_of_lading_parser as f\nf()', 'x.bol_extraction()', 'from sdk import bol_extraction as f\nf()', 'x.bol_extractor()', 'from sdk import bol_extractor as f\nf()', 'x.bol_parser()', 'from sdk import bol_parser as f\nf()', 'x.extract_bill_of_lading_info()', 'from sdk import extract_bill_of_lading_info as f\nf()', 'x.parse_bill_of_lading_info()', 'from sdk import parse_bill_of_lading_info as f\nf()', 'x.bill_of_lading_scan()', 'from sdk import bill_of_lading_scan as f\nf()', 'x.bill_of_lading_scanner()', 'from sdk import bill_of_lading_scanner as f\nf()', 'x.scan_bill_of_lading()', 'from sdk import scan_bill_of_lading as f\nf()', 'x.scan_bills_of_lading()', 'from sdk import scan_bills_of_lading as f\nf()', 'x.extract_bol_data()', 'from sdk import extract_bol_data as f\nf()', 'x.parse_bol_data()', 'from sdk import parse_bol_data as f\nf()']

NEGATIVE_CASES = ['import mindee', 'import veryfi', 'import azure.ai.formrecognizer', 'import azure.ai.documentintelligence', 'import google.cloud.documentai', 'import boto3', 'import mindee\nmindee.Client()', 'import azure.ai.documentintelligence\nx.DocumentIntelligenceClient()', 'import veryfi\nveryfi.Client()', 'extract_bill_of_lading(f)', '"extract bills of lading"', '# extract bills of lading', 'x.extract_bill_of_lading', 'bad syntax !', 'text.parse("bill of lading")', 'import re\nre.search("shipper", text)\nre.findall("carrier",text)', 'import mindee\nmindee.Client()\nx.parse(product.InvoiceV4)', 'import mindee\nmindee.Client()\nx.parse(product.ReceiptV5)', 'import mindee\nmindee.Client()\nx.parse(product.PassportV1)', 'import mindee\nmindee.Client()\nx.parse(product.FinancialDocumentV1)', 'import mindee\nmindee.Client()\nx.parse(product.BankCheckV1)', 'import mindee\nmindee.Client()\nx.parse(product.BankAccountDetailsV2)', 'import mindee\nmindee.Client()\nx.parse(product.PayslipV2)', 'import mindee\nmindee.Client()\nx.parse(product.PayslipV3)', 'import mindee\nmindee.Client()\nx.parse(product.HealthcareCardV1)', 'import mindee\nmindee.Client()\nx.parse(product.BusinessCardV1)', 'import mindee\nmindee.Client()\nx.parse(product.CustomV1)', 'import mindee\nmindee.Client()\nx.parse(product.GeneratedV1)', 'import mindee\nmindee.Client()\nx.parse(product.DeliveryNoteV1)', 'import mindee\nmindee.Client()\nx.parse(product.ResumeV1)', 'import mindee\nmindee.Client()\nx.parse(product.Other)', 'import mindee\nmindee.Client()\nx.parse(product.TypeBillOfLadingV1)', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-invoice")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-receipt")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-layout")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-read")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-idDocument")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-check.us")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-tax.us")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-bankStatement.us")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-payStub.us")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-healthInsuranceCard.us")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-businessCard")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-creditCard")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-contract")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-mortgage.us.1003")', 'import azure.ai.documentintelligence\nx.begin_analyze_document("prebuilt-billOfLading")', 'import veryfi\nveryfi.Client()\nx.process_any_document()', 'import veryfi\nveryfi.Client()\nx.process_any_document_url()', 'import veryfi\nveryfi.Client()\nx.process_document()', 'import veryfi\nveryfi.Client()\nx.process_document_url()', 'import veryfi\nveryfi.Client()\nx.process_w2_document()', 'import veryfi\nveryfi.Client()\nx.process_w9_document()', 'import veryfi\nveryfi.Client()\nx.process_w8_document()', 'import veryfi\nveryfi.Client()\nx.process_check()', 'import veryfi\nveryfi.Client()\nx.process_check_url()', 'import veryfi\nveryfi.Client()\nx.process_check_with_remittance()', 'import veryfi\nveryfi.Client()\nx.process_check_with_remittance_url()', 'import veryfi\nveryfi.Client()\nx.process_bank_statement_document()', 'import veryfi\nveryfi.Client()\nx.process_bank_statement_document_url()', 'import veryfi\nveryfi.Client()\nx.process_bussines_card_document()', 'import veryfi\nveryfi.Client()\nx.process_bussines_card_document_url()', 'import veryfi\nveryfi.Client()\nx.classify_document()', 'import veryfi\nveryfi.Client()\nx.get_business_cards()', 'import veryfi\nveryfi.Client()\nx.get_business_card()', 'import veryfi\nveryfi.Client()\nx.delete_business_card()', 'import veryfi\nveryfi.Client()\nx.process_bill_of_lading_document()', 'import veryfi\nveryfi.Client()\nx.process_bill_of_lading_document_url()', 'x.process_document()', 'x.batch_process_documents()', 'x.analyze_document()', 'x.analyze_expense()', 'x.start_document_analysis()', 'x.get_expense_analysis()', 'x.extract_text()', 'x.image_to_string()', 'x.read_csv()', 'x.read_excel()', 'x.read_pdf()', 'x.convert_into()', 'x.extract_table()', 'x.extract_tables()', 'x.find_table()', 'x.find_tables()', "post('https://api.veryfi.com/api/v8/partner/documents')", "post('https://app.nanonets.com/api/v2/OCR/Model/opaque/LabelFile/')", "post('https://app.docsumo.com/api/v1/eevee/apikey/upload/')", "post('https://api.cargoai.co/solutions/ai/awb')", 'post("https://api.edenai.run/v3/universal-ai",json={"model":"ocr/invoice_parser/affinda"})', 'post("https://api.edenai.run/v3/universal-ai",json={"model":"ocr/resume_parser/affinda"})', 'post("https://api.edenai.run/v3/universal-ai",json={"model":"ocr/bill_of_lading/affinda"})', 'import mindee\nx.extract(model_id="opaque")', 'import subprocess\nsubprocess.run(["mindee","bol.pdf"])', 'import subprocess\nsubprocess.run(["veryfi","bol.pdf"])', 'from sdk import extract_bill_of_lading\ndef extract_bill_of_lading(): pass\nextract_bill_of_lading()', 'from sdk import extract_bills_of_lading\ndef extract_bills_of_lading(): pass\nextract_bills_of_lading()', 'from sdk import parse_bill_of_lading\ndef parse_bill_of_lading(): pass\nparse_bill_of_lading()', 'from sdk import parse_bills_of_lading\ndef parse_bills_of_lading(): pass\nparse_bills_of_lading()', 'from sdk import extract_bol\ndef extract_bol(): pass\nextract_bol()', 'from sdk import extract_bols\ndef extract_bols(): pass\nextract_bols()', 'from sdk import parse_bol\ndef parse_bol(): pass\nparse_bol()', 'from sdk import parse_bols\ndef parse_bols(): pass\nparse_bols()', 'from sdk import extract_bill_of_lading_data\ndef extract_bill_of_lading_data(): pass\nextract_bill_of_lading_data()', 'from sdk import parse_bill_of_lading_data\ndef parse_bill_of_lading_data(): pass\nparse_bill_of_lading_data()', 'from sdk import bill_of_lading_extraction\ndef bill_of_lading_extraction(): pass\nbill_of_lading_extraction()', 'from sdk import bill_of_lading_extractor\ndef bill_of_lading_extractor(): pass\nbill_of_lading_extractor()', 'from sdk import bill_of_lading_parser\ndef bill_of_lading_parser(): pass\nbill_of_lading_parser()', 'from sdk import bol_extraction\ndef bol_extraction(): pass\nbol_extraction()', 'from sdk import bol_extractor\ndef bol_extractor(): pass\nbol_extractor()', 'from sdk import bol_parser\ndef bol_parser(): pass\nbol_parser()', 'from sdk import extract_bill_of_lading_info\ndef extract_bill_of_lading_info(): pass\nextract_bill_of_lading_info()', 'from sdk import parse_bill_of_lading_info\ndef parse_bill_of_lading_info(): pass\nparse_bill_of_lading_info()', 'from sdk import bill_of_lading_scan\ndef bill_of_lading_scan(): pass\nbill_of_lading_scan()', 'from sdk import bill_of_lading_scanner\ndef bill_of_lading_scanner(): pass\nbill_of_lading_scanner()', 'from sdk import scan_bill_of_lading\ndef scan_bill_of_lading(): pass\nscan_bill_of_lading()', 'from sdk import scan_bills_of_lading\ndef scan_bills_of_lading(): pass\nscan_bills_of_lading()', 'from sdk import extract_bol_data\ndef extract_bol_data(): pass\nextract_bol_data()', 'from sdk import parse_bol_data\ndef parse_bol_data(): pass\nparse_bol_data()']

NEGATIVE_CASES += [name + '()' for name in EXPECTED_GENERIC]

def evidence_test(source, expected):
    def test(self):
        self.assertEqual(bool(module_evidence(source)), expected, source)
        result = audit(self.fixture(files={'app.py': source}))
        self.assertEqual(result['verdict'], 'PASS' if expected else 'FAIL')
    return test


for index, source in enumerate(POSITIVE_CASES):
    setattr(AuditTests, 'test_route_positive_%03d' % index, evidence_test(source, True))
for index, source in enumerate(NEGATIVE_CASES):
    setattr(AuditTests, 'test_route_negative_%03d' % index, evidence_test(source, False))

if __name__ == '__main__':
    unittest.main()
