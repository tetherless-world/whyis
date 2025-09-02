/**
 * Autocomplete menu utilities for UI components.
 * Provides functions for styling autocomplete menus and fetching author/organization data.
 * 
 * @module autocomplete-menu
 */

import axios from 'axios'

/**
 * Reformats and styles the Material Design autocomplete menu for better display
 * @param {*} param - Unused parameter (kept for compatibility)
 * @returns {boolean} True if the menu was successfully processed
 * @example
 * processAutocompleteMenu(); // Applies styling to visible autocomplete menus
 */
function processAutocompleteMenu (param) {
    const itemListContainer = document.getElementsByClassName("md-menu-content-bottom-start")
    if(itemListContainer.length >= 1) {
        itemListContainer[0].style['z-index'] = 12;
        itemListContainer[0].style['width'] = "75%";
        itemListContainer[0].style['max-width'] = "75%";
        return status = true
    }
  }

/**
 * Fetches a list of authors/persons matching the given query from both FOAF and Schema.org types
 * @param {string} query - The search query for author names
 * @returns {Promise<Array>} Array of author objects sorted by relevance score
 * @throws {Error} If the API request fails
 * @example
 * const authors = await getAuthorList('john smith');
 * // Returns combined results from FOAF Person and Schema.org Person types
 */
async function getAuthorList (query) { 
    // Until the resolver allows for OR operator, must run two gets to capture both person types
    const [foafRes, schemaRes] = await axios.all([
        axios.get(
        `/?term=${query}*&view=resolve&type=http://xmlns.com/foaf/0.1/Person`),
        axios.get(
        `/?term=${query}*&view=resolve&type=http://schema.org/Person`)
    ]).catch((err) => {
        throw(err)
    })
    var combinedList = foafRes.data.concat(schemaRes.data)
    .sort((a, b) => (a.score < b.score) ? 1 : -1);
    return combinedList
}

/**
 * Fetches a list of organizations matching the given query
 * @param {string} query - The search query for organization names
 * @returns {Promise<Array>} Array of organization objects from the API
 * @throws {Error} If the API request fails
 * @example
 * const orgs = await getOrganizationlist('university');
 * // Returns organizations matching the search term
 */
async function getOrganizationlist (query) {
    const orgList = await axios.get(
      `/?term=${query}*&view=resolve&type=http://schema.org/Organization`)
    return orgList.data
}

export { processAutocompleteMenu, getAuthorList, getOrganizationlist }
