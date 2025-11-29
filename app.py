from flask import Flask, render_template, request, redirect, url_for
import flask
import sqlalchemy as sa
from alembic import op



from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from  datetime import datetime
import pandas as pd
from datetime import date
from flask import make_response
import csv
import io
from datetime import datetime
from flask import jsonify
from flask_migrate import Migrate
#rom narwhals.dtypes import Datetime
from openpyxl.styles.builtins import total
from pandas.core.interchange.dataframe_protocol import Column
from pymongo import MongoClient
from flask_cors import CORS
from functools import wraps
from flask import abort


#from models import Material, FinishedProduct, Vendor, Invoice, InvoiceItem

import pytz
from sqlalchemy.orm import joinedload

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-very-secure-random-secret-key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)



from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Viewer')
    can_register = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # route name for login page

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#CREATING DATABASES
from sqlalchemy import DateTime, Column

class Material(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_code = db.Column(db.String(50), unique=True, nullable=False)
    material_name = db.Column(db.String(100), nullable=False)
    vendor = db.Column(db.String(100))
    item_category = db.Column(db.String(100))
    unit_of_measurement = db.Column(db.String(50))
    minimum_stock_level = db.Column(db.Integer)
    current_stock = db.Column(db.Integer)
    reorder_quantity = db.Column(db.Integer)
    purchase_history = db.Column(db.Text)
    #material_id = db.Column(db.Integer, db.ForeignKey('material.id', ondelete='CASCADE'), nullable=False)
    yellow_alert = db.Column(db.Integer, nullable=True)
    red_alert = db.Column(db.Integer, nullable=True)
    rate = db.Column(db.Float, default=0.0)
    location = db.Column(db.String(200))
    tax = db.Column(db.Float, default=0.0)
    rate2 = db.Column(db.Float, default=0.0)
    #added_on = db.Column(DateTime, default=datetime.utcnow)


class FinishedProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # product_code = db.Column(db.String(50), unique=True, nullable=False)
    # name = db.Column(db.String(100), nullable=False)
    # rate = db.Column(db.Float(50))
    # capacity = db.Column(db.Float(50))
    # configuration = db.Column(db.String(100))
    # model_name = db.Column(db.String(100))
    # dealer_zone = db.Column(db.String(100))
    # current_stock = db.Column(db.Integer)
    fg_in_date = db.Column(db.Date, nullable=False)
    grn_no = db.Column(db.String(100), nullable=False)
    item_code = db.Column(db.String(20), nullable=False)
    item_name = db.Column(db.String(100), nullable=False)
    sn_no = db.Column(db.String(100), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    battery_sn_number = db.Column(db.String(100), nullable=False)
    gps_number = db.Column(db.String(100))
    charger_number = db.Column(db.String(100))
    model_number = db.Column(db.String(100), nullable=False)
    gps_imei_no = db.Column(db.String(100))

class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_code = db.Column(db.String(50), unique=True, nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    contact = db.Column(db.String(100))
    address = db.Column(db.String(250))
    gstin = db.Column(db.String(20))
    material_type = db.Column(db.String(100))
    country = db.Column(db.String(100),nullable=False)
    state = db.Column(db.String(100),nullable=False)
    pin = db.Column(db.String(100),nullable=False)


class MaterialTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    transaction_type = db.Column(db.String(20),
                                 nullable=False)  # 'purchase', 'return', 'production', 'service', 'rnd', 'other'
    quantity = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    remarks = db.Column(db.String(200))

    material = db.relationship('Material', backref=db.backref('transactions', lazy=True))

class FinishedProductTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    finished_product_id = db.Column(db.Integer, db.ForeignKey('finished_product.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # e.g., 'add', 'update', 'in', 'out'
    quantity = db.Column(db.Integer)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    remarks = db.Column(db.String(200))

    #finished_product = db.relationship('FinishedProduct', backref=db.backref('transactions', lazy=True))

#invoice
class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(25), unique=True, nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_gstin = db.Column(db.String(20))
    customer_address = db.Column(db.String(200))
    customer_contact = db.Column(db.String(100))
    date = db.Column(db.Date, default=datetime.utcnow)
    subtotal = db.Column(db.Float, default=0.0)
    cgst = db.Column(db.Float, default=0.0)
    sgst = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    rate = db.Column(db.Float)
    gst_rate = db.Column(db.Float)
    cgst_rate  = db.Column(db.Float, nullable = True)
    sgst_rate = db.Column(db.Float, nullable = True)
    line_total = db.Column(db.Float)
    invoice = db.relationship('Invoice', backref=db.backref('items', lazy=True))

class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_number = db.Column(db.String(50), unique=True, nullable=False)
    grn_number = db.Column(db.String(50), unique=True, nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    items = db.relationship('PurchaseOrderItem', backref='purchase_order', lazy=True)

class PurchaseOrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    purchase_order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)

    #invoice_number = db.Column(db.String(50), nullable=False)
   # purchase_order_number = db.Column(db.String(50), unique=True, nullable=False)
    #date = db.Column(db.Date, default=datetime.utcnow)

    # Optional: Relationship to Material
    material = db.relationship('Material')

from datetime import datetime

class Requisition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requisition_no = db.Column(db.String(50), unique=True, nullable=False)
    order_no = db.Column(db.String(50))
    date = db.Column(db.Date, default=datetime.utcnow)
    department = db.Column(db.String(100))
    name = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    purpose = db.Column(db.String(200))
    remark = db.Column(db.String(200))
    status = db.Column(db.String(20)) # 'Accepted', 'Rejected', etc.
    issuer_remark = db.Column(db.String(200))

    items = db.relationship('RequisitionItem', backref='requisition', cascade="all, delete", lazy=True)

class RequisitionItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requisition_id = db.Column(db.Integer, db.ForeignKey('requisition.id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('material.id'), nullable=False)
    quantity = db.Column(db.Integer)
    material_code = db.Column(db.String(50))
    material_name = db.Column(db.String(100))
    unit_of_measurement = db.Column(db.String(50))
    current_stock = db.Column(db.Integer)
    vendor = db.Column(db.String(100))
    rate = db.Column(db.Float)


class CustomerInvoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_gstin = db.Column(db.String(20))
    customer_contact = db.Column(db.String(15))
    customer_address = db.Column(db.Text)
    subtotal = db.Column(db.Float, default=0.0)
    total_tax = db.Column(db.Float, default=0.0)
    grand_total = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('CustomerInvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')


class CustomerInvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('customer_invoice.id'), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    product_id = db.Column(db.String(50))  # m_1 or f_1 format
    quantity = db.Column(db.Float, nullable=False)
    rate = db.Column(db.Float, nullable=False)
    tax_rate = db.Column(db.Float, default=0.0)
    tax_amount = db.Column(db.Float, default=0.0)
    line_total = db.Column(db.Float, nullable=False)


def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in allowed_roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def generate_grn_number():
    last_po = PurchaseOrder.query.order_by(PurchaseOrder.id.desc()).first()
    if last_po and last_po.grn_number.startswith('GRN-'):
        last_num = int(last_po.grn_number.split('-')[1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"GRN-{new_num:05d}"

def generate_material_code():
    last_material = Material.query.order_by(Material.id.desc()).first()
    if last_material and last_material.material_code.startswith('ATPL-'):
        last_num = int(last_material.material_code.split('-')[1])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"ATPL-{new_num:04d}"

@app.route('/')
def splash():
    return render_template('intro.html')

from flask import flash

@app.route('/add_purchase_order', methods=['GET', 'POST'])
@login_required
@roles_required('super_access','store_access')
def add_purchase_order():
    materials = Material.query.all()
    purchase_orders = PurchaseOrder.query.order_by(PurchaseOrder.date.desc()).limit(10).all()
    # needed for GET and on error re-render

    if request.method == 'POST':
        try:
            po_number = request.form['purchase_order_number']
            invoice_number = request.form['invoice_number']
            grn_number = request.form['grn_number']
            date_str = request.form.get('date', datetime.today().strftime('%Y-%m-%d'))
            grn_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            material_ids = request.form.getlist('material_id')
            quantities = request.form.getlist('quantity')
            rates = request.form.getlist('rate')
            totals = request.form.getlist('total')

            if not all([po_number, invoice_number, grn_number]):
                raise ValueError("Missing required purchase order fields")

            new_po = PurchaseOrder(
                purchase_order_number=po_number,
                invoice_number=invoice_number,
                grn_number=grn_number,
                date=grn_date
            )
            db.session.add(new_po)
            db.session.flush()

            for mid, qty, rate, total in zip(material_ids, quantities, rates, totals):
                qty = int(qty)
                rate = float(rate)
                total = float(total)
                if qty > 0:
                    po_item = PurchaseOrderItem(
                        purchase_order_id=new_po.id,
                        product_id=int(mid),
                        quantity=qty,
                        rate=rate,
                        total=total
                    )
                    material = Material.query.get(int(mid))
                    material.current_stock += qty  # Update stock
                    db.session.add(po_item)

            db.session.commit()
            return jsonify({"success": True, "message": "Purchase order added successfully"})

        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "error": str(e)}), 400

    # For GET request render page with materials list
    generated_grn = generate_grn_number()
    today_date = datetime.today().strftime('%Y-%m-%d')
    return render_template('add_purchase_order.html', materials=materials, generated_grn=generated_grn, today_date=today_date, purchase_orders=purchase_orders)

@app.route('/recent_purchase_orders', methods=['GET'])
@login_required
@roles_required('super_access', 'store_access')
def recent_purchase_orders_page():
    # Use same query logic as add_purchase_order (you can change limit if you want more)
    purchase_orders = PurchaseOrder.query.order_by(PurchaseOrder.date.desc()).limit(50).all()
    return render_template('recent_purchase_orders.html', purchase_orders=purchase_orders)


@app.route('/modify_material/<int:material_id>', methods=['GET', 'POST'])
@login_required
@roles_required('super_access','store_access')
def modify_material(material_id):
    material = Material.query.get_or_404(material_id)
    if request.method == 'POST':
        old_data = {
            'material_name': material.material_name,
            'vendor': material.vendor,
            'item_category': material.item_category,
            'unit_of_measurement': material.unit_of_measurement,
            'minimum_stock_level': material.minimum_stock_level,
            'current_stock': material.current_stock,
            'reorder_quantity': material.reorder_quantity,
            'purchase_history': material.purchase_history,
            'yellow_alert': material.yellow_alert,
            'red_alert': material.red_alert
        }

        # Update fields
        material.material_name = request.form['material_name']
        material.vendor = request.form['vendor']
        material.item_category = request.form['item_category']
        material.unit_of_measurement = request.form['unit_of_measurement']
        material.minimum_stock_level = int(request.form['minimum_stock_level'])
        material.current_stock = int(request.form['current_stock'])
        material.reorder_quantity = int(request.form['reorder_quantity'])
        material.purchase_history = request.form['purchase_history']

        yellow_val = request.form.get('yellow_alert')
        red_val = request.form.get('red_alert')
        material.yellow_alert = int(yellow_val) if yellow_val and yellow_val.isdigit() else None
        material.red_alert = int(red_val) if red_val and red_val.isdigit() else None

        db.session.commit()

        # Create a transaction log for modification
        remarks = "Material details modified"
        # Optional: add changed field names
        changes = []
        for key, old_value in old_data.items():
            new_value = getattr(material, key)
            if old_value != new_value:
                changes.append(f"{key}: {old_value} → {new_value}")
        if changes:
            remarks += " [" + "; ".join(changes) + "]"

        transaction = MaterialTransaction(
            material_id=material.id,
            transaction_type='modify',
            quantity=0,  # Or you can use None if allowed
            transaction_date=datetime.today(),
            remarks=remarks
        )
        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for('show_materials'))

    return render_template('modify_material.html', material=material)

@app.route('/delete_material/<int:id>', methods=['POST'])
@login_required
@roles_required('super_access')
def delete_material(id):
    material = Material.query.get_or_404(id)
    try:
        MaterialTransaction.query.filter_by(material_id=material.id).delete()
        db.session.delete(material)
        db.session.commit()
        flash('Material deleted successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Failed to delete material.', 'danger')
    return redirect(url_for('show_materials'))

@app.route('/delete_finished_product/<int:id>', methods=['POST'])
@login_required
@roles_required('super_access')
def delete_finished_product(id):
    product = FinishedProduct.query.get_or_404(id)
    try:
        FinishedProductTransaction.query.filter_by(finished_product_id=product.id).delete()
        db.session.delete(product)
        db.session.commit()
        flash('Finished product deleted successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Failed to delete finished product.', 'danger')
    return redirect(url_for('show_finished_goods'))

@app.route('/delete_vendor/<int:id>', methods=['POST'])
@login_required
@roles_required('super_access')
def delete_vendor(id):
    vendor = Vendor.query.get_or_404(id)
    try:
        db.session.delete(vendor)
        db.session.commit()
        flash('Vendor deleted successfully.', 'success')
    except Exception:
        db.session.rollback()
        flash('Failed to delete vendor.', 'danger')
    return redirect(url_for('show_vendors'))


@app.route('/dashboard')
def dashboard():
    material_count = Material.query.count()
    finished_product_count = FinishedProduct.query.count()
    vendor_count = Vendor.query.count()
    invoice_count = Invoice.query.count()
    purchase_order_count = PurchaseOrder.query.count()
    recent_purchase_orders = PurchaseOrder.query.order_by(PurchaseOrder.date.desc()).limit(5).all()

    return render_template('dashboard.html',
                           material_count=material_count,
                           finished_product_count=finished_product_count,
                           vendor_count=vendor_count,
                           invoice_count=invoice_count,
                           purchase_order_count=purchase_order_count,
                           recent_purchase_orders=recent_purchase_orders,
                           username=current_user.username,
                           role=current_user.role)


#INVOICE GENERATION
from flask import request, render_template, redirect, url_for
from flask_login import login_required
# from yourapp import app, db  # Adjust as per your app structure
# from yourapp.models import Material, FinishedProduct, Invoice, InvoiceItem  # Adjust imports as needed
from datetime import datetime

@app.route('/generate_invoice', methods=['GET', 'POST'])
@login_required
@roles_required('super_access','manager_access')
def generate_invoice():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_gstin = request.form.get('customer_gstin', '')
        customer_address = request.form.get('customer_address', '')
        customer_contact = request.form.get('customer_contact', '')

        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        new_invoice = Invoice(
            invoice_number=invoice_number,
            customer_name=customer_name,
            customer_gstin=customer_gstin,
            customer_address=customer_address,
            customer_contact=customer_contact
        )
        db.session.add(new_invoice)
        db.session.flush()  # Get invoice ID

        product_names = request.form.getlist('product_name')
        quantities = request.form.getlist('quantity')
        tax_rates = request.form.getlist('tax_percent')

        subtotal = 0
        total_tax = 0

        for pname, qty_str, tax_str in zip(product_names, quantities, tax_rates):
            qty = int(qty_str)
            if qty <= 0:
                continue

            tax_rate = float(tax_str) if tax_str else 0.0

            # Product lookup by prefixed ID
            if pname.startswith('m_'):
                product_id = int(pname[2:])
                product = Material.query.get(product_id)
                rate = product.rate if product and product.rate else 0.0
                product_name = product.material_name if product else 'Unknown Material'
                if product:
                    product.current_stock = max(product.current_stock - qty, 0)
            elif pname.startswith('f_'):
                product_id = int(pname[2:])
                product = FinishedProduct.query.get(product_id)
                rate = 0.0  # Update if FinishedProduct has rate
                product_name = product.item_name if product else 'Unknown FinishedProduct'
            else:
                product = None
                product_name = pname
                rate = 0.0

            taxable = qty * rate
            tax_amount = taxable * tax_rate / 100
            line_total = taxable + tax_amount

            db.session.add(InvoiceItem(
                invoice_id=new_invoice.id,
                product_name=product_name,
                quantity=qty,
                rate=rate,
                gst_rate=tax_rate,
                cgst_rate=None,
                sgst_rate=None,
                line_total=line_total
            ))

            subtotal += taxable
            total_tax += tax_amount

        total = subtotal + total_tax

        new_invoice.subtotal = subtotal
        new_invoice.cgst = None
        new_invoice.sgst = None
        new_invoice.total = total

        db.session.commit()
        return redirect(url_for('view_invoice', invoice_id=new_invoice.id))

    # GET method: send combined products list for modal search
    materials = Material.query.all()
    finished_products = FinishedProduct.query.all()

    combined_products = [
        {
            'id': f'm_{m.id}',
            'name': m.material_name,
            'rate': m.rate or 0.0,
            'tax': m.tax or 0.0,
            'type': 'Material'
        } for m in materials
    ] + [
        {
            'id': f'f_{f.id}',
            'name': f.item_name,
            'rate': 0.0,
            'tax': 0.0,
            'type': 'FinishedProduct'
        } for f in finished_products
    ]

    return render_template('generate_invoice.html', products=combined_products)




@app.route('/view_invoice/<int:invoice_id>')
@login_required
@roles_required('super_access')
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('invoice.html', invoice=invoice)


# DASHBOARD ALERTS API
@app.route('/dashboard_alerts')
@login_required
@roles_required('super_access')
def dashboard_alerts():
    low_stock_count = Material.query.filter(Material.current_stock < Material.minimum_stock_level).count()
    pending_invoice_count = Invoice.query.filter(Invoice.total == 0).count() if 'invoice' in db.metadata.tables else 0
    return jsonify({'low_stock': low_stock_count, 'pending_invoices': pending_invoice_count})


@app.route('/invoice_history')
@login_required
@roles_required('super_access','manager_access','admin_access')
def invoice_history():
    invoices = Invoice.query.order_by(Invoice.date.desc()).all()
    return render_template('invoice_history.html', invoices=invoices)


@app.route('/add_material', methods=['GET', 'POST'])

#from flask import flash

@app.route('/add_material', methods=['GET', 'POST'])
@login_required
@roles_required('super_access','store_access')
def add_material():
    if request.method == 'POST':
        try:
            material_code  = generate_material_code()
            material = Material(
                material_code=request.form['material_code'],
                material_name=request.form['material_name'],
                vendor=request.form['vendor'],
                item_category=request.form['item_category'],
                unit_of_measurement=request.form['unit_of_measurement'],
                minimum_stock_level=int(request.form['minimum_stock_level']),
                current_stock=int(request.form['current_stock']),
                reorder_quantity=int(request.form['reorder_quantity']),
                purchase_history=request.form['purchase_history'],
                location=request.form.get('location'),
                tax=float(request.form['tax']),
                rate2=float(request.form['rate2'])
            )
            db.session.add(material)
            db.session.commit()

            transaction = MaterialTransaction(
                material_id=material.id,
                transaction_type='add',
                quantity=material.current_stock,
                transaction_date=datetime.today(),
                remarks='Material IN'
            )
            db.session.add(transaction)
            db.session.commit()

            flash('Material added successfully!', 'success')
            return redirect(url_for('add_material'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding material. Please try again.', 'error')
            return redirect(url_for('add_material'))

    next_code = generate_material_code()
    return render_template('add_material.html', material_code=next_code)



# Assuming you have a list for products
finished_goods_list = []

from flask import flash

@app.route('/add_finished_product', methods=['GET', 'POST'])
@login_required
@roles_required('super_access','manager_access')
# @roles_required('store_access')
def add_finished_product():
    if request.method == 'POST':
        fg_in_date_str = request.form.get('fg_in_date')
        fg_in_date = datetime.strptime(fg_in_date_str, '%Y-%m-%d').date() if fg_in_date_str else None

        item_code = request.form.get('item_code')
        number_value = request.form.get('number') or ''

        # Derive item_name and base model_number according to item_code
        if item_code == '105B':
            item_name = 'highstar'
            base_model_number = 'ATPL/MDL/DGN/02'
        elif item_code == '105C':
            item_name = 'highpower'
            base_model_number = 'ATPL/MDL/DGN/03'
        else:
            item_name = request.form.get('item_name') or ''
            base_model_number = request.form.get('model_number') or ''

        if item_code:
            sn_no_value = f"ATPLFB3W{item_code}512DL2507"
        else:
            sn_no_value = request.form.get('sn_no') or ''
        # Concatenate for battery_sn_number: "ATPLFB3W" + item_code + "512DL2507" + number
        battery_sn_number = f"ATPLFB3W{item_code}512DL2507{number_value}"

        fp = FinishedProduct(
            fg_in_date=fg_in_date,
            grn_no=request.form.get('grn_no'),
            item_code=item_code,
            item_name=item_name,
            # sn_no=sn_no_value,
            number=int(number_value) if number_value.isdigit() else 0,
            # battery_sn_number=battery_sn_number,
            # gps_number=request.form.get('gps_number') or None,
            # charger_number=request.form.get('charger_number') or None,
            model_number=base_model_number,
            # gps_imei_no=request.form.get('gps_imei_no') or None
        )

        db.session.add(fp)
        db.session.commit()
        flash('Finished product added successfully')
        return redirect(url_for('dashboard'))

    return render_template('add_finished_product.html')


@app.route('/show_materials')
@login_required
@roles_required('super_access','store_access','admin_access')
def show_materials():
    materials = Material.query.all()  # Fetch data from DB
    materials_with_alert = []
    for m in materials:
        # If alert thresholds are not set, do not color or set default 'sufficient'
        if m.red_alert is not None and m.current_stock < m.red_alert:
            alert = 'red'
        elif m.yellow_alert is not None and m.current_stock < m.yellow_alert:
            alert = 'yellow'
        else:
            alert = 'sufficient'
        materials_with_alert.append((m,alert))

    return render_template('show_materials.html', materials=materials_with_alert)

@app.route('/show_finished_goods')
@login_required
@roles_required('super_access','store_access','manager_access','admin_access')
def show_finished_goods():
    products = FinishedProduct.query.all()
    return render_template('show_finished_goods.html', products=products)

@app.route('/modify_finished_product/<int:id>', methods=['GET', 'POST'])
def modify_finished_product(id):
    product = FinishedProduct.query.get_or_404(id)

    if request.method == 'POST':
        old_data = {
            'fg_in_date': product.fg_in_date,
            'grn_no': product.grn_no,
            'item_code': product.item_code,
            'item_name': product.item_name,
            # 'sn_no': product.sn_no,
            'number': product.number,
            # 'battery_sn_number': product.battery_sn_number,
            # 'gps_number': product.gps_number,
            # 'charger_number': product.charger_number,
            'model_number': product.model_number,
            # 'gps_imei_no': product.gps_imei_no
        }

        # Update fields
        product.fg_in_date = datetime.strptime(request.form['fg_in_date'], '%Y-%m-%d')
        product.grn_no = request.form['grn_no']
        product.item_code = request.form['item_code']
        product.item_name = request.form['item_name']
        # product.sn_no = request.form['sn_no']
        product.number = int(request.form['number'])
        # product.battery_sn_number = request.form['battery_sn_number']
        # product.gps_number = request.form.get('gps_number')
        # product.charger_number = request.form.get('charger_number')
        product.model_number = request.form['model_number']
        # product.gps_imei_no = request.form.get('gps_imei_no')

        # Commit changes to DB
        db.session.commit()

        changes = []
        remarks = ""

        for key, old_value in old_data.items():
            new_value = getattr(product, key)
            if old_value != new_value:
                changes.append(f"{key} : {old_value} -> {new_value}")

        if changes:
            remarks = "[" + "; ".join(changes) + "]"
            # You can handle the remarks further, e.g., log or save to the database

        return redirect(url_for('show_finished_goods'))

    return render_template('modify_finished_good.html', product=product)



@app.route('/search', methods=['GET', 'POST'])
@login_required
@roles_required('super_access','store_access','admin_access')
def search():
    query = request.args.get('query')
    materials = []
    products = []
    if query:
        # Case-insensitive search by code or name in materials
        materials = Material.query.filter(
            (Material.material_code.ilike(f'%{query}%')) |
            (Material.material_name.ilike(f'%{query}%'))
        ).all()
        # Case-insensitive search by code or name in products
        products = FinishedProduct.query.filter(
            (FinishedProduct.product_code.ilike(f'%{query}%')) |
            (FinishedProduct.name.ilike(f'%{query}%'))
        ).all()

    return render_template('search.html', query=query, materials=materials, products=products)

@app.route('/material_transaction', methods=['GET', 'POST'])
@login_required
@roles_required('super_access')
def material_transaction():
    materials = Material.query.all()
    if request.method == 'POST':
        material_id = int(request.form['material_id'])
        transaction_type = request.form['transaction_type']
        quantity = int(request.form['quantity'])
        remarks = request.form['remarks']
        transaction_date_str = request.form['transaction_date']
        transaction_date = datetime.strptime(transaction_date_str, '%Y-%m-%d').date()

        transaction = MaterialTransaction(
            material_id=material_id,
            transaction_type=transaction_type,
            quantity=quantity,
            transaction_date=transaction_date,
            remarks=remarks
        )
        db.session.add(transaction)
        db.session.commit()
        # Optional: Update current stock accordingly or handle in reconciliation
        return redirect(url_for('material_transaction'))
    return render_template('material_transaction.html', materials=materials)

@app.route('/history')
@login_required
@roles_required('super_access','store_access','manager_access','admin_access')
def history():
    filter_type = request.args.get('type', 'material')

    if filter_type == 'finished_goods':
        # Fetch finished goods transactions with related product data
        records = FinishedProductTransaction.query.join(FinishedProduct).all()
    else:
        # Default to material transactions with material data
        records = MaterialTransaction.query.join(Material).all()

    return render_template('history.html', records=records, filter_type=filter_type)

from flask import Flask, render_template, request, redirect, url_for, abort
from datetime import date
# ... (other imports and configurations)

# Update Material Stock Route
@app.route('/update_material/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('super_access')
def update_material(id):
    material = Material.query.get_or_404(id)
    if request.method == 'POST':
        try:
            new_stock = int(request.form['current_stock'])
        except ValueError:
            return "Invalid stock quantity", 400
        old_stock = material.current_stock or 0
        material.current_stock = new_stock
        db.session.commit()
        quantity_change = new_stock - old_stock
        if quantity_change != 0:
            transaction_type = 'stock_increase' if quantity_change > 0 else 'stock_decrease'
            transaction = MaterialTransaction(
                material_id=material.id,
                transaction_type=transaction_type,
                quantity=abs(quantity_change),
                transaction_date=date.today(),
                remarks='Stock updated manually'
            )
            db.session.add(transaction)
            db.session.commit()
        return redirect(url_for('show_materials'))
    return render_template('update_material.html', material=material)

# Update Finished Product Stock Route
@app.route('/update_finished_product/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('super_access')
def update_finished_product(id):
    product = FinishedProduct.query.get_or_404(id)
    if request.method == 'POST':
        try:
            new_stock = int(request.form['current_stock'])
        except ValueError:
            return "Invalid stock quantity", 400
        old_stock = product.current_stock or 0
        product.current_stock = new_stock
        db.session.commit()
        quantity_change = new_stock - old_stock
        if quantity_change != 0:
            transaction_type = 'stock_increase' if quantity_change > 0 else 'stock_decrease'
            transaction = FinishedProductTransaction(
                finished_product_id=product.id,
                transaction_type=transaction_type,
                quantity=abs(quantity_change),
                transaction_date=date.today(),
                remarks='Stock updated manually'
            )
            db.session.add(transaction)
            db.session.commit()
        return redirect(url_for('show_finished_goods'))
    return render_template('update_finished_product.html', product=product)

@app.route('/add_vendor', methods=['GET', 'POST'])
@login_required
@roles_required('super_access','store_access')
def add_vendor():
    if request.method == 'POST':
        vendor_code = request.form['vendor_code']
        company_name = request.form['company_name']
        contact = request.form['contact']
        address = request.form['address']
        gstin = request.form['gstin']
        material_type = request.form['material_type']
        country = request.form['country']
        state = request.form['state']
        pin =  request.form['pin']

        vendor = Vendor(
            vendor_code=vendor_code,
            company_name=company_name,
            contact=contact,
            address=address,
            gstin=gstin,
            material_type=material_type,
            country = country,
            state=state,
            pin=pin
        )
        db.session.add(vendor)
        db.session.commit()
        return redirect(url_for('show_vendors'))

    return render_template('add_vendor.html')
@app.route('/show_vendors')
@login_required
@roles_required('super_access','store_access','admin_access')
def show_vendors():
    vendors = Vendor.query.all()
    return render_template('show_vendors.html', vendors=vendors)





@app.route('/export/<string:table_name>')
@login_required
@roles_required('super_access','manager_access','admin_access')
def export_data(table_name):
    output = io.StringIO()
    writer = csv.writer(output)

    if table_name == 'materials':
        data = Material.query.all()
        writer.writerow(['ID', 'Material Code', 'Material Name', 'Vendor', 'Item Category',
                         'UOM', 'Min Stock', 'Current Stock', 'Reorder Qty', 'Purchase History'])
        for m in data:
            writer.writerow([m.id, m.material_code, m.material_name, m.vendor, m.item_category,
                             m.unit_of_measurement, m.minimum_stock_level, m.current_stock,
                             m.reorder_quantity, m.purchase_history])

    elif table_name == 'finished_products':
        data = FinishedProduct.query.all()
        writer.writerow(['ID', 'Product Code', 'Name', 'Capacity', 'Configuration',
                         'Model Name', 'Dealer Zone', 'Current Stock'])
        for p in data:
            writer.writerow([p.id, p.product_code, p.name, p.capacity, p.configuration,
                             p.model_name, p.dealer_zone, p.current_stock])

    elif table_name == 'vendors':
        data = Vendor.query.all()
        writer.writerow(['ID', 'Vendor Code', 'Company Name', 'Contact', 'Address',
                         'GSTIN', 'Material Type'])
        for v in data:
            writer.writerow([v.id, v.vendor_code, v.company_name, v.contact,
                             v.address, v.gstin, v.material_type])
    else:
        return "Invalid table name", 400

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={table_name}.csv"
    response.headers["Content-type"] = "text/csv"
    return response

from sqlalchemy.exc import IntegrityError

@app.route('/import/<string:table_name>', methods=['GET', 'POST'])
@login_required
@roles_required('super_access')
def import_data(table_name):
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            return "No file uploaded", 400 #it will return the written string

        filename = file.filename.lower()

        import pandas as pd
        if filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(file)
        elif filename.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            return "Only .csv or .xlsx files are allowed", 400

        try:
            if table_name == 'materials':
                for _, row in df.iterrows():
                    # Check if material_code already exists
                    existing = Material.query.filter_by(material_code=row.get('material_code') or row.get('Material Code')).first()
                    if existing:
                        # Optionally update existing record here or continue
                        continue

                    new_material = Material(
                        material_code=row.get('material_code') or row.get('Material Code'),
                        material_name=row.get('material_name') or row.get('Material Name'),
                        vendor=row.get('vendor') or row.get('Vendor'),
                        item_category=row.get('item_category') or row.get('Item Category'),
                        unit_of_measurement=row.get('unit_of_measurement') or row.get('Unit Of Measurement'),
                        minimum_stock_level=int(row.get('minimum_stock_level') or row.get('Minimum Stock Level') or 0),
                        current_stock=int(row.get('current_stock') or row.get('Current Stock') or 0),
                        reorder_quantity=int(row.get('reorder_quantity') or row.get('Reorder Quantity') or 0),
                        purchase_history=row.get('purchase_history') or row.get('Purchase History')
                    )
                    db.session.add(new_material)

            elif table_name == 'vendors':
                for _, row in df.iterrows():
                    existing = Vendor.query.filter_by(vendor_code=row.get('vendor_code') or row.get('Vendor Code')).first()
                    if existing:
                        continue
                    new_vendor = Vendor(
                        vendor_code=row.get('vendor_code') or row.get('Vendor Code'),
                        company_name=row.get('company_name') or row.get('Company Name'),
                        contact=row.get('contact') or row.get('Contact'),
                        address=row.get('address') or row.get('Address'),
                        gstin=row.get('gstin') or row.get('GSTIN'),
                        material_type=row.get('material_type') or row.get('Material Type')
                    )
                    db.session.add(new_vendor)

            elif table_name == 'finished_products':
                for _, row in df.iterrows():
                    existing = FinishedProduct.query.filter_by(product_code=row.get('product_code') or row.get('Product Code')).first()
                    if existing:
                        continue
                    new_product = FinishedProduct(
                        product_code=row.get('product_code') or row.get('Product Code'),
                        name=row.get('name') or row.get('Name'),
                        capacity=row.get('capacity') or row.get('Capacity'),
                        configuration=row.get('configuration') or row.get('Configuration'),
                        model_name=row.get('model_name') or row.get('Model Name'),
                        dealer_zone=row.get('dealer_zone') or row.get('Dealer Zone'),
                        current_stock=int(row.get('current_stock') or row.get('Current Stock') or 0)
                    )
                    db.session.add(new_product)

            else:
                return "Invalid table name", 400

            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            return "Integrity error: Possible duplicate or invalid data detected.", 400

        return f"{table_name.replace('_', ' ').title()} data imported successfully!"

    return render_template('import.html', table_name=table_name)

ALLOWED_USERS = {
    'admin_user': 'super_access',
    'ritesh': 'super_access',
    'store': 'store_access',
    'manager': 'manager_access',
    'admin': 'admin_access'
    # Add more usernames and roles here to control access
}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username not in ALLOWED_USERS:
            flash('Username not authorized to register. Contact admin.', 'danger')
            return redirect(url_for('register'))

        if User.query.filter_by(username=username).first():
            flash('Username already registered, please login.', 'info')
            return redirect(url_for('login'))

        role = ALLOWED_USERS[username]

        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('dashboard'))

    return render_template('login.html')
@app.route('/requisition/edit/<int:requisition_id>', methods=['GET', 'POST'])
def edit_requisition(requisition_id):
    requisition = Requisition.query.get_or_404(requisition_id)

    if request.method == 'POST':
        # Update requisition fields from form data
        requisition.requisition_no = request.form.get('requisition_no')
        requisition.order_no = request.form.get('order_no')

        date_str = request.form.get('date')
        if date_str:
            requisition.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            requisition.date = None

        requisition.status = request.form.get('status')
        requisition.department = request.form.get('department')
        requisition.name = request.form.get('name')
        requisition.designation = request.form.get('designation')
        requisition.purpose = request.form.get('purpose')
        requisition.remark = request.form.get('remark')
        requisition.issuer_remark = request.form.get('issuer_remark')

        # Update item details - implement as needed based on your form structure
        for item in requisition.items:
            prefix = f'item_{item.id}_'
            item.material_name = request.form.get(prefix + 'material_name')
            item.material_code = request.form.get(prefix + 'material_code')
            item.unit_of_measurement = request.form.get(prefix + 'unit')
            item.current_stock = request.form.get(prefix + 'current_stock')
            item.quantity = request.form.get(prefix + 'quantity')
            item.vendor = request.form.get(prefix + 'vendor')
            item.rate = request.form.get(prefix + 'rate')

        try:
            db.session.commit()
            flash('Requisition updated successfully.', 'success')
            return redirect(url_for('requisition_history'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating requisition: ' + str(e), 'danger')

    return render_template('edit_requisition.html', req=requisition)

@app.route('/search_materials')
@login_required
@roles_required('super_access')
def search_materials():
    query = request.args.get('q', '')
    materials = Material.query.filter(Material.material_name.ilike(f'%{query}%')).all()
    results = [{'id': m.id, 'text': f"{m.material_name} (Stock: {m.current_stock})"} for m in materials]
    return jsonify(results)


from flask import jsonify


# @app.route('/purchase_order', methods=['GET', 'POST'])
# def purchase_order():
#     materials = Material.query.all()
#     if request.method == 'POST':
#         try:
#             po_number = request.form['purchase_order_number']
#             invoice_number = request.form['invoice_number']
#             grn_number = request.form['grn_number']
#             new_po = PurchaseOrder(
#                 purchase_order_number=po_number,
#                 invoice_number=invoice_number,
#                 grn_number=grn_number,
#                 date=datetime.today()
#             )
#             db.session.add(new_po)
#             db.session.flush()
#
#             material_ids = request.form.getlist('material_id')
#             quantities = request.form.getlist('quantity')
#             rates = request.form.getlist('rate')
#             totals = request.form.getlist('total')
#
#             for mid, qty, rate, total in zip(material_ids, quantities, rates, totals):
#                 qty = int(qty)
#                 rate = float(rate)
#                 total = float(total)
#                 if qty > 0:
#                     po_item = PurchaseOrderItem(
#                         purchase_order_id=new_po.id,
#                         product_id=int(mid),
#                         quantity=qty,
#                         rate=rate,
#                         total=total
#                     )
#                     material = Material.query.get(int(mid))
#                     material.current_stock += qty
#                     db.session.add(po_item)
#
#             db.session.commit()
#             return jsonify({"success": True, "message": "Purchase order added successfully"})
#
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({"success": False, "error": str(e)}), 500
#
#     return render_template('purchase_order.html', materials=materials)


from sqlalchemy.orm import joinedload

@app.route('/purchase_order_invoice/<int:po_id>')
@login_required
@roles_required('super_access')
def purchase_order_invoice(po_id):
    po = PurchaseOrder.query.options(
        joinedload(PurchaseOrder.items).joinedload(PurchaseOrderItem.material)
    ).get_or_404(po_id)

    items = po.items
    grand_total = sum(item.total for item in items)
    return render_template('purchase_order_invoice.html', po=po, items=items, grand_total=grand_total)

from flask import jsonify, request

@app.route('/api/materials')
@login_required
@roles_required('super_access')
def api_materials():
    q = request.args.get('q', '').lower()
    results = []
    materials = Material.query.filter(Material.material_name.ilike(f"%{q}%")).limit(20)
    for mat in materials:
        results.append({
            'id': mat.id,
            'text': f"{mat.material_name} ({mat.material_code})",
            'material_code': mat.material_code,
            'unit_of_measurement': mat.unit_of_measurement,
            'current_stock': mat.current_stock,
            'vendor': mat.vendor,
            'rate': mat.rate
        })
    return jsonify(results=results)

from flask import render_template, request, redirect, url_for, flash


from datetime import datetime

@app.route('/add_requisition', methods=['GET', 'POST'])
@login_required
@roles_required('super_access','store_access')
def add_requisition():
    if request.method == 'POST':
        # Header
        requisition_no = request.form['requisition_no']
        order_no = request.form.get('order_no', '')
        date_str = request.form.get('date', '')
        department = request.form.get('department', '')
        name = request.form.get('name', '')
        designation = request.form.get('designation', '')
        purpose = request.form.get('purpose', '')
        remark = request.form.get('remark', '')
        status = request.form.get('status', '')
        issuer_remark = request.form.get('issuer_remark', '')

        # Convert string date to Python date object
        date_obj = None
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                date_obj = None  # or handle as needed

        # Save master
        req = Requisition(
            requisition_no=requisition_no,
            order_no=order_no,
            date=date_obj,  # use the date object, not the string
            department=department,
            name=name,
            designation=designation,
            purpose=purpose,
            remark=remark,
            status=status,
            issuer_remark=issuer_remark
        )
        db.session.add(req)
        db.session.flush()

        # Items
        material_ids = request.form.getlist('material_id[]')
        quantities = request.form.getlist('quantity[]')

        for idx, mat_id in enumerate(material_ids):
            if not mat_id:
                continue
            qty = int(quantities[idx]) if quantities[idx] else 0
            mat = Material.query.get(int(mat_id))
            if mat and qty > 0:
                db.session.add(RequisitionItem(
                    requisition_id=req.id,
                    material_id=mat.id,
                    material_code=mat.material_code,
                    material_name=mat.material_name,
                    unit_of_measurement=mat.unit_of_measurement,
                    current_stock=mat.current_stock,
                    vendor=mat.vendor,
                    rate=mat.rate,
                    quantity=qty
                ))
                # Deduct stock
                mat.current_stock = max(0, mat.current_stock - qty)
        db.session.commit()
        flash("Requisition added and stock updated.", "success")
        return redirect(url_for('requisition_history'))

    # Pass today's date to the template for the date input default
    today_date = datetime.today().strftime('%Y-%m-%d')
    return render_template('add_requisition.html', today_date=today_date)

@app.route('/requisition_history')
@login_required
@roles_required('super_access','store_access','admin_access')
def requisition_history():
    # Get filter parameters from request args
    requisition_no = request.args.get('requisition_no', '').strip()
    department = request.args.get('department', '').strip()
    date_str = request.args.get('date', '').strip()

    # Build filter query
    query = Requisition.query

    if requisition_no:
        query = query.filter(Requisition.requisition_no.ilike(f"%{requisition_no}%"))
    if department:
        query = query.filter(Requisition.department.ilike(f"%{department}%"))
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(Requisition.date == date_obj)
        except ValueError:
            pass  # ignore invalid date

    requisitions = query.order_by(Requisition.date.desc()).all()

    return render_template('requisition_history.html', requisitions=requisitions)



@app.route('/api/purchase_orders')
@login_required
@roles_required('super_access')
def api_purchase_orders():
    try:
        pos = PurchaseOrder.query.options(
            joinedload(PurchaseOrder.items).joinedload('material')
        ).order_by(PurchaseOrder.date.desc()).all()

        data = []
        for po in pos:
            data.append({
                'id': po.id,
                'purchase_order_number': po.purchase_order_number,
                'grn_number': po.grn_number,
                'invoice_number': po.invoice_number,
                'date': po.date.strftime('%Y-%m-%d') if po.date else '',
                'items': [{
                    'product_name': item.material.material_name if item.material else '',
                    'material_code': item.material.material_code if item.material else '',
                    'vendor': item.material.vendor if item.material else '',
                    'rate': item.rate,
                    'quantity': item.quantity,
                    'total': item.total
                } for item in po.items]
            })

        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error in /api/purchase_orders: {e}")
        return jsonify({"error": "Internal Server Error"}), 500


@app.route('/search_purchase_orders', methods=['GET'])
@login_required
@roles_required('super_access')
def search_purchase_orders():
    q = request.args.get('q', '').strip()

    if q:
        results = PurchaseOrder.query.filter(
            (PurchaseOrder.purchase_order_number.ilike(f'%{q}%')) |
            (PurchaseOrder.invoice_number.ilike(f'%{q}%'))
        ).order_by(PurchaseOrder.date.desc()).all()
    else:
        results = []

    return render_template('search_purchase_orders.html', purchase_orders=results, query=q)


@app.route('/api/search_purchase_orders')
@login_required
@roles_required('super_access')
def api_search_purchase_orders():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])  # Return empty list if query is empty

    pos = PurchaseOrder.query.filter(
        (PurchaseOrder.purchase_order_number.ilike(f'%{q}%')) |
        (PurchaseOrder.invoice_number.ilike(f'%{q}%'))
    ).order_by(PurchaseOrder.date.desc()).all()

    results = [{
        'id': po.id,
        'purchase_order_number': po.purchase_order_number,
        'grn_number': po.grn_number,
        'invoice_number': po.invoice_number,
        'date': po.date.strftime('%Y-%m-%d') if po.date else ''
    } for po in pos]

    return jsonify(results)

from flask import request, redirect, url_for, flash

@app.route('/customer_out', methods=['GET', 'POST'])
@login_required
@roles_required('super_access')
def customer_out():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_address = request.form['customer_address']
        contact_number = request.form['contact_number']

        product_ids = request.form.getlist('product_id')
        quantities = request.form.getlist('quantity')

        # Validate lengths match, quantities positive, stock sufficient

        # For each product: fetch, update current_stock -= quantity

        for pid, qty_str in zip(product_ids, quantities):
            qty = int(qty_str)
            product = FinishedProduct.query.get(pid)
            if not product:
                flash(f"Product with ID {pid} not found")
                return redirect(url_for('customer_out'))

            if product.current_stock < qty:
                flash(f"Insufficient stock for product {product.name}")
                return redirect(url_for('customer_out'))

            product.current_stock -= qty
            # optionally create a stock transaction record here

            db.session.add(product)

        # Save customer out record, if you have a CustomerOut model
        # e.g.,
        # cust_out = CustomerOut(name=customer_name, address=customer_address, contact=contact_number)
        # db.session.add(cust_out)
        # db.session.commit()

        db.session.commit()
        flash("Customer dispatch saved successfully")
        return redirect(url_for('dashboard'))

    finished_products = FinishedProduct.query.all()
    return render_template('customer_out.html', finished_products=finished_products)

@app.route('/api/states/<country>')
@login_required
@roles_required('super_access')
def api_states(country):
    country_states = {
        'India': ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'],
        'China': ['Beijing', 'Shanghai', 'Guangdong','Anhui', 'Fujian', 'Gansu', 'Guangdong', 'Guizhou', 'Hainan', 'Hebei', 'Heilongjiang', 'Henan', 'Hubei', 'Hunan', 'Jiangsu', 'Jiangxi', 'Jilin', 'Liaoning', 'Qinghai', 'Shaanxi', 'Shandong', 'Shanxi', 'Sichuan', 'Yunnan', 'Zhejiang','Tianjin','HongKong','Xinjiang'],
        'Korea': ['Seoul', 'Busan', 'Incheon','Busan', 'Chagang', 'Chungcheongbuk', 'Chungcheongnam', 'Gyeonggi', 'Gyeongsangbuk', 'Gyeongsangnam', 'Hwanghae', 'Incheon', 'Jeju', 'Jeollabuk', 'Jeollanam', 'Kangwon', 'Nampo', 'Pyeongyang', 'Rason', 'Ryanggang' ],
    }
    return jsonify(states=country_states.get(country, []))

@app.route('/fetch_all_products')
@login_required
def fetch_all_products():
    materials = Material.query.all()
    finished_goods = FinishedProduct.query.all()

    combined = []
    for m in materials:
        combined.append({
            'id': f'm_{m.id}',
            'name': m.material_name,
            'rate': m.rate or 0.0,
            'tax': m.tax or 0.0,
            'type': 'Material'
        })
    for f in finished_goods:
        combined.append({
            'id': f'f_{f.id}',
            'name': f.item_name,
            'rate': 0.0,  # add actual rate if available
            'tax': 0.0,
            'type': 'FinishedProduct'
        })

    return jsonify(combined)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Customer Invoice Routes
@app.route('/customer_invoice', methods=['GET', 'POST'])
@login_required
@roles_required('super_access', 'manager_access')
def customer_invoice():
    if request.method == 'POST':
        # Process invoice creation
        customer_name = request.form['customer_name']
        customer_gstin = request.form.get('customer_gstin', '')
        customer_contact = request.form.get('customer_contact', '')
        customer_address = request.form.get('customer_address', '')

        # Create invoice
        invoice_number = f"CINV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        new_invoice = CustomerInvoice(
            invoice_number=invoice_number,
            customer_name=customer_name,
            customer_gstin=customer_gstin,
            customer_contact=customer_contact,
            customer_address=customer_address
        )
        db.session.add(new_invoice)
        db.session.flush()

        # Process line items
        product_names = request.form.getlist('product_name')
        quantities = request.form.getlist('quantity')
        rates = request.form.getlist('rate')
        taxes = request.form.getlist('tax_percent')

        subtotal = 0
        total_tax = 0

        for pname, qty_str, rate_str, tax_str in zip(product_names, quantities, rates, taxes):
            qty = float(qty_str)
            rate = float(rate_str)
            tax_rate = float(tax_str)

            if qty <= 0 or rate <= 0:
                continue

            # Handle product from both databases
            product_name_display = pname
            if pname.startswith('m_'):
                product_id = int(pname[2:])
                material = Material.query.get(product_id)
                product_name_display = material.material_name if material else pname
                if material:
                    material.current_stock = max(material.current_stock - qty, 0)
            elif pname.startswith('f_'):
                product_id = int(pname[2:])
                product = FinishedProduct.query.get(product_id)
                product_name_display = product.item_name if product else pname

            taxable = qty * rate
            tax_amount = taxable * tax_rate / 100
            line_total = taxable + tax_amount

            # Save line item
            db.session.add(CustomerInvoiceItem(
                invoice_id=new_invoice.id,
                product_name=product_name_display,
                product_id=pname,
                quantity=qty,
                rate=rate,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                line_total=line_total
            ))

            subtotal += taxable
            total_tax += tax_amount

        total = subtotal + total_tax
        new_invoice.subtotal = subtotal
        new_invoice.total_tax = total_tax
        new_invoice.grand_total = total

        db.session.commit()
        return redirect(url_for('show_customer_invoices'))

    # GET: Fetch combined products for search
    materials = Material.query.all()
    finished_products = FinishedProduct.query.all()

    products = [
                   {'id': f'm_{m.id}', 'name': m.material_name, 'rate': m.rate or 0.0, 'tax': m.tax or 18.0,
                    'type': 'Material'}
                   for m in materials
               ] + [
                   {'id': f'f_{f.id}', 'name': f.item_name, 'rate': 0.0, 'tax': 18.0, 'type': 'FinishedProduct'}
                   for f in finished_products
               ]

    return render_template('customer_invoice.html', products=products)


@app.route('/fetch_customer_products')
@login_required
def fetch_customer_products():
    materials = Material.query.all()
    finished_products = FinishedProduct.query.all()

    combined = [
                   {'id': f'm_{m.id}', 'name': m.material_name, 'rate': m.rate or 0.0, 'tax': m.tax or 18.0,
                    'type': 'Material'}
                   for m in materials
               ] + [
                   {'id': f'f_{f.id}', 'name': f.item_name, 'rate': 0.0, 'tax': 18.0, 'type': 'FinishedProduct'}
                   for f in finished_products
               ]

    return jsonify(combined)


@app.route('/show_customer_invoices')
@login_required
@roles_required('super_access', 'manager_access')
def show_customer_invoices():
    invoices = CustomerInvoice.query.order_by(CustomerInvoice.created_at.desc()).all()
    return render_template('show_customer_invoices.html', invoices=invoices)


@app.route('/customer_invoice/<int:invoice_id>')
@login_required
def view_customer_invoice(invoice_id):
    invoice = CustomerInvoice.query.get_or_404(invoice_id)
    return render_template('view_customer_invoice.html', invoice=invoice)


@app.context_processor
def utility_processor():
    def grand_total_words(amount):
        # Amount to words converter
        numbers = {
            1000: 'Thousand', 100: 'Hundred', 90: 'Ninety', 80: 'Eighty', 70: 'Seventy',
            60: 'Sixty', 50: 'Fifty', 40: 'Forty', 30: 'Thirty', 20: 'Twenty',
            19: 'Nineteen', 18: 'Eighteen', 17: 'Seventeen', 16: 'Sixteen',
            15: 'Fifteen', 14: 'Fourteen', 13: 'Thirteen', 12: 'Twelve',
            11: 'Eleven', 10: 'Ten', 9: 'Nine', 8: 'Eight', 7: 'Seven',
            6: 'Six', 5: 'Five', 4: 'Four', 3: 'Three', 2: 'Two', 1: 'One',10000: 'ten thousand',100000: 'one lakh'
        }

        def convert(num):
            if num == 0: return 'Zero'
            result = []
            for value, word in numbers.items():
                count = 0
                while num >= value:
                    num -= value
                    count += 1
                if count:
                    if value >= 1000:
                        result.append(convert(count) + ' ' + word)
                    elif value == 100:
                        result.append(word)
                    else:
                        result.append(str(count) + ' ' + word if count > 1 else word)
            return ' '.join(result)

        int_part = int(amount)
        return f"Rupees {convert(int_part)} Only"

    return dict(grand_total_words=grand_total_words)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0",debug=True,port=8080)
