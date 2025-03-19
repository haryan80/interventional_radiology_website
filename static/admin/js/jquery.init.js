/*global django:true, jQuery:false*/
/* Puts the included jQuery into our own namespace using noConflict and passing
 * it to a function which will add some functionality and then assign jQuery
 * and $ to point to the Django jQuery namespace.
 */

var django = django || {};

django.jQuery = jQuery.noConflict(true);
var jQuery = django.jQuery;
var $ = django.jQuery;