import axios from 'axios'

// Reformat the auto-complete menu
function processAutocompleteMenu (param) {
    var runSetStyle;
    if(param){
      if(runSetStyle){
        return clearInterval(runSetStyle);
      }
    }
    runSetStyle = setInterval(() => {
      const itemListContainer = document.getElementsByClassName("md-menu-content-bottom-start")
      if(itemListContainer.length >= 1) {
        itemListContainer[0].setAttribute("style", "width: 90%; max-width: 90%; position: absolute; top: 841px; left: 95px; will-change: top, left;")
        return status = true
      }
    }, 20)
    return runSetStyle
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

async function getTypeList (query) {
  const allTypes = await axios.get(
    `/about?type=http://www.w3.org/2002/07/owl%23Class&view=resolve&term=${query}*`
  )
  return allTypes.data
}

export default async function getSuggestedTypes (uri){
  const suggestedTypes = await axios.get(
    `/about?view=suggested_types&uri=${uri}`)
  return suggestedTypes.data
}

export { processAutocompleteMenu, getAuthorList, getOrganizationlist, getTypeList, getSuggestedTypes}
