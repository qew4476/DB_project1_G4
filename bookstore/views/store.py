import re
from typing_extensions import Self
from flask import Flask, request, template_rendered, Blueprint
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from numpy import identity, product
import random
import string
from sqlalchemy import null
from link import *
import math
from base64 import b64encode
from api.sql import Member, Order_List, Product, Record, Cart, Course, Selerecord

store = Blueprint('bookstore', __name__, template_folder='../templates')


@store.route('/', methods=['GET', 'POST'])
@login_required
def bookstore():
    hasSelected = Selerecord.get_record(current_user.id)   # 已選課程
    hasSelected_cid = []
    for i in hasSelected:
        hasSelected_cid.append(i[1])


    result = Course.count()
    count = math.ceil(result[0]/9)
    flag = 0

    # 若為管理者則無法進入
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        search = request.values.get('keyword')
        keyword = search

        cursor.prepare('SELECT * FROM COURSE WHERE CNAME LIKE :search OR DEPARTMENT LIKE :search OR TID LIKE :search OR CID LIKE :search')
        cursor.execute(None, {'search': '%' + keyword + '%'})
        book_row = cursor.fetchall()
        book_data = []
        final_data = []

# book是指課程
        for i in book_row:
            book = {
                '課程編號': i[0],
                '課程名稱': i[1],
                '開課系所': i[2],
                '教室': i[4],
                '教師姓名': Course.get_course_tname(i[0])
            }
            book_data.append(book)
            total = total + 1

        if (len(book_data) < end):
            end = len(book_data)
            flag = 1

        for j in range(start, end):
            final_data.append(book_data[j])

        count = math.ceil(total/9)

        return render_template('bookstore.html', hasSelected_cid=hasSelected_cid,single=single, keyword=search, book_data=book_data, user=current_user.name, page=1, flag=flag, count=count)

    elif 'cid' in request.args:
        cid = request.args['cid']
        data = Course.get_course(cid)

        cname = data[1]
        department = data[2]
        tid = data[3]  # 教師編號
        # description = data[4]
        # image = 'sdg.jpg'

        product = {
            '課程編號': cid,
            '課程名稱': cname,
            '開課系所': department,
            '教室': i[4],
            '教師編號': tid
        }

        return render_template('product.html', data=product, user=current_user.name)

    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9

        book_row = Course.get_all_course()
        book_data = []
        final_data = []

        for i in book_row:
            book = {
                '課程編號': i[0],
                '課程名稱': i[1],
                '開課系所': i[2],
                '教室': i[4],
                '教師姓名': Course.get_course_tname(i[0])

            }
            book_data.append(book)

        if (len(book_data) < end):
            end = len(book_data)
            flag = 1

        for j in range(start, end):
            final_data.append(book_data[j])

        return render_template('bookstore.html', hasSelected_cid=hasSelected_cid,book_data=final_data, user=current_user.name, page=page, flag=flag, count=count)

    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')
        keyword = search
        cursor.prepare('SELECT * FROM COURSE WHERE CNAME LIKE :search OR DEPARTMENT LIKE :search OR TID LIKE :search OR CID LIKE :search')
        cursor.execute(None, {'search': '%' + keyword + '%'})
        book_row = cursor.fetchall()
        book_data = []
        total = 0

        for i in book_row:
            book = {
                '課程編號': i[0],
                '課程名稱': i[1],
                '開課系所': i[2],
                '教室': i[4],
                '教師姓名': Course.get_course_tname(i[0])
            }

            book_data.append(book)
            total = total + 1

        if (len(book_data) < 9):
            flag = 1

        count = math.ceil(total/9)

        return render_template('bookstore.html', hasSelected_cid=hasSelected_cid,keyword=search, single=single, book_data=book_data, user=current_user.name, page=1, flag=flag, count=count)

    else:
        book_row = Course.get_all_course()
        book_data = []
        temp = 0
        for i in book_row:
            book = {
                '課程編號': i[0],
                '課程名稱': i[1],
                '開課系所': i[2],
                '教室': i[4],
                '教師姓名': Course.get_course_tname(i[0])
            }
            if len(book_data) < 9:
                book_data.append(book)

        return render_template('bookstore.html', hasSelected_cid=hasSelected_cid,book_data=book_data, user=current_user.name, page=1, flag=flag, count=count)


# 加選
@store.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    # 回傳有cid代表要加課
    if request.method == 'POST':
        if "cid" in request.form:

            cid = request.values.get('cid')  # 使用者想要加選的課程編號
            lesson_row = Selerecord.check_course(current_user.id, cid)  # 檢查使用者是否已經選過這門課

            if (lesson_row == None):  # 如果沒選過的話，加選
                Selerecord.add_course({'id': current_user.id, 'cid': cid})
 



                
    return redirect(url_for('bookstore.bookstore'))



@store.route('/selectPage', methods=['GET', 'POST'])
@login_required
def selectPage():
    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if request.method =='POST':
        if "delete" in request.form:
            cid = request.values.get('delete')  #要刪的課程編號
            Selerecord.delete_course(current_user.id, cid)   
                  

    course_row = Selerecord.get_record(current_user.id)
    course_data = []
    for i in course_row:
        cid = i[1]
        tname = Course.get_course_tname(cid)
        course = {
            '課程編號': cid,
            '課程名稱': Course.get_course(cid)[1],
            '開課系所': Course.get_course(cid)[2],
            '教師姓名': tname
        }
        course_data.append(course)

    #課程資料顯示

    return render_template('cart.html',user = current_user.name,data = course_data)

