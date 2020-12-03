import axios from 'axios';

async function saveAgent (agent) {
  const regUnhyphenated = /^\d{16}$/
  const unhyphenated = regUnhyphenated.test(agent['@id']);
  if (unhyphenated){
    agent['@id'] = agent['@id'].replace(/^\(?([0-9]{4})\)?([0-9]{4})?([0-9]{4})?([0-9]{4})$/, "$1-$2-$3-$4")
  }
  const regHyphenated = /^\(?([0-9]{4})\)?[-]?([0-9]{4})[-]?([0-9]{4})[-]?([0-9]{4})$/;
  const validOrcid = regHyphenated.test(agent['@id']);

  // Get the data for this ORCID id through Whyis using view=describe
  if (validOrcid){
    const response = await axios.get(`/orcid/${agent['@id']}?view=describe`, {
      headers: {
        'Accept': 'application/ld+json',
      }
    })
    .then(response => { 
      let orcidAuth = response.data;
      return orcidAuth
    })
    .catch(err => { 
      throw err;
    }); 
  }
}

let run;

const processAutocompleteMenu = () => {
    run = setInterval(() => {
        const floatList = document.getElementsByClassName("md-menu-content-bottom-start")
        if(floatList.length >= 1) {
            floatList[0].setAttribute("style", "z-index:1000 !important; width: 80%; max-width: 80%; position: absolute; top: 644px; left:50%; transform:translateX(-50%); will-change: top, left;")
            return status = true
        }
    }, 40)

    return run
}

export { saveAgent, processAutocompleteMenu}
