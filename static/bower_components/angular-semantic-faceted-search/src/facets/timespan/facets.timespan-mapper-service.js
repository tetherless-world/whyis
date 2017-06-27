(function() {
    'use strict';

    angular.module('seco.facetedSearch')

    .factory('timespanMapperService', timespanMapperService);

    /* ngInject */
    function timespanMapperService(_, objectMapperService) {
        TimespanMapper.prototype.makeObject = makeObject;
        TimespanMapper.prototype.parseValue = parseValue;

        var proto = Object.getPrototypeOf(objectMapperService);
        TimespanMapper.prototype = angular.extend({}, proto, TimespanMapper.prototype);

        return new TimespanMapper();

        function TimespanMapper() {
            this.objectClass = Object;
        }

        function makeObject(obj) {
            var o = new this.objectClass();

            o.min = parseValue(_.get(obj, 'min.value'));
            o.max = parseValue(_.get(obj, 'max.value'));

            return o;
        }

        function parseValue(value) {
            if (!value) {
                return undefined;
            }
            var d = _(value.substring(0, 10).split('-')).map(function(d) { return parseInt(d, 10); }).value();
            return new Date(d[0], d[1]-1, d[2]);
        }
    }
})();
