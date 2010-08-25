"""
_Create_

Implementation of Createfor Oracle.

Inherit from CreateAgent, and add Oracle specific substitutions (e.g. 
use trigger and sequence to mimic auto increment in MySQL.
"""

__revision__ = "$Id: Create.py,v 1.1 2010/06/21 21:18:22 sryu Exp $"
__version__ = "$Revision: 1.1 $"

from WMCore.Agent.Database.CreateAgentBase import CreateAgentBase

class Create(CreateAgentBase):
    """
    Class to set up the WMBS schema in a MySQL database
    """
    sequenceTables = ["wm_components", "wm_workers"]
    seqStartNum = 40
    
    def __init__(self, logger = None, dbi = None, params = None):
        """
        _init_

        Call the base class's constructor and create all necessary tables,
        constraints and inserts.
        """
        CreateAgentBase.__init__(self, logger, dbi, params)

        for tableName in self.sequenceTables:
            seqname = '%s_SEQ' % tableName
            self.create["%s%s" % (self.seqStartNum, seqname)] = """
            CREATE SEQUENCE %s start with 1 
            increment by 1 nomaxvalue cache 100""" % seqname

            triggerName = '%s_TRG' % tableName
            self.create["%s%s" % (self.seqStartNum, triggerName)] = """
                    CREATE TRIGGER %s
                        BEFORE INSERT ON %s
                        REFERENCING NEW AS newRow
                        FOR EACH ROW
                        BEGIN
                            SELECT %s.nextval INTO :newRow.id FROM dual;
                        END; """ % (triggerName, tableName, seqname)