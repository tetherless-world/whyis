
import { listNanopubs, postNewNanopub, describeNanopub, deleteNanopub, lodPrefix } from 'utilities/nanopub' 
import EventServices from '../modules/events/event-services'

const defaultContext= { 
    "dcat": "http://w3.org/ns/dcat#",
    "dct": "http://purl.org/dc/terms/",
    "vcard": "http://www.w3.org/2006/vcard/ns#",
    "foaf": "http://xmlns.com/foaf/0.1/",
        
    "name": "foaf:name",
    "contributor": "dct:contributor",         
    "organization": "foaf:Organization",
    "author": "dct:creator", 
    "person": "foaf:Person",
    "lastname":"foaf:lastname",
    "firstname":"foaf:firstname",
    "onbehalfof":"http://www.w3.org/ns/prov#actedOnBehalfOf", 
}

const defaultAgent = { 
    "@id": null,
    "@type": "http://xmlns.com/foaf/0.1/Agent",
    name: "", 
}

const defaultOrganization = {
    "@id": null,
    "@type": "http://xmlns.com/foaf/0.1/Organization",
    name: "", 
}

const defaultAuthor = {
    "@id": null,
    "@type": "http://xmlns.com/foaf/0.1/Person",
    name:"",
    lastname: "",
    firstname: "",
}

const foaf = "http://xmlns.com/foaf/0.1/"

const agentFieldUris = {
    name: `${foaf}name`,  
    organization: `${foaf}Organization`, 
    person: `${foaf}Person`, 
    onbehalfof: "http://www.w3.org/ns/prov#actedOnBehalfOf",
    lastname: `${foaf}lastname`,
    firstname: `${foaf}firstname`,
} 
 
const organizationPrefix = 'organization' 
const personPrefix = 'person'

function generateId (agentPrefix, orcid) {
  var agentId;
  if (arguments.length === 1) { 
    const { v4: uuidv4 } = require('uuid');
    agentId = uuidv4();
  } else {
    agentId = orcid;
  }
  return `${window.location.origin}/${agentPrefix}/${agentId}`
} 

function generateURI (agent, orcid) { 
  if (arguments.length === 1) { 
    const { v4: uuidv4 } = require('uuid');
    var agentId = uuidv4();
  } else {
    var agentId = orcid;
  }
  const name = agent.name.replace(/\s+/g, '');
  // return `${lodPrefix}/${agent.type}/${agent.lastname}${agent.firstname}/${agentId}`
  return `${lodPrefix}/${agent.type}/${name}/${agentId}`
}

function buildLd (agent) {
  agent = Object.assign({}, agent)
  // agent.context = JSON.stringify(agent.context)
  const agentLd =  {
    // '@context': defaultContext,
    '@id': agent.uri,
    '@type': `${foaf}${agent.type}`, 
  }

  Object.entries(agent)
    .filter(([field, value]) => agentFieldUris[field])
    .forEach(([field, value]) => agentLd[agentFieldUris[field]] = [{ '@value': value }]);

  console.log(agentLd) 
  return agentLd
}

function recursiveFieldSetter ([field, value]) { 
  var fieldDict = {} 
  for (var val in value) {  
    if (Array.isArray(value)){
      fieldDict[val] = recursiveFieldSetter([field, value[val]])
    } 
    else if ((val === '@type') || (val === '@value')){ 
      fieldDict[val] = value[val];
      if (agentFieldUris.hasOwnProperty(value[val])){
        fieldDict[val] = agentFieldUris[value[val]];
      }
    }
    else if (agentFieldUris.hasOwnProperty(val)){ 
      fieldDict[agentFieldUris[val]] = recursiveFieldSetter([agentFieldUris[val], value[val]]);
    } else {
      fieldDict['@value'] = value;
    }
  }
  return fieldDict
}

function getDefaultAgent (type) { 
    if (type === "organization"){
        return Object.assign({}, defaultOrganization)
    } else if (type === "author"){ 
        return Object.assign({}, defaultAuthor)
    } else {
        return Object.assign({}, defaultAgent)
    }
}

async function saveAgent (agent) {
  // let deletePromise = Promise.resolve()
  // if (agent.orcid) {
  //   deletePromise = deleteAgent(agent.orcid)
  //   agent.uri = generateURI(agent, agent.orcid) 
  // } else {
    agent.uri = generateURI(agent, agent['@id'])
  // } 
// }
  // } 
  const agentLd = buildLd(agent) 
  // await deletePromise
  try{
    console.log(agent.uri)
    agent['@id'] = agent.uri;
    return postNewNanopub(agentLd, defaultContext)
    .then(EventServices.author = agent)
  } catch(err){
    return alert(err)
  }
  
}

function deleteAgent (agentUri) { 
  return listNanopubs(agentUri)
    .then(nanopubs => {
      console.log("in delete")
      console.log(nanopub.np)
      Promise.all(nanopubs.map(nanopub => deleteNanopub(nanopub.np)))
    }
    )
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

export { getDefaultAgent, saveAgent, deleteAgent, processAutocompleteMenu}
