'use strict';

module.exports = function(grunt) {

    grunt.initConfig({
        concat: {
            dist: {
                src: ['src/sparql.module.js',
                    'src/sparql.sparql-service.js',
                    'src/sparql.advanced-sparql-service.js',
                    'src/sparql.object-mapper-service.js',
                    'src/sparql.pager-service.js',
                    'src/sparql.query-builder-service.js'],
                dest: 'dist/sparql-service.js'
            }
        },
        ngdocs: {
            all: ['src/**/*.js'],
            options: {
                title: 'SPARQL Service'
            },
            sourceLink: true
        }
    });

    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-ngdocs');

    grunt.registerTask('build', ['concat:dist', 'ngdocs:all']);
};
