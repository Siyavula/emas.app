import csv
import cStringIO as StringIO
from datetime import datetime
from five import grok
from zope.interface import Interface
from zope.component import getUtility

from emas.app.usercatalog import IUserCatalog

class ExportUsers(grok.View):
    """ Export users.
    """

    grok.context(Interface)
    grok.require('cmf.ManagePortal')
    grok.name('export-users')

    def __call__(self):
        regStartDate = self.request.get('start-date')
        regEndDate = self.request.get('end-date')
        if regStartDate:
            regStartDate = datetime.strptime(regStartDate, '%Y-%m-%d')
        if regEndDate:
            regEndDate = datetime.strptime(regEndDate, '%Y-%m-%d')
        if regStartDate or regEndDate:
            regDateFilter = (regStartDate, regEndDate)
        else:
            regDateFilter = None
        usercatalog = getUtility(IUserCatalog)
        users = usercatalog.search(regdate=regDateFilter)
        csvfile = StringIO.StringIO()
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["username", "fullname", "email",
                            "registrationdate"])
        for usermd in users:
            csvwriter.writerow([usermd['username'],
                                usermd['fullname'],
                                usermd['email'],
                                usermd['registrationdate']])

        result = csvfile.getvalue()
        csvfile.close()

        filename = 'user-export-%s.csv' % datetime.today().strftime('%Y-%m-%d')
        self.request.RESPONSE.setHeader('Content-Type',
            'text/comma-separated-values')
        self.request.RESPONSE.setHeader('Content-Disposition',
            'attachment; filename=%s' % filename)
        self.request.RESPONSE.setHeader('Content-Length', len(result))
        self.request.RESPONSE.setHeader('Cache-Control', 's-maxage=0')

        return result

    def render(self):
        return ''
