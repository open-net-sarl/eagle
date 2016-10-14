Open Net Eagle View System: Project module
==========================================

This is the projects module of the Eagle View management system

**Features list :**
	- introduces the accounting management
    - links the contract to:
        - sales
        - invoices
        - sale susbriptions
	- all these elements have their own tab
    - default analytic account for all the subscription of an Eagle file

**Author :** 

.. image:: http://open-net.ch/logo.png
   :alt: Open Net Sàrl
   :target: http://open-net.ch

Industrie 59  
CH-1030 Bussigny 
http://www.open-net.ch

http://www.open-net.ch
info@open-net.ch

**History :**

V9.0: 2016-05
    * Upgrade to Odoo V9

V9.2: 2016-09-19/Cyp
    * Sale subscription line in an Eagle form: now edition stands in a full form
    * Assets management
    * Generating a sale/invoice now fully refreshes the client window to reflect the corresp. changes
    * Button from analytic account to leads now points to a list instead of the form
    * Analytic accounts list now filtered by customer in an Eagle form
    * Sale subscription may have their own name
    * Button from analytic account to sale susbscriptions now points to a list instead of the form
    * Removed fields in an Eagle form: sale subscription line's sequence and actual quantity
    * New dependency: sale_timesheet
    * New: timesheet button hidden in sale order form (linked to the analytic account instead of only the sale)
    * Correction: now displays three qty fields in sale order line when coming from an Eagle file
