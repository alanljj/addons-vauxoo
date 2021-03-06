# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
###############Credits######################################################
#    Coded by: vauxoo consultores (info@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
################################################################################


from openerp.osv import osv


class mail_notification(osv.Model):

    _inherit = 'mail.notification'

    def get_partners_to_notify(self, cr, uid, message, partners_to_notify=None, context=None):
        res = super(mail_notification,
                    self).get_partners_to_notify(cr, uid,
                                    message,
                                    partners_to_notify=partners_to_notify,
                                    context=context)
        if message.author_id and\
                (message.author_id.receive_my_emails and
                message.author_id.notification_email_send == "all"):
            res.append(message.author_id.id)
        return res
