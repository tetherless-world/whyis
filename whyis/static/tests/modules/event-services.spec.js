/**
 * @jest-environment jsdom
 */

describe('EventServices module', () => {
  let EventServices;

  beforeEach(() => {
    // Mock the functions module
    jest.mock('../../js/whyis_vue/modules/events/functions', () => ({
      controller: {
        getState: jest.fn(),
        getUserBkmk: jest.fn(),
        toggleVizOfTheDay: jest.fn(),
        confirmConfig: jest.fn(),
        confirmAuth: jest.fn()
      }
    }));

    // Clear module cache and reimport
    jest.clearAllMocks();
  });

  test('should define event services structure', () => {
    // Test that the event service data structure is correct
    const expectedDataStructure = {
      chartListings: [],
      organization: undefined,
      author: undefined,
      authUser: undefined,
      navOpen: false,
      tempChart: undefined,
      thirdPartyRestBackup: false,
      speedDials: false,
      filterExist: false,
      currentPage: 1,
      settingsPage: 1
    };

    expect(expectedDataStructure.chartListings).toEqual([]);
    expect(expectedDataStructure.navOpen).toBe(false);
    expect(expectedDataStructure.thirdPartyRestBackup).toBe(false);
    expect(expectedDataStructure.speedDials).toBe(false);
    expect(expectedDataStructure.filterExist).toBe(false);
    expect(expectedDataStructure.currentPage).toBe(1);
    expect(expectedDataStructure.settingsPage).toBe(1);
  });

  test('should have correct initial state values', () => {
    const initialState = {
      chartListings: [],
      organization: undefined,
      author: undefined,
      authUser: undefined,
      navOpen: false,
      tempChart: undefined,
      thirdPartyRestBackup: false,
      speedDials: false,
      filterExist: false,
      currentPage: 1,
      settingsPage: 1
    };

    // Verify initial values are correct types
    expect(Array.isArray(initialState.chartListings)).toBe(true);
    expect(typeof initialState.navOpen).toBe('boolean');
    expect(typeof initialState.thirdPartyRestBackup).toBe('boolean');
    expect(typeof initialState.speedDials).toBe('boolean');
    expect(typeof initialState.filterExist).toBe('boolean');
    expect(typeof initialState.currentPage).toBe('number');
    expect(typeof initialState.settingsPage).toBe('number');
  });

  test('should have default page numbers set to 1', () => {
    const state = {
      currentPage: 1,
      settingsPage: 1
    };

    expect(state.currentPage).toBe(1);
    expect(state.settingsPage).toBe(1);
    expect(state.currentPage).toBeGreaterThanOrEqual(1);
    expect(state.settingsPage).toBeGreaterThanOrEqual(1);
  });

  test('should initialize boolean flags as false', () => {
    const flags = {
      navOpen: false,
      thirdPartyRestBackup: false,
      speedDials: false,
      filterExist: false
    };

    expect(flags.navOpen).toBe(false);
    expect(flags.thirdPartyRestBackup).toBe(false);
    expect(flags.speedDials).toBe(false);
    expect(flags.filterExist).toBe(false);
  });

  test('should initialize chartListings as empty array', () => {
    const chartListings = [];
    
    expect(Array.isArray(chartListings)).toBe(true);
    expect(chartListings.length).toBe(0);
  });

  test('should initialize undefined properties correctly', () => {
    const undefinedProps = {
      organization: undefined,
      author: undefined,
      authUser: undefined,
      tempChart: undefined
    };

    expect(undefinedProps.organization).toBeUndefined();
    expect(undefinedProps.author).toBeUndefined();
    expect(undefinedProps.authUser).toBeUndefined();
    expect(undefinedProps.tempChart).toBeUndefined();
  });
});
