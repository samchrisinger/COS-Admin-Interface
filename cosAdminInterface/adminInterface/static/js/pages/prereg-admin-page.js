'use strict';

//var $osf = require('../osfHelpers');
var ko = require('knockout');
var $ = require('jquery');

var drafts;

/**
  * A thin wrapper around ko.applyBindings that ensures that a view model
  * is bound to the expected element. Also shows the element (and child elements) if it was
  * previously hidden by applying the 'scripted' CSS class.
  *
  * Takes a ViewModel and a selector (string) or a DOM element.
  */
var applyBindings = function(viewModel, selector) {
    var elem, cssSelector;
    var $elem = $(selector);
    if (typeof(selector.nodeName) === 'string') { // dom element
        elem = selector;
        // NOTE: Only works with DOM elements that have an ID
        cssSelector = '#' + elem.id;
    } else {
        elem = $elem[0];
        cssSelector = selector;
    }
    if ($elem.length === 0) {
        throw "No elements matching selector '" + selector + "'";  // jshint ignore: line
    }
    if ($elem.length > 1) {
        throw "Can't bind ViewModel to multiple elements."; // jshint ignore: line
    }
    // Ensure that the bound element is shown
    if ($elem.hasClass('scripted')){
        $elem.show();
    }
    // Also show any child elements that have the scripted class
    $(cssSelector + ' .scripted').each(function(elm) {
        $(this).show();
    });
    ko.applyBindings(viewModel, $elem[0]);
};

ko.bindingHandlers.enterkey = {
    init: function (element, valueAccessor, allBindings, viewModel) {
        var callback = valueAccessor();
        $(element).keypress(function (event) {
            var keyCode = (event.which ? event.which : event.keyCode);
            if (keyCode === 13) {
                callback.call(viewModel);
                return false;
            }
            return true;
        });
    }
};

var CommentsSent = function() {
    var self = this;
    self.edit = ko.observable(false);
    self.commentsSent = ko.observable('no');
};

CommentsSent.prototype.enlargeIcon = function(data, event) {
    var icon = event.currentTarget;
    $(icon).addClass("fa-2x");
};

CommentsSent.prototype.shrinkIcon = function(data, event) {
    var icon = event.currentTarget;
    $(icon).removeClass("fa-2x");
};
CommentsSent.prototype.editItem = function() {
    var self = this;
    self.commentsSent.edit(true);
};

CommentsSent.prototype.stopEditing = function() {
    var self = this;
    self.commentsSent.edit(false);
};

var ProofOfPub = function() {
    var self = this;
    self.edit = ko.observable(false);
    self.proofOfPub = ko.observable('no');
};

ProofOfPub.prototype.enlargeIcon = function(data, event) {
    var icon = event.currentTarget;
    $(icon).addClass("fa-2x");
};

ProofOfPub.prototype.shrinkIcon = function(data, event) {
    var icon = event.currentTarget;
    $(icon).removeClass("fa-2x");
};
ProofOfPub.prototype.editItem = function() {
    var self = this;
    self.proofOfPub.edit(true);
};

ProofOfPub.prototype.stopEditing = function() {
    var self = this;
    self.proofOfPub.edit(false);
};

var PaymentSent = function() {
    var self = this;
    self.edit = ko.observable(false);
    self.paymentSent = ko.observable('no');
};

PaymentSent.prototype.enlargeIcon = function(data, event) {
    var icon = event.currentTarget;
    $(icon).addClass("fa-2x");
};

PaymentSent.prototype.shrinkIcon = function(data, event) {
    var icon = event.currentTarget;
    $(icon).removeClass("fa-2x");
};
PaymentSent.prototype.editItem = function() {
    var self = this;
    self.paymentSent.edit(true);
};

PaymentSent.prototype.stopEditing = function() {
    var self = this;
    self.paymentSent.edit(false);
};

var Notes = function() {
    var self = this;
    self.edit = ko.observable(false);
    self.notes = ko.observable('none');
};

Notes.prototype.enlargeIcon = function(data, event) {
    var icon = event.currentTarget;
    $(icon).addClass("fa-2x");
};

Notes.prototype.shrinkIcon = function(data, event) {
    var icon = event.currentTarget;
    $(icon).removeClass("fa-2x");
};
Notes.prototype.editItem = function() {
    var self = this;
    self.notes.edit(true);
};

Notes.prototype.stopEditing = function() {
    var self = this;
    self.notes.edit(false);
};

var Row = function(params) {
    var self = this;

    // TODO change default
    self.editing = ko.observable(true);

    self.title = params.registration_metadata.q1.value;
    self.fullname = params.initiator.fullname;
    self.username = params.initiator.username;
    self.initiated = self.formatTime(params.initiated);
    self.updated = self.formatTime(params.updated);
    self.commentsSent = new CommentsSent();

    //variables for editing items in row    
    self.proofOfPub = new ProofOfPub();
    self.paymentSent = new PaymentSent();
    self.notes = new Notes();
};


Row.prototype.highlightRow = function(data, event) {  
    var row = event.currentTarget;
    $(row).css("background","#E0EBF3"); 
};

Row.prototype.unhighlightRow = function(data, event) {
    var row = event.currentTarget;
    $(row).css("background",""); 
};

Row.prototype.formatTime = function(time) {
    var parsedTime = time.split(".");
    return parsedTime[0]; 
};

Row.prototype.goToDraft = function(data, event) {
    var self = this;
    if (self.editing() === false) {
        var path = "/project/" + data.branched_from.node.id + "/draft/" + data.pk;
        location.href = path;
    }
};

var AdminView = function(adminSelector) {
    var self = this;

    self.adminSelector = adminSelector;

    self.getDrafts = $.getJSON.bind(null, "/get-drafts/");

    self.drafts = ko.observableArray();
    self.loading = ko.observable(true);

    self.sortedDrafts = ko.pureComputed(function() {
        var row = self.sortBy();
        return self.drafts().sort(function (left, right) { 
            var a = deep_value(left, row).toLowerCase();
            var b = deep_value(right, row).toLowerCase();
            return a == b ? 0 : 
                (a < b ? -1 : 1); 
        });
    }, this);

    self.sortBy = ko.observable('registration_metadata.q1.value');

    self.init();
}

AdminView.prototype.init = function() {
    var self = this;

    // '#prereg-row'
    applyBindings(self, self.adminSelector);

    var getDrafts = self.getDrafts();

    // create new view model for each row
    getDrafts.then(function(response) {
        self.drafts(
            $.map(response.drafts, function(draft){
                return new Row(draft);
            })
        );
    });

    $.when(getDrafts).then(function() {
        self.loading(false);
    });
}

AdminView.prototype.setSort = function(data, event) {
    self.sortBy(event.target.id);
};

$(document).ready(function() {
    var adminView = new AdminView('#prereg-row');
});

var deep_value = function(obj, path){
    for (var i=0, path=path.split('.'), len=path.length; i<len; i++){
        if (obj === undefined) {
            return "No title";
        }
        obj = obj[path[i]];
    };
    return obj;
};
