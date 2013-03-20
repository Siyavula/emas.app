import csv
from cStringIO import StringIO
import logging

from email.Utils import formataddr

from five import grok
from zope import event
from zope.interface import Interface

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.PlonePAS.events import UserInitialLoginInEvent

LOG = logging.getLogger('import-users:')

grok.templatedir('templates')

class ImportUsers(grok.View):
    """ Import users from a CSV file.
    """
    
    grok.context(Interface)
    grok.require('cmf.ManagePortal')
    grok.name('import-users')
    
    required_fields = ["fullname",
                       "userid",
                       "email",
                       "school",]

    def update(self):
        self.mtool = getToolByName(self.context, 'portal_membership')

        self.errors = []
        self.data = []
        self.imported_users = []
        self.existing_users = []
        self.duplicate_userids = []

        if self.request.get('submit.userimport', '') == 'Import':
            self.errors, self.data = self.extractData()
            if self.errors:
                return

            self.import_users()

            if self.errors:
                LOG.info('\n'.join(self.errors))

    def extractData(self):
        data = self.request.form['userdata']
        errors = []
        if not data or len(data.readlines()) < 1:
            errors.append('No data supplied')
        data.seek(0)
        return errors, data
    
    def import_users(self):
        reader = csv.DictReader(self.data)
        existing_users = self.mtool.listMemberIds()
        linenum = 0
        for line in reader:
            linenum += 1
            userid = line['userid']
            LOG.info('Importing user:%s' % userid)
            if userid:
                if userid in existing_users:
                    self.existing_users.append(userid)
                elif userid in self.imported_users:
                    self.duplicate_userids.append(userid)
                else:
                    self.imported_users.append(userid)
                    password = line.get('password', userid)
                    roles = line.get('roles', ['Member',])
                    self.mtool.addMember(userid, password, roles, [], line)

                    # set initial login for user
                    login_time = self.context.ZopeTime() - 1
                    member = self.mtool.getMemberById(userid)
                    props = {'login_time': login_time,
                             'last_login_time': login_time}
                    member.setMemberProperties(props)
            else:
                self.errors.append('Error on line:%s (%s)' % (linenum, line))
