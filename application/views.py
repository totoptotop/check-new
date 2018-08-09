import sendgrid
import humanize, names
from flask import request, render_template, flash, current_app, jsonify, redirect, url_for, session, send_from_directory
from ldap3 import Server, Connection, ALL
from application import app, logger, cache
from application.decorators import threaded_async
from application.models import *
from forms import *
from time import time
from datetime import timedelta
from application.FW.triggerFW import generate_docx_html, getMondayDate
from threading import Thread

loaded_excel = False
generating = False

def check_login():
    if ('logged_in' in session):
        if (session['logged_in'] == True): 
            return True, session['role']
    session['logged_in'] = False
    return False, 'Guest'

def doReport():
    global generating
    generate_docx_html()
    generating = False

def writeLog(logStr):
    import time
    f = open('log/asset-'+time.strftime("%d-%m-%Y")+'.log','a+')
    f.write(time.strftime("%H:%M:%S") + ' - ' +logStr +'\n')
    f.close()

@app.route('/')
@app.route('/index')
def index():
        return redirect(url_for('ip_table'))

@app.route('/ip_table')
@app.route('/ip_table/')
def ip_table():
    ipDB = IpTable()
    list_vlans = ipDB.get_all_vlan()
    list_records = ipDB.list_all()
    return render_template("ip_table.html", list_records=list_records, list_vlans=list_vlans)

@app.route('/autovlan', methods=['POST'])
def autovlan():
    def cut_to_vlan(ipadr):
        if (ipadr == ''):
            return ''
        import re
        research = re.search("(.*)\.",ipadr)
        ip_vlan = research.group(1)
        return ip_vlan

    ip_to_auto = request.form['ipadr']
    ip_to_auto = cut_to_vlan(ip_to_auto)
    tbl_IP = IpTable()
    vlan_detect = tbl_IP.query.with_entities(IpTable.ipAdress, IpTable.vlan).group_by(IpTable.vlan).all()
    vlaned = ''
    kq = False
    for sample_ip, vlan in vlan_detect:
        if (ip_to_auto == cut_to_vlan(sample_ip) and vlan != 'Other'):
            vlaned = vlan
            kq = True
            break
    rs = {
        'result': kq,
        'vlan_auto': vlaned
    }
    return jsonify(data=rs)


@app.route('/ip_table/add_record', methods=['GET', 'POST'])
def add_record():
    if not(check_login()[0]):
        return login()
    
    list_opers = IpTable().get_all_oper()[1:]
    form = Form_IP_Add(request.form)
    if request.method == 'POST':
        if form.validate():
            ipAdress = form.ipAdress.data
            hostName = form.hostName.data
            Owner = form.Owner.data
            dateStart = form.dateStart.data
            opersys = request.form['oper-sys']
            editor = session['user_name']
            status = 'active'
            service = request.form['inputService']
            vlan = 'Other'
            new_record = IpTable()
            if new_record.add_data(ipAdress, hostName, Owner, opersys, service, editor, status, vlan, added_time=dateStart):
                writeLog(request.remote_addr + ' - ' + session['user_name'] + ' - ' + 'add ' + str((ipAdress, hostName, Owner, opersys, service, editor, status, vlan, dateStart)))
                flash('IP ' + ipAdress + " added successfully.", category="success")
                # render_template("add_ip_record.html")
                # return redirect(url_for('add_record'))
            else:
                flash('IP ' + ipAdress + " da co trong database.", category="danger")
        # else:
        #     flash(str(form.validate()), category="danger")

    return render_template("add_ip_record.html", form=form, list_opers=list_opers)
    
@app.route('/ip_table/view', methods=['GET', 'POST'])
@app.route('/ip_table/view/<int:page>', methods=['GET', 'POST'])
def view_record(page=1, readonly=True):
    form = Form_IP_Add(request.form)
    list_opers = IpTable().get_all_oper()

    if request.method == 'POST':
        if form.validate():
            old_record = IpTable()
            ipAdress = form.ipAdress.data
            hostName = form.hostName.data
            Owner = form.Owner.data
            opersys = request.form['oper-sys']
            createDate = form.dateStart.data
            service = request.form['inputService']
            old_record.edit(page, ipAdress, hostName, Owner, opersys, createDate)
            logger.info("Editing a record.")
            writeLog(request.remote_addr + ' - ' + session['user_name'] + ' - ' + 'edit ' + str(page) + ' with date ' + str(request.form))
            flash('IP ' + ipAdress + " editted successfully.", category="success")
    ip_tbl = IpTable()
    record = ip_tbl.get_info_by_id(page)
    return render_template("ip_view.html", form=form, record=record, readonly=readonly, list_opers=list_opers)
    
