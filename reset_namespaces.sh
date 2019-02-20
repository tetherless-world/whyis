curl -X DELETE http://localhost:8080/blazegraph/namespace/knowledge
curl -X POST --data-binary @knowledge.properties -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace
rm -rf /data/nanopublications
rm -rf /data/files
#curl -X DELETE http://localhost:8080/blazegraph/namespace/admin
#curl -X POST --data-binary @admin.properties -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace
