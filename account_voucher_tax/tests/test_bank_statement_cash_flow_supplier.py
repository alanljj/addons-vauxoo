from openerp.addons.account_voucher_tax.tests.common import TestTaxCommon
import time


class TestCashFlowTaxSupplier(TestTaxCommon):

    def setUp(self):
        super(TestCashFlowTaxSupplier, self).setUp()

    def test_cf_iva_16_supplier(self):
        cr, uid = self.cr, self.uid

        # create advance
        move_line_ids = self.create_statement(
            cr, uid, None, self.partner_agrolait_id, -116,
            self.bank_journal_id, time.strftime('%Y')+'-06-01',
            self.account_payable_id)

        self.assertEquals(len(move_line_ids), 4)
        checked_line = 0

        for move_line in move_line_ids:
            if move_line.account_id.id == self.acc_provision_tax_16_supplier:
                self.assertEquals(move_line.debit, 0.0)
                self.assertEquals(move_line.credit, 16)
                self.assertEquals(move_line.amount_residual, 16)
                move_line_tax_rec_id = move_line
                checked_line += 1
                continue
            if move_line.account_id.id == self.acc_tax_16_payment:
                self.assertEquals(move_line.debit, 16)
                self.assertEquals(move_line.credit, 0.0)
                checked_line += 1
                continue
            if move_line.account_id.id == self.account_payable_id:
                move_line_rec_id = move_line
                checked_line += 1
                continue

        self.assertEquals(checked_line, 3)

        # create invoice
        invoice_id = self.account_invoice_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.invoice_supplier_journal_id,
            'reference_type': 'none',
            'name': 'invoice to supplier',
            'account_id': self.account_payable_id,
            'type': 'in_invoice',
            'date_invoice': time.strftime('%Y')+'-06-01',
            })
        self.account_invoice_line_model.create(cr, uid, {
            'product_id': self.product_id,
            'quantity': 1,
            'price_unit': 100,
            'invoice_line_tax_id': [(6, 0, [self.tax_16])],
            'invoice_id': invoice_id,
            'name': 'product that cost 100'})

        # validate invoice
        self.registry('account.invoice').signal_workflow(
            cr, uid, [invoice_id], 'invoice_open')
        invoice_record = self.account_invoice_model.browse(
            cr, uid, [invoice_id])

        for line_invoice in invoice_record.move_id.line_id:
            if line_invoice.account_id.id == self.account_payable_id:
                move_line_inv_id = line_invoice.id
                continue
            if line_invoice.account_id.id == self.acc_tax16:
                move_line_inv_tax_rec_id = line_invoice

        # create reconciliation with account voucher
        voucher_id = self.account_voucher_model.create(cr, uid, {
            'partner_id': self.partner_agrolait_id,
            'journal_id': self.journal_bank_special,
            'account_id': self.account_bnk_id,
            'date': time.strftime('%Y')+'-06-01',
            'type': 'purchase',
            'amount': 0
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'cr',
            'move_line_id': move_line_rec_id.id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_payable_id,
            'amount': 116
            })
        self.account_voucher_line_model.create(cr, uid, {
            'voucher_id': voucher_id,
            'type': 'dr',
            'move_line_id': move_line_inv_id,
            'partner_id': self.partner_agrolait_id,
            'account_id': self.account_payable_id,
            'amount': 116
            })

        self.account_voucher_model.proforma_voucher(cr, uid, voucher_id, {})

        self.assertEquals(
            len(self.account_voucher_model.browse(
                cr, uid, voucher_id).move_id.line_id), 5)
        checked_line = 0
        for voucher_line in self.account_voucher_model.browse(
                cr, uid, voucher_id).move_id.line_id:

            if voucher_line.account_id.id ==\
                    self.acc_provision_tax_16_supplier:
                self.assertEquals(voucher_line.debit, 16)
                self.assertEquals(voucher_line.credit, 0.0)
                self.assertEquals(voucher_line.amount_residual, 0.0)
                self.assertEquals(
                    voucher_line.reconcile_id.name,
                    move_line_tax_rec_id.reconcile_id.name)
                checked_line += 1
                continue
            if voucher_line.account_id.id == self.acc_tax16:
                self.assertEquals(voucher_line.debit, 0.0)
                self.assertEquals(voucher_line.credit, 16)
                self.assertEquals(voucher_line.amount_residual, 0.0)
                self.assertEquals(
                    voucher_line.reconcile_id.name,
                    move_line_inv_tax_rec_id.reconcile_id.name)
                checked_line += 1
                continue

        self.assertEquals(checked_line, 2)
