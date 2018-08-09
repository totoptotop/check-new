import datetime

from sqlalchemy import desc, asc
from sqlalchemy import or_

from application import db

def IP2Int(ip):
    o = map(int, ip.split('.'))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res


class IpTable(db.Model):
    __tablename__ = "ipTable"
    id = db.Column(db.Integer, autoincrement= True, primary_key=True)
    intIP = db.Column(db.Integer)
    ipAdress = db.Column(db.String(255))
    hostname = db.Column(db.String(255))
    owner = db.Column(db.String(255))
    editor = db.Column(db.String(255))
    historyID = db.Column(db.Integer)
    vlan = db.Column(db.String(255))
    status = db.Column(db.String(255))
    opersys = db.Column(db.String(255))
    service = db.Column(db.String(255))
    added_time = db.Column(db.DateTime)

    def get_info_by_id(self, some_id):
        record = IpTable.query.filter(IpTable.id == some_id).first_or_404()
        aux = dict()
        aux['id'] = record.id
        aux['ipAdress'] = record.ipAdress
        aux['hostname'] = record.hostname
        aux['owner'] = record.owner
        aux['opersys'] = record.opersys
        aux['status'] = record.status
        aux['historyID'] = record.historyID
        aux['vlan'] = record.vlan
        aux['service'] = record.service
        aux['added_time'] = record.added_time.strftime('%d/%m/%Y')
        return aux

    def get_info_by_ip(self, some_ip):
        record = IpTable.query.filter(IpTable.ipAdress.like("%"+ some_ip +"%")).first()
        aux = dict()
        aux['id'] = record.id
        aux['ipAdress'] = record.ipAdress
        aux['hostname'] = record.hostname
        aux['owner'] = record.owner
        aux['opersys'] = record.opersys
        aux['status'] = record.status
        aux['historyID'] = record.historyID
        aux['vlan'] = record.vlan
        aux['service'] = record.service
        aux['added_time'] = record.added_time.strftime('%d/%m/%Y')
        return aux

    def add_data(self, ipAdress, hostname, owner, opersys, service, editor, status, vlan, historyID = 0, added_time=datetime.datetime.now()):
        try:
            new_record = IpTable(intIP=IP2Int(ipAdress), 
                ipAdress=ipAdress, hostname=hostname, 
                owner=owner, opersys=opersys, service=service,
                editor=editor, status=status,
                historyID=historyID, vlan=vlan, added_time=added_time)
            db.session.add(new_record)
            db.session.commit()
            return True
        except:
            return False

    def edit(self, ipID, ipAdress, hostname, owner, opersys, createDate):
        rc = IpTable.query.filter(IpTable.id == ipID).first_or_404()
        rc.hostname = hostname
        rc.owner = owner
        rc.opersys = opersys
        rc.added_time = createDate
        db.session.commit()
        
    def delete(self, ipID):
        record = IpTable.query.filter(IpTable.id == ipID).first()
        if (record is None):
            return False, ipID
        ipaddr = record.ipAdress
        db.session.delete(record)
        db.session.commit()
        return True, ipaddr
        
    def list_all(self):
        return IpTable.query.order_by(asc(IpTable.intIP)).all()
        
    def get_by_status(self,status):
        return IpTable.query.with_entities(IpTable.ipAdress).filter(IpTable.status == status).order_by(asc(IpTable.intIP)).all()

    def get_all_vlan(self):
        return IpTable.query.with_entities(IpTable.vlan).distinct().order_by(asc(IpTable.vlan)).all()

    def get_all_oper(self):
        return IpTable.query.with_entities(IpTable.opersys).distinct().order_by(asc(IpTable.opersys)).all()
    
    def get_all_owner(self):
        return IpTable.query.with_entities(IpTable.owner).distinct().order_by(asc(IpTable.owner)).all()

    def replace_owner(self, oldOwner, newOwner):
        records = IpTable.query.filter(IpTable.owner == oldOwner).all()
        for rc in records:
            rc.owner = newOwner
        try:
            # db.session.add_all()
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False


class UserTable(db.Model):
    __tablename__ = "account"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(255))
    name = db.Column(db.String(255))
    role = db.Column(db.String(255))
    passhash = db.Column(db.String(255))

    def get_user(self, user, passhash):
        record = UserTable.query.filter(UserTable.user == user, UserTable.passhash == passhash).first()
        aux = dict()
        if record == None :
            aux['ok'] = False
            return aux
        else:
            aux['ok'] = True
            aux['name'] = record.name
            aux['role'] = record.role
        return aux

    def get_all_user(self):
        return UserTable.query.with_entities(UserTable.user, UserTable.role, UserTable.id).all()

    def add_data(self, user, name, passhash, role):
        record = UserTable.query.filter(UserTable.name == name).first()
        new_record = UserTable(user=user, role=role, name=name, passhash=passhash)
        db.session.add(new_record)
        db.session.commit()
        return {'Status':'Success'}
        
    def del_user(self, userID):
        record = UserTable.query.filter(UserTable.id == userID).first()
        if (record is None):
            return False, userID
        username = record.name
        db.session.delete(record)
        db.session.commit()
        return True, username
        
    def get_id(self, some_id):
        record = UserTable.query.filter(UserTable.id == some_id).first()
        aux = dict()
        aux['id'] = record.id
        aux['user'] = record.user
        aux['name'] = record.name
        aux['passhash'] = record.passhash
        return aux