@app.route('/ip_table/delete', methods=['GET'])
@app.route('/ip_table/delete/<int:ipID>', methods=['GET'])
def del_ipAdd(ipID=1, readonly=True):
    if not(check_login()[0]):
        return login()
    ip_record = IpTable()
    rs, ipaddr = ip_record.delete(ipID)
    if rs:
        writeLog(request.remote_addr + ' - ' + session['user_name'] + ' - ' + 'deletd ' + str(ipID) + ' as ' + ipaddr)
        flash("IP " + str(ipaddr) + " deleted!", category="success")
    else:
        flash("Record can NOT delete", category="danger")
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if (check_login()[0]):
        return index()
        
    tbl_users = UserTable()
    
    form = Form_Login(request.form)
    if request.method == 'POST':
        if form.validate():
            import hashlib
            m = hashlib.md5()
            uName = form.uName.data
            pWord = form.pWord.data
            if ('ncb-bank' in uName):
                import re
                research = re.search("(.*)\@ncb-bank",uName)
                domainName = research.group(1)
                accDomain = domainName+'@ncb-bank'
                logger.info(accDomain)
                rs = tbl_users.get_user(domainName,'HelloFromDomain')
                try:
                    conn = Connection('10.1.33.18',accDomain, password=pWord,auto_bind=True)
                    if rs['ok']:
                        session['logged_in'] = True
                        session['user_name'] = accDomain + '.vn'
                        session['role'] = rs['role']
                        logger.info("logged " + session['user_name'] + ".")
                        writeLog(request.remote_addr + ' - ' + uName + ' - ' + 'logged')
                        return redirect(url_for('index'))
                    else:
                        writeLog(request.remote_addr + ' - ' + uName + ' - ' + 'permission failed')
                        flash('You do NOT have any permission to be here!','danger')
                except:
                    writeLog(request.remote_addr + ' - ' + uName + ' - ' + 'login failed')
                    flash("Wrong password or username", 'danger')
            else:
                m.update(pWord)
                rs = tbl_users.get_user(uName, str(m.hexdigest()))
                if rs['ok']:
                    session['logged_in'] = True
                    session['user_name'] = rs['name']
                    session['role'] = rs['role']
                    logger.info("logged " + session['user_name'] + ".")
                    writeLog(request.remote_addr + ' - ' + uName + ' - ' + 'logged')
                    return redirect(url_for('index'))
                else:
                    writeLog(request.remote_addr + ' - ' + uName + ' - ' + 'login failed')
                    flash("Wrong password or username", 'danger')
                
    return render_template("login.html", form=form)

@app.route("/logout")
def logout():
    if not(check_login()[0]):
        return index()
    session['logged_in'] = False
    return redirect(url_for('login'))
    
@app.route('/add_admin')
def add_admin(userId=0):
    result = UserTable().add_data('toanpho','ToanPVN','9b24968048f98e9414f50af062f3f3f6', 'admin')
    return jsonify(data=result)
    
@app.route('/fanboy')
def account():
    return render_template("account.html")

@app.route('/admin')
def admin():
    chk_login = check_login()
    if (not chk_login[0]):
        return login()
    list_accounts = UserTable().get_all_user()
    list_owners = IpTable().get_all_owner()
    import time
    try:
        f = open('log/asset-'+time.strftime("%d-%m-%Y")+'.log','r').read()
    except:
        f = 'Nothing gonna change my love for you'
    return render_template("admin.html", list_accounts=list_accounts, list_owners=list_owners, rawLog = f)

