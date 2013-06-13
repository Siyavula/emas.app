from zope.interface import Interface
from emas.app import MessageFactory as _

class IEmasAppLayer(Interface):
    """ Marker interface for emas.app. """

class IMemberServiceDataAccess(Interface):

    def get_all_memberservices(self):
        """ Fetches all memberservices regardless of memberid, grade or subject.
            Useful for full export of all current memberservices or listing views.
        """
        pass

    def get_member_services_for(self, memberid):
        """ Fetches all memberservices for a specfic member.
            Ignores grade and subject.
            Ignores expiry dates.
        """
        pass

    def get_member_services_by_subject(self, memberid, subject):
        """ Fetches all memberservices for a specific member.
            Ignores expiry dates.
            Filters on subject.
        """
        pass

    def get_member_services_by_grade(self, memberid, grade):
        """ Fetches all memberservices for a specific member.
            Ignores expiry dates.
            Filters on grade.
        """
        pass

    def get_member_services_by_subject_and_grade(self, memberid, subject, grade):
        """ Fetches all memberservices for a specific member.
            Ignores expiry dates.
            Filters on subject and grade.
        """
        pass

    def get_active_member_services(self, memberid):
        """ Fetches only active memberservices for a given member.
            Ignores subject and grade.
        """
        pass

    def get_active_member_services_by_subject(self, memberid, subject):
        """ Fetches only active memberservices for a given member.
            Filters on subject.
        """
        pass

    def get_active_member_services_by_grade(self, memberid, grade):
        """ Fetches only active memberservices for a given member.
            Filters on grade.
        """
        pass

    def get_active_member_services_by_subject_and_grade(self, memberid, subject, grade):
        """ Fetches all active memberservices for a specific member.
            Filters on subject and grade.
        """
        pass

    def get_expired_member_services(self, memberid):
        """ Fetches only expired memberservices for a given member.
            Ignores subject and grade.
        """
        pass

    def get_expired_member_services_by_subject(self, memberid, subject):
        """ Fetches only expired memberservices for a given member.
            Filters on subject.
        """
        pass

    def get_expired_member_services_by_grade(self, memberid, grade):
        """ Fetches only expired memberservices for a given member.
            Filters on grade.
        """
        pass

    def get_expired_member_services_by_subject_and_grade(self, memberid, subject, grade):
        """ Fetches all expired memberservices for a specific member.
            Filters on subject and grade.
        """
        pass

    def get_memberservice_by_primary_key(id):
        """ Utility method.
            Useful if you know what the persistent store primary key is and just
            want to get that specific memberservice.
        """

    def add_memberservice(self, memberid, title, related_service_id, expiry_date,
                          credits=0, service_type="subscription"):
        """ Adds a memberservice to the persistent store.
            Sets all given attributes.
            Returns the primary key of the new memberservice.
        """
        pass

    def update_memberservice(memberservice):
        """ Updates and existing memberservice.
            Returns the primary key of the update memberservice.
        """
        pass

    def delete_memberservice(memberservice):
        """ Deletes a given memberservice from the persistent store.
        """
        pass

