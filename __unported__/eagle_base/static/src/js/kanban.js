openerp.eagle_base = function (instance) {

//    openerp.web_kanban.KanbanRecord.include({

instance.eagle_base = instance.web_kanban.KanbanRecord.extend({
    template: 'KanbanView.record',
    init: function (parent, record) {
        this._super(parent);
    },
    object_read: function(model, fields, id) {
            var self = this;
            var dataset = new openerp.web.DataSet(self, model, self.session.context, id);
            dataset.read_ids([id], fields).done(function(result) {
                return result;
            });
            return "";
        }
    });

};

// vim:et fdc=0 fdl=0 foldnestmax=3 fdm=syntax:
