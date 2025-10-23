module.exports = {
  testEnvironment: 'jsdom',
  moduleFileExtensions: [
    'js',
    'json',
    'vue'
  ],
  transform: {
    '^.+\\.vue$': 'vue-jest',
    '^.+\\.js$': 'babel-jest'
  },
  transformIgnorePatterns: [
    '/node_modules/(?!(vue)/)'
  ],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/js/whyis_vue/$1',
    '\\.(css|less|scss|sass)$': '<rootDir>/tests/__mocks__/styleMock.js'
  },
  testMatch: [
    '**/tests/**/*.spec.js',
    '**/tests/**/*.test.js'
  ],
  collectCoverageFrom: [
    'js/whyis_vue/**/*.js',
    '!js/whyis_vue/**/*.vue',
    '!js/whyis_vue/main.js',
    '!js/whyis_vue/**/index.js',
    '!**/node_modules/**'
  ],
  coverageDirectory: '<rootDir>/coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testPathIgnorePatterns: ['/node_modules/', '/js/angular-openlayers-directive/', '/js/angular-semantic-faceted-search/']
};
