var app = angular.module('topics', []);
app.controller('topicCtrl', function($scope, $http) {
  $scope.topics = getTopics();

  function getTopics(){
    var endpoint = "http://localhost:9999/bigdata/sparql";
    var query = "prefix dc: <http://purl.org/dc/terms/>\
                  select DISTINCT ?o {\
                  ?p <http://www.w3.org/ns/dcat#keyword>  ?o\
                }";

      $http.get(endpoint+"?format=json&query="+encodeURIComponent(query))
      .then(function(response) {
          var topics = [];
          var data = response.data.results.bindings;
          for(var i = 0; i < data.length; i++){
            topics.push(data[i].o.value);
          }
          console.log(topics);
          return topics;
      });
    }

});
