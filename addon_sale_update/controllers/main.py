# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2022-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Midilaj (<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import requests,json

from odoo import http
from odoo.http import content_disposition, request, serialize_exception as _serialize_exception
from odoo.tools import html_escape


class XLSXReportController(http.Controller):

    @http.route('/web/binary/quations', type='http', auth="public")
    def print_report_quations_cnt(self, so_no, **kw):
        report_url = 'http://localhost:8080/jasperserver/rest_v2/reports/reports/JWT_quotation_sale.pdf?prm_so=%s' % (so_no)
        #report_url = 'http://localhost:8080/jasperserver/rest_v2/reports/reports/wht.pdf'
        headers = {'Authorization': 'Basic amFzcGVyYWRtaW46amFzcGVyYWRtaW4='}
        res = requests.get(report_url, headers=headers)

        filename = '%s .pdf' % (so_no)

        return request.make_response(res.content, [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', content_disposition(filename))
        ])


    ################  API CREATE CENSOR #############################
    @http.route('/create_censor', type="json", auth='public', methods=['POST'], csrf=False, website=True)
    def create_censor(self, **kwargs):
        data = http.request.params
        print("data value:", data)
        name = data['name']

        products = request.env['product.template'].sudo().search([('name', '=', name)])
        prod_id = products.id
        request.env['volte.censor'].sudo().create({
            'name': data['name'],
            'sensor': prod_id,
            'location': data['location'],
            'DATA01': data['DATA01'],
            'DATA02': data['DATA02'],
            'DATA03': data['DATA03'],
            # 'unit': data['unit'],
        })

        args = {
            'meaasge': 'success',
            'success': 'True',
            'data':
                {

                    'name': data['name']
                },
        }
        return args

    @http.route('/check_pin', type="json", auth='public', methods=['POST'], csrf=False)
    def check_pin01(self):
        data = http.request.params
        if not data['pin']:
            raise Exception("Parameter pin not found.")

        # get all teachers
        get_rec = request.env['hr.employee'].sudo().search([('pin', '=', data['pin'])],limit = 1, order="id desc")
        res_msg = []
        for rec in get_rec:
            res_msg.append({
                'id': rec.id,
               ## 'code': rec.emp_id,
                'message': 'found',

            })
        if not res_msg :
            res_msg.append({
                'id': 'NO',
                'code': 'NO',
                'message': 'NO',
            })
        return res_msg

    @http.route('/check_product', type="json", auth='public', methods=['POST'], csrf=False)
    def check_product(self):
        data = http.request.params

        location_id = int(data['location_id'])
        product_id = int(data['product_id'])
        if not data['location_id']:
            raise Exception("Parameter location not found.")

        # get all teachers
        get_rec = request.env['stock.quant'].sudo().search([('location_id', '=', location_id),('product_id', '=',  product_id )],limit = 1, order="id desc")
        res_msg = []
        for rec in get_rec:
            res_msg.append({
                'id': rec.id,
                'quantity': rec.quantity,
                'inventory_quantity': rec.inventory_quantity,
                'message': 'found',

            })
        if not res_msg :
            res_msg.append({
                'id': 'NO',
                'quantity': 'NO',
                'message': 'NO',
            })
        return res_msg


    @http.route('/web/binary/report_iotsumary', type='http', auth="public")
    def do_print_report01(self, **kw):
        report_url = 'http://localhost:8080/jasperserver/rest_v2/reports/report/report_iotsumary.pdf?'
        headers = {'Authorization': 'Basic amFzcGVyYWRtaW46amFzcGVyYWRtaW4='}
        res = requests.get(report_url, headers=headers)

        filename = 'report_iotsumary%s.pdf'

        return request.make_response(res.content, [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', content_disposition(filename))
        ])