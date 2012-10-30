import csv
from cStringIO import StringIO
import logging

from email.Utils import formataddr

from five import grok
from zope.interface import Interface

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

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
        pmt = getToolByName(self.context, 'portal_membership')

        self.errors = []
        self.data = []
        self.imported_users = []
        self.not_imported_users = []

        if self.request.get('submit.userimport', '') == 'Import':
            self.errors, self.data = self.extractData(self.request)
            if self.errors:
                return

            reader = csv.DictReader(self.data)
            errors, self.not_imported_users, self.imported_users = \
                self.import_users(reader, pmt)

            if errors:
                self.errors.extend(errors)
                LOG.info('\n'.join(self.errors))

    def extractData(self, request):
        data = self.request.form['userdata']
        errors = []
        if not data or len(data.readlines()) < 1:
            errors.append('No data supplied')
        data.seek(0)
        return errors, data
    
    def get_existing_users(self, reader, membershiptool):
        existing_users = set(membershiptool.listMemberIds())
        userids = set([line['userid'] for line in reader])
        not_created_ids = userids.intersection(existing_users)
        return not_created_ids

    def import_users(self, reader, membershiptool):
        existing_users = membershiptool.listMemberIds()
        imported_users = []
        not_imported_users = []
        errors = []
        linenum = 0
        for line in reader:
            linenum += 1
            userid = line['userid']
            LOG.info('Importing user:%s' % userid)
            if userid:
                if userid in existing_users:
                    not_imported_users.append(userid)
                else:
                    imported_users.append(userid)
                    password = line.get('password', userid)
                    roles = line.get('roles', ['Member',])
                    membershiptool.addMember(userid, password, roles, [], line)
            else:
                errors.append('Error on line:%s (%s)' % (linenum, line))

        return errors, not_imported_users, imported_users
