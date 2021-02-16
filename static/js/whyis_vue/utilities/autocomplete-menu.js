import axios from 'axios'

// Reformat the auto-complete menu
function processAutocompleteMenu (param) {
    const itemListContainer = document.getElementsByClassName("md-menu-content-bottom-start")
    if(itemListContainer.length >= 1) {
        itemListContainer[0].style['z-index'] = 12;
        itemListContainer[0].style['width'] = "75%";
        itemListContainer[0].style['max-width'] = "75%";
        return status = true
    }
  }

// Auto-complete methods for author and institution
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

async function getOrganizationlist (query) {
    const orgList = await axios.get(
      `/?term=${query}*&view=resolve&type=http://schema.org/Organization`)
    return orgList.data
}

export { processAutocompleteMenu, getAuthorList, getOrganizationlist }
