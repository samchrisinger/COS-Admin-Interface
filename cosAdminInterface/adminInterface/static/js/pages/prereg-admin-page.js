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

function adminView(data) {
    var self = this;
    self.data = data.drafts;

    self.drafts = ko.pureComputed(function() {
        var row = self.sortBy();
        return data.drafts.sort(function (left, right) { 
            var a = deep_value(left, row).toLowerCase();
            var b = deep_value(right, row).toLowerCase();
            return a == b ? 0 : 
                (a < b ? -1 : 1); 
        });
    }, this);
    self.sortBy = ko.observable('registration_metadata.q1.value');

    // variables for editing items in row
    self.edit = ko.observable(false);
    self.item = ko.observable();
    self.commentsSent = ko.observable('no');
    self.proofOfPub = ko.observable('no');
    self.paymentSent = ko.observable('no');
    self.notes = ko.observable('none');

    self.setSort = function(data, event) {
        self.sortBy(event.target.id);
    };

    self.highlightRow = function(data, event) {  
        var row = event.currentTarget;
        $(row).css("background","#E0EBF3"); 
    };

    self.unhighlightRow = function(data, event) {
        var row = event.currentTarget;
        $(row).css("background",""); 
    };

    self.formatTime = function(time) {
        var parsedTime = time.split(".");
        return parsedTime[0]; 
    };

    self.goToDraft = function(data, event) {
        if (self.edit() === false) {
            var path = "/project/" + data.branched_from.node.id + "/draft/" + data.pk;
            location.href = path;
        }
    };

    self.enlargeIcon = function(data, event) {
        var icon = event.currentTarget;
        $(icon).addClass("fa-2x");
    };

    self.shrinkIcon = function(data, event) {
        var icon = event.currentTarget;
        $(icon).removeClass("fa-2x");
    };

    self.editItem = function(item) {
        self.edit(true);
        $('.'+item).hide();
        $('.input_' + item).show();
        $('.input_' + item).focus();
    };

    self.stopEditing = function(item) {
        $('.'+item).show();
        $('.input_' + item).hide();
    };

}

$(document).ready(function() {
    // call to get drafts
    var test = '/get-drafts/';
    var request = $.ajax({
        url: test
    });
    request.done(function(data) {
        applyBindings(new adminView(data), '#prereg-row');
    });
    request.fail(function(xhr, textStatus, error) {
        console.log('Failed to populate data', {
            url: test,
            textStatus: textStatus,
            error: error
        });
    });
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