@app.route('/admin/command', methods=['POST'])
def admin_command():
    chk_login = check_login()
    if (not chk_login[0]):
        return login()
    if (request.form['command'] == 'add'):
        import re
        email = request.form['inputEmail']
        research = re.search("(.*)\@ncb-bank",email)

        if (research is None):
            flash('Wrong email format!! >"< Does "'+email+'" is a fucking email??', 'danger')
        else:
            domainName = research.group(1)
            result = UserTable().add_data(domainName,domainName+'@ncb-bank.vn','HelloFromDomain', request.form['role'])
            flash('Add ok '+domainName+' as an "' + request.form['role'] +'"! <3', 'success')
            writeLog(request.remote_addr + ' - ' + session['user_name'] + ' - ' + 'add ' + email + ' as ' + str(request.form['role']))
########################################################
    elif (request.form['command'] == 'del'):
        del_success = []
        del_error = []
        for user_id in request.form.getlist('users'):
            rs,uname = UserTable().del_user(user_id)
            writeLog(request.remote_addr + ' - ' + session['user_name'] + ' - ' + 'del ' + uname)
            if rs:
                del_success.append(uname)
            else:
                del_error.append(uname)
        if (len(del_success)>0):
            flash('Deleted '+ ', '.join(del_success) + ' !', 'success')
        if (len(del_error) > 0):
            flash('Can NOT delete'+ ', '.join(del_success) + ' !', 'danger')
##########################################################
    elif (request.form['command'] == 'replaceOwner'):
        oldOwner = request.form['oldOwner']
        newOwner = request.form['newOwner']
        tbl_IP = IpTable()
        rs = tbl_IP.replace_owner(oldOwner,newOwner)
        if (rs == True):
            logline = request.remote_addr + ' - ' + session['user_name'] + ' - ' + '[Success] replace ' + oldOwner + ' by ' + newOwner + '.'
            writeLog(logline)
            flash('Replace ' + oldOwner + ' by ' + newOwner + ' successfully!', 'success')
        else:
            logline = request.remote_addr + ' - ' + session['user_name'] + ' - ' + '[Failed] replace ' + oldOwner + ' by ' + newOwner + '.'
            writeLog(logline)
            flash('Replace ' + oldOwner + ' by ' + newOwner + ' error!', 'danger')
    return redirect(url_for('admin'))
    

@app.route('/report')
def report():
    import os
    import glob
    reportList = glob.glob(app.config['REPORT_FOLDER'] + '/*.html')
    reportList.sort(key=os.path.getctime, reverse=True)
    reportList = [elem.replace('application/static/FRT/','') for elem in reportList ]
    changeList = glob.glob(app.config['CHANGES_FOLDER'] + '/*.docx')
    changeList.sort(key=os.path.getctime, reverse=True)
    changeList = [elem.replace('application/static/Changes/','') for elem in changeList ]
    return render_template("report.html", reportList = reportList, changeList=changeList)

@app.route('/report/generate')
def generate_():
    if not(check_login()[0]):
        return login()
    import os
    global generating
    if (generating):
        flash("I'm exporting report, please don't force me! :(", 'warning')
    else:
        writeLog(request.remote_addr + ' - ' + session['user_name'] + ' - ' + 'generate report')
        reportList = os.listdir(app.config['REPORT_FOLDER'])
        checkString = ''.join(reportList)
        day = getMondayDate()
        if day in checkString:
            flash('I have done report for this week, What the fuck do you want? >"<', 'warning')
        else:
            generating = True
            t = Thread(target=doReport, args=())
            t.start()
            return render_template('force.html')

    return redirect(url_for('report'))


@app.before_first_request
def before_first_request():
    logger.info(url_for('index'))
    global loaded_excel
    loaded_excel = False
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    logger.info("-------------------- initializing everything ---------------------")
    db.create_all()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

    
# @app.route('/service')
# @app.route('/service/<int:page>')
# def service(page=1):
#     m_tasks = IpTable()
#     list_records = m_tasks.list_all(page, app.config['LISTINGS_PER_PAGE'])

#     return render_template("service.html", list_records=list_records)

# @app.route('/service/add_record', methods=['GET', 'POST'])
# def add_service():
#     if (session['logged_in'] == False):
#         return redirect(url_for('login'))
    
#     form = Form_Service_Add(request.form)
#     if request.method == 'POST':
#         if form.validate():
#             flash("Record added successfully.", category="success")
#             # new_record = SampleTable()

#             # title = form.title.data
#             # description = form.description.data

#             # new_record.add_data(title, description)
#             # logger.info("Adding a new record.")
#             # flash("Record added successfully.", category="success")

#     return render_template("add_service.html", form=form)