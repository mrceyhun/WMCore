#!/usr/bin/env python
"""
_Workflow_

A simple object representing a Workflow in WMBS.

A workflow has an owner (e.g. PA instance, CRAB server user) and
a specification. The specification describes how jobs should be 
created and what the jobs are supposed to do. This description 
is held external to WMBS, WMBS just stores a pointer (url) to 
the specification file. A workflow can be used with many 
filesets and subscriptions (e.g. repeating the same task on a 
bunch of data).

workflow + fileset = subscription
"""

__revision__ = "$Id: Workflow.py,v 1.21 2009/05/08 16:04:10 sfoulkes Exp $"
__version__ = "$Revision: 1.21 $"

from WMCore.WMBS.WMBSBase import WMBSBase
from WMCore.DataStructs.Workflow import Workflow as WMWorkflow
from WMCore.WMBS.Fileset import Fileset

class Workflow(WMBSBase, WMWorkflow):
    """
    A simple object representing a Workflow in WMBS.

    A workflow has an owner (e.g. PA instance, CRAB server user) and
    a specification. The specification describes how jobs should be 
    created and what the jobs are supposed to do. This description 
    is held external to WMBS, WMBS just stores a pointer (url) to 
    the specification file. A workflow can be used with many 
    filesets and subscriptions (e.g. repeating the same task on a 
    bunch of data).
    
    workflow + fileset = subscription
    """
    def __init__(self, spec = None, owner = None, name = None, id = -1):
        WMBSBase.__init__(self)
        WMWorkflow.__init__(self, spec = spec, owner = owner, name = name)

        self.id = id
        return
        
    def exists(self):
        """
        _exists_

        Determine whether or not a workflow exists with the given spec, owner
        and name.  Return the ID if the workflow exists, False otherwise.
        """
        action = self.daofactory(classname = "Workflow.Exists")
        result = action.execute(spec = self.spec, owner = self.owner,
                                name = self.name, conn = self.getDBConn(),
                                transaction = self.existingTransaction())
    
        return result

    def create(self):
        """
        _create_

        Write the workflow to the database.  If the workflow already exists in
        the database nothing will happen.
        """
        existingTransaction = self.beginTransaction()

        self.id = self.exists()

        if self.id != False:
            self.load()
            return
        
        action = self.daofactory(classname = "Workflow.New")
        action.execute(spec = self.spec, owner = self.owner, name = self.name,
                       conn = self.getDBConn(),
                       transaction = self.existingTransaction())
        
        self.id = self.exists()
        self.commitTransaction(existingTransaction)
        return
    
    def delete(self):
        """
        _delete_

        Remove this workflow from the database.
        """
        action = self.daofactory(classname = "Workflow.Delete")
        action.execute(id = self.id, conn = self.getDBConn(),
                       transaction = self.existingTransaction())

        return
        
    def load(self):
        """
        _load_

        Load a workflow from WMBS.  One of the following must be provided:
          - The workflow ID
          - The workflow name
          - The workflow spec and owner
        """
        existingTransaction = self.beginTransaction()

        if self.id > 0:
            action = self.daofactory(classname = "Workflow.LoadFromID")
            result = action.execute(workflow = self.id,
                                    conn = self.getDBConn(),
                                    transaction = self.existingTransaction())
        elif self.name != None:
            action = self.daofactory(classname = "Workflow.LoadFromName")
            result = action.execute(workflow = self.name,
                                    conn = self.getDBConn(),
                                    transaction = self.existingTransaction())
        else:
            action = self.daofactory(classname = "Workflow.LoadFromSpecOwner")
            result = action.execute(spec = self.spec, owner = self.owner,
                                    conn = self.getDBConn(),
                                    transaction = self.existingTransaction())

        self.id = result["id"]
        self.spec = result["spec"]
        self.name = result["name"]
        self.owner = result["owner"]

        action = self.daofactory(classname = "Workflow.LoadOutput")
        results = action.execute(workflow = self.id, conn = self.getDBConn(),
                                transaction = self.existingTransaction())

        for result in results:
            outputFileset = Fileset(id = result["output_fileset"])
            self.outputMap[result["output_identifier"]] = outputFileset
            
        self.commitTransaction(existingTransaction)
        return

    def addOutput(self, outputIdentifier, outputFileset):
        """
        _addOutput_

        Associate an output of this workflow with a particular fileset.
        """
        existingTransaction = self.beginTransaction()

        if self.id == False:
            self.create()
        
        self.outputMap[outputIdentifier] = outputFileset
        
        action = self.daofactory(classname = "Workflow.InsertOutput")
        action.execute(workflowID = self.id, outputIdentifier = outputIdentifier,
                       filesetID = outputFileset.id, conn = self.getDBConn(),
                       transaction = self.existingTransaction())
        
        self.commitTransaction(existingTransaction)
        return
