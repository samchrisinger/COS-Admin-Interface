'use strict';
var ko = require('knockout');
var $ = require('jquery');
var URI = require('URIjs');

/**
 * Generate OSF absolute URLs, including prefix and arguments. Assumes access to mako globals for pieces of URL.
 * Can optionally pass in an object with params (name:value) to be appended to URL. Calling as:
 *   apiV2Url('users/4urxt/applications',
 *      {query:
 *          {'a':1, 'filter[fullname]': 'lawrence'},
 *       prefix: 'https://staging2.osf.io/api/v2/'})
 * would yield the result:
 *  'https://staging2.osf.io/api/v2/users/4urxt/applications?a=1&filter%5Bfullname%5D=lawrence'
 * @param {String} path The string to be appended to the absolute base path, eg 'users/4urxt'
 * @param {Object} options (optional)
 */
var apiV2Url = function (path, options){
    var contextVars = window.contextVars || {};
    var defaultPrefix = contextVars.apiV2Prefix || '';

    var defaults = {
        prefix: defaultPrefix, // Manually specify the prefix for API routes (useful for testing)
        query: {}  // Optional query parameters to be appended to URL
    };
    var opts = $.extend({}, defaults, options);

    var apiUrl = URI(opts.prefix);
    var pathSegments = URI(path).segment();
    pathSegments.forEach(function(el){apiUrl.segment(el);});  // Hack to prevent double slashes when joining base + path
    apiUrl.query(opts.query);

    return apiUrl.toString();
};


/**
* Posts JSON data.
*
* NOTE: The `success` and `error` callbacks are deprecated. Prefer the Promise
* interface (using the `done` and `fail` methods of a jqXHR).
*
* Example:
*     var $osf = require('./osf-helpers');
*     var request = $osf.postJSON('/foo', {'email': 'bar@baz.com'});
*     request.done(function(response) {
*         // ...
*     })
*     request.fail(function(xhr, textStatus, err) {
*         // ...
*     }
*
* @param  {String} url  The url to post to
* @param  {Object} data JSON data to send to the endpoint
* @return {jQuery xhr}
*/
var postJSON = function(url, data, success, error) {
    var ajaxOpts = {
        url: url, type: 'post',
        data: JSON.stringify(data),
        contentType: 'application/json', dataType: 'json'
    };
    // For backwards compatibility. Prefer the Promise interface to these callbacks.
    if (typeof success === 'function') {
        ajaxOpts.success = success;
    }
    if (typeof error === 'function') {
        ajaxOpts.error = error;
    }
    return $.ajax(ajaxOpts);
};

/**
  * Puts JSON data.
  *
  * NOTE: The `success` and `error` callbacks are deprecated. Prefer the Promise
  * interface (using the `done` and `fail` methods of a jqXHR).
  *
  * Example:
  *     osf.putJSON('/foo', {'email': 'bar@baz.com'})
  *
  * @param  {String} url  The url to put to
  * @param  {Object} data JSON data to send to the endpoint
  * @return {jQuery xhr}
  */
var putJSON = function(url, data, success, error) {
    var ajaxOpts = {
        url: url, type: 'put',
        data: JSON.stringify(data),
        contentType: 'application/json', dataType: 'json'
    };
    // For backwards compatibility. Prefer the Promise interface to these callbacks.
    if (typeof success === 'function') {
        ajaxOpts.success = success;
    }
    if (typeof error === 'function') {
        ajaxOpts.error = error;
    }
    return $.ajax(ajaxOpts);
};

/**
* Set XHR Authentication
*
* Example:
*     var $osf = require('./osf-helpers');
*
*     JQuery
*     $ajax({
*         beforeSend: $osf.setXHRAuthorization,
*         // ...
*     }).done( ... );
*
*     MithrilJS
*     m.request({
*         config: $osf.setXHRAuthorization,
*         // ...
*     }).then( ... );
*
* @param  {Object} XML Http Request
* @return {Object} xhr
*/
var setXHRAuthorization = function (xhr) {
    if (window.contextVars.accessToken) {
        xhr.setRequestHeader('Authorization', 'Bearer ' + window.contextVars.accessToken);
    }
    return xhr;
};

//////////////////
// Data binders //
//////////////////

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

module.exports = window.$.osf = {
    postJSON: postJSON,
    putJSON: putJSON,
    setXHRAuthorization: setXHRAuthorization,
    apiV2Url: apiV2Url, 
    applyBindings: applyBindings,
 
};