# def only_SelePage():    #return 當下這名使用者的選課資料

#     count = Selerecord.get_oneRecord(current_user.id)   #取得使用者一筆選課資料，用來判斷是否有選過課

#     if (count == None):
#         return 0
#     course_row = Selerecord.get_record(current_user.id)
#     course_data = []
#     for i in course_row:
#         cid = i[1]
#         tname = Course.get_course_tname(cid)
#         course = {
#             '課程編號': cid,
#             '課程名稱': Course.get_course(cid)[1],
#             '開課系所': Course.get_course(cid)[2],
#             '教師姓名': tname
#         }
#         course_data.append(course)

#     return course_data



def only_cart():

    count = Cart.check(current_user.id)

    if (count == None):
        return 0

    data = Cart.get_cart(current_user.id)
    tno = data[2]
    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pid = i[1]
        pname = Product.get_name(i[1])
        price = i[3]
        amount = i[2]

        product = {
            '商品編號': pid,
            '商品名稱': pname,
            '商品價格': price,
            '數量': amount
        }
        product_data.append(product)

    return product_data






# 會員購物車
@store.route('/cart', methods=['GET', 'POST'])
@login_required  # 使用者登入後才可以看
def cart():

    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    # 回傳有 pid 代表要 加商品
    if request.method == 'POST':

        if "pid" in request.form:
            data = Cart.get_cart(current_user.id)

            if (data == None):  # 假如購物車裡面沒有他的資料
                time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                Cart.add_cart(current_user.id, time)  # 幫他加一台購物車
                data = Cart.get_cart(current_user.id)

            tno = data[2]  # 取得交易編號
            pid = request.values.get('pid')  # 使用者想要購買的東西
            # 檢查購物車裡面有沒有商品
            product = Record.check_product(pid, tno)
            # 取得商品價錢
            price = Product.get_product(pid)[2]

            # 如果購物車裡面沒有的話 把他加一個進去
            if (product == None):
                Record.add_product(
                    {'id': tno, 'tno': pid, 'price': price, 'total': price})
            else:
                # 假如購物車裡面有的話，就多加一個進去
                amount = Record.get_amount(tno, pid)
                total = (amount+1)*int(price)
                Record.update_product(
                    {'amount': amount+1, 'tno': tno, 'pid': pid, 'total': total})

        elif "delete" in request.form:
            pid = request.values.get('delete')
            tno = Cart.get_cart(current_user.id)[2]

            Member.delete_product(tno, pid)
            product_data = only_cart()

        elif "user_edit" in request.form:
            change_order()
            return redirect(url_for('bookstore.bookstore'))

        elif "buy" in request.form:
            change_order()
            return redirect(url_for('bookstore.order'))

        elif "order" in request.form:
            tno = Cart.get_cart(current_user.id)[2]
            total = Record.get_total_money(tno)
            Cart.clear_cart(current_user.id)

            time = str(datetime.now().strftime('%Y/%m/%d %H:%M:%S'))
            format = 'yyyy/mm/dd hh24:mi:ss'
            Order_List.add_order(
                {'mid': current_user.id, 'time': time, 'total': total, 'format': format, 'tno': tno})

            return render_template('complete.html', user=current_user.name)

    product_data = only_cart()

    if product_data == 0:
        return render_template('empty.html', user=current_user.name)
    else:
        return render_template('cart.html', data=product_data, user=current_user.name)


@store.route('/order')
def order():
    data = Cart.get_cart(current_user.id)
    tno = data[2]

    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pname = Product.get_name(i[1])
        product = {
            '商品編號': i[1],
            '商品名稱': pname,
            '商品價格': i[3],
            '數量': i[2]
        }
        product_data.append(product)

    total = Record.get_total(tno)[0]

    return render_template('order.html', data=product_data, total=total, user=current_user.name)


@store.route('/orderlist')
def orderlist():
    if "oid" in request.args:
        pass

    user_id = current_user.id

    data = Member.get_order(user_id)
    orderlist = []

    for i in data:
        temp = {
            '訂單編號': i[0],
            '訂單總價': i[3],
            '訂單時間': i[2]
        }
        orderlist.append(temp)

    orderdetail_row = Order_List.get_orderdetail()
    orderdetail = []

    for j in orderdetail_row:
        temp = {
            '訂單編號': j[0],
            '商品名稱': j[1],
            '商品單價': j[2],
            '訂購數量': j[3]
        }
        orderdetail.append(temp)

    return render_template('orderlist.html', data=orderlist, detail=orderdetail, user=current_user.name)


def change_order():
    data = Cart.get_cart(current_user.id)
    tno = data[2]  # 使用者有購物車了，購物車的交易編號是什麼
    product_row = Record.get_record(data[2])

    for i in product_row:

        # i[0]：交易編號 / i[1]：商品編號 / i[2]：數量 / i[3]：價格
        if int(request.form[i[1]]) != i[2]:
            Record.update_product({
                'amount': request.form[i[1]],
                'pid': i[1],
                'tno': tno,
                'total': int(request.form[i[1]])*int(i[3])
            })
            print('change')

    return 0




