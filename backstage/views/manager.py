#CRUD
#Create: 管理者可新增課程到系統上
#Read: 管理者可以讀取各個課程及其資料 暫時還沒有
#Update: 管理者更新課程內容
#Delete: 管理者刪除某課程或是其中內容
from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER'] 
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        cid = request.values.get('delete')
        data = Product.get_course(cid)
        
        if(data == None):
            flash('failed')
        else:
            data = Product.get_course(cid)
            Product.delete_course(cid)
    
    elif 'edit' in request.values:
        cid = request.values.get('edit')
        return redirect(url_for('manager.edit', cid = cid))
    
    book_data = book()
    return render_template('productManager.html', bookdata = book_data, user=current_user.name)

def book():
    book_row = Product.get_all_course()
    book_data = []
    for i in book_row:
        book = {
                '課程編號': i[0],
                '課程名稱': i[1],
                '開課系所': i[2],
                '教師姓名': Course.get_course_tname(i[0]),
                '教室代號': i[4]
            }
        book_data.append(book)
    return book_data

@manager.route('/studentManager', methods=['GET', 'POST'])
@login_required
def studentManager():
    if request.method == 'POST':
        pass
    else:

#show student data
        order_row = Student.get_all_student()
        order_data = []
        for i in order_row:
            order = {
                
                '學號': i[0],
                '姓名': i[1],
                '權限': i[2],
                'Email': i[3],
                '緊急聯絡人姓名': i[4],
                '緊急聯絡人電話': i[5],
            }
            order_data.append(order)
            

    return render_template('student.html', orderData = order_data, user=current_user.name)



#新增課程
@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while(data != None):
            number = str(random.randrange( 10000, 99999))
            en = random.choice(string.ascii_letters)
            cid = en + number
            data = Product.get_course(cid)                             #這行為原始code用來跳離迴圈的條件，懶得修掉，data可以忽略
        cid = request.values.get('cid')
        name = request.values.get('name')
        department = request.values.get('department')
        tid = request.values.get('tid')
        roomid = request.values.get('roomid')

        if (len(name) < 1):
            return redirect(url_for('manager.productManager'))

        #防呆，避免輸入不存在的老師
        exist_teacher = Teacher.get_teacher()
        teacher_list = []
        for i in exist_teacher:
            teacher_list.append(i[0])
        exist_course = Course.get_all_course()
        course_list = []
        for i in exist_course:
            course_list.append(i[0])
        if (tid not in teacher_list):
            flash('FailedGet')
            return redirect(url_for('manager.productManager'))
        elif(cid in course_list):
            flash('FailedGet')
            return redirect(url_for('manager.productManager'))
        else:
            
            Product.add_course(
                {'cid' : cid,
                'cName' : name,
                'department' : department,
                'tid' : tid,
                'roomid' : roomid
                }
            )
            return redirect(url_for('manager.productManager'))

    return render_template('productManager.html')

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':

        
                    #防呆，避免輸入不存在的老師
        exist_teacher = Teacher.get_teacher()
        teacher_list = []
        for i in exist_teacher:
            teacher_list.append(i[0])
        if(request.values.get('tid') not in teacher_list):
            flash('FailedGet')
            return redirect(url_for('manager.productManager'))

        Product.update_course(
            {
            'cid' : request.values.get('cid'),
            'cName' : request.values.get('cname'),
            'department' : request.values.get('department'),
            'tid' : request.values.get('tid'),
            'roomid' : request.values.get('roomid')
            }
        )

        return redirect(url_for('manager.productManager'))

    else:
        course = show_info()
        return render_template('edit.html', data = course, user=current_user.name)


def show_info():
    cid = request.args['cid']
    data = Product.get_course(cid)
    cname = data[1]
    department = data[2]
    tid = data[3]
    roomid = data[4]

    product = {
        '課程編號': cid,
        '課程名稱': cname,
        '開課系所': department,
        '教師代碼': tid,
        '教室代碼': roomid,
    }
    return product

#顯示教師資料
@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))


    if request.method == 'POST':
        pass
    else:
        order_row = Teacher.get_teacher()
        order_data = []
        for i in order_row:
            order = {
                '教師編號': i[0],
                '教師姓名': i[1],
            }
            order_data.append(order)
            

    return render_template('orderManager.html', orderData = order_data, user=current_user.name)

@manager.route('/selectmanage', methods=['GET', 'POST'])
@login_required
def selectmanage():
    # 以防使用者誤闖
    if request.method == 'GET':
        if (current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('manager.home'))                  

    course_row = Selerecord.get_all_record(); #取得所有選課紀錄
    course_data = []
    for i in course_row:
        cid = i[1]
        tname = Course.get_course_tname(cid)
        course = {
            '課程編號': cid,
            '課程名稱': Course.get_course(cid)[1],
            '開課系所': Course.get_course(cid)[2],
            '教師姓名': tname,
            '選課帳號': i[0],
            '選課學號':Student.get_studentid(i[0])
        }
        course_data.append(course)
    
    # if request.method =='POST':
    #     if "delete" in request.form:
    #         cid = request.values.get('delete')  #要刪的課程編號
    #         Selerecord.delete_course(current_user.id, cid)   


    #課程資料顯示

    return render_template('selectmanage.html',data = course_data,user=current_user.name)