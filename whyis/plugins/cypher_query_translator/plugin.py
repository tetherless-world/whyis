from whyis.plugin import Plugin, Listener
import rdflib
from flask import current_app
import re
import json
from typing import Dict, List, Optional, Any, Union


class CypherQueryListener(Listener):
    """Listen for Cypher query events and translate them to SPARQL."""
    
    signals = ['on_cypher_query']
    
    def on_cypher_query(self, cypher_query: str, context: Optional[Dict] = None) -> str:
        """
        Translate a Cypher query to SPARQL and execute it.
        
        Args:
            cypher_query: The Cypher query string
            context: Optional JSON-LD context for URI mappings
            
        Returns:
            SPARQL query results as JSON
        """
        return []


class CypherToSparqlTranslator:
    """Core translator that converts Cypher queries to SPARQL."""
    
    def __init__(self, jsonld_context: Optional[Dict] = None):
        """
        Initialize the translator.
        
        Args:
            jsonld_context: JSON-LD context for URI mappings
        """
        self.context = jsonld_context or {}
        self.prefixes = {
            'rdf': rdflib.RDF,
            'rdfs': rdflib.RDFS,
            'owl': rdflib.OWL,
            'xsd': rdflib.XSD,
            'reif': rdflib.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
        }
        
    def expand_uri(self, term: str) -> str:
        """
        Expand a term using JSON-LD context.
        
        Args:
            term: The term to expand
            
        Returns:
            Expanded URI or the original term if no mapping found
        """
        if term in self.context:
            return self.context[term]
        elif ':' in term:
            prefix, local = term.split(':', 1)
            if prefix in self.context:
                return self.context[prefix] + local
        return term
        
    def translate(self, cypher_query: str) -> str:
        """
        Translate a Cypher query to SPARQL.
        
        Args:
            cypher_query: The Cypher query to translate
            
        Returns:
            The equivalent SPARQL query
        """
        # Normalize the query
        query = cypher_query.strip()
        
        # Parse different Cypher clauses
        match_clause = self._extract_match_clause(query)
        where_clause = self._extract_where_clause(query)
        return_clause = self._extract_return_clause(query)
        
        # Build SPARQL query
        sparql_query = self._build_sparql_query(match_clause, where_clause, return_clause)
        
        return sparql_query
        
    def _extract_match_clause(self, query: str) -> str:
        """Extract the MATCH clause from Cypher query."""
        match = re.search(r'MATCH\s+(.*?)(?:\s+WHERE|\s+RETURN|$)', query, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
        
    def _extract_where_clause(self, query: str) -> str:
        """Extract the WHERE clause from Cypher query."""
        match = re.search(r'WHERE\s+(.*?)(?:\s+RETURN|$)', query, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
        
    def _extract_return_clause(self, query: str) -> str:
        """Extract the RETURN clause from Cypher query."""
        match = re.search(r'RETURN\s+(.*?)$', query, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
        
    def _build_sparql_query(self, match_clause: str, where_clause: str, return_clause: str) -> str:
        """Build SPARQL query from parsed Cypher clauses."""
        
        # Start building SPARQL
        prefixes_str = "\n".join([f"PREFIX {prefix}: <{uri}>" for prefix, uri in self.prefixes.items()])
        
        select_vars = self._parse_return_clause(return_clause)
        where_patterns = self._parse_match_clause(match_clause)
        filter_conditions = self._parse_where_clause(where_clause)
        
        sparql_query = f"""
{prefixes_str}

SELECT {select_vars}
WHERE {{
    {where_patterns}
    {filter_conditions}
}}
"""
        
        return sparql_query.strip()
        
    def _parse_return_clause(self, return_clause: str) -> str:
        """Parse Cypher RETURN clause to SPARQL SELECT."""
        if not return_clause:
            return "*"
            
        # Split on commas and clean up variable names
        vars_list = []
        for var in return_clause.split(','):
            var = var.strip()
            # Handle property access like n.name
            if '.' in var:
                var_parts = var.split('.')
                var_name = f"?{var_parts[0]}_{var_parts[1]}"
            else:
                var_name = f"?{var}" if not var.startswith('?') else var
            vars_list.append(var_name)
            
        return " ".join(vars_list)
        
    def _parse_match_clause(self, match_clause: str) -> str:
        """Parse Cypher MATCH clause to SPARQL WHERE patterns."""
        if not match_clause:
            return ""
            
        patterns = []
        
        # Parse node patterns: (n:Label) or (n)
        node_pattern = r'\(([^)]+)\)'
        nodes = re.findall(node_pattern, match_clause)
        
        for node in nodes:
            parts = node.split(':')
            var_name = parts[0].strip()
            
            if len(parts) > 1:  # Has type
                label = parts[1].strip()
                expanded_type = self.expand_uri(label)
                patterns.append(f"?{var_name} rdf:type <{expanded_type}> .")
            else:
                # Just ensure the variable exists
                patterns.append(f"?{var_name} ?p{var_name} ?o{var_name} .")
        
        # Parse relationship patterns: -[:REL]-> or -[r:REL]->
        rel_pattern = r'-\[([^\]]*)\]->'
        relationships = re.findall(rel_pattern, match_clause)
        
        # Parse property patterns with reification support
        prop_patterns = self._parse_property_patterns(match_clause)
        patterns.extend(prop_patterns)
        
        return "\n    ".join(patterns)
        
    def _parse_property_patterns(self, match_clause: str) -> List[str]:
        """Parse property patterns and create reification statements if needed."""
        patterns = []
        
        # Look for property patterns like {name: "value"}
        prop_pattern = r'\{([^}]+)\}'
        property_groups = re.findall(prop_pattern, match_clause)
        
        for prop_group in property_groups:
            # Parse individual properties
            props = prop_group.split(',')
            for prop in props:
                if ':' in prop:
                    key, value = prop.split(':', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    
                    # Create reification pattern for property statements
                    expanded_prop = self.expand_uri(key)
                    patterns.extend([
                        f"?stmt rdf:type rdf:Statement .",
                        f"?stmt rdf:subject ?s .",
                        f"?stmt rdf:predicate <{expanded_prop}> .",
                        f"?stmt rdf:object \"{value}\" ."
                    ])
                    
        return patterns
        
    def _parse_where_clause(self, where_clause: str) -> str:
        """Parse Cypher WHERE clause to SPARQL FILTER."""
        if not where_clause:
            return ""
            
        # Simple property filters
        filters = []
        
        # Handle property equality: n.name = "value"
        prop_eq_pattern = r'(\w+)\.(\w+)\s*=\s*["\']([^"\']+)["\']'
        prop_matches = re.findall(prop_eq_pattern, where_clause)
        
        for var, prop, value in prop_matches:
            filters.append(f'FILTER(?{var}_{prop} = "{value}")')
            
        return "\n    ".join(filters)


class CypherQueryResolver(CypherQueryListener):
    """Concrete implementation of Cypher query resolution."""
    
    def __init__(self, database: str = "knowledge", jsonld_context: Optional[Dict] = None):
        """
        Initialize the resolver.
        
        Args:
            database: Database name to query against
            jsonld_context: JSON-LD context for URI mappings
        """
        self.database = database
        self.translator = CypherToSparqlTranslator(jsonld_context)
        
    def on_cypher_query(self, cypher_query: str, context: Optional[Dict] = None) -> List[Dict]:
        """
        Execute a Cypher query by translating it to SPARQL.
        
        Args:
            cypher_query: The Cypher query string
            context: Optional JSON-LD context for URI mappings
            
        Returns:
            Query results as list of dictionaries
        """
        try:
            # Update context if provided
            if context:
                self.translator.context.update(context)
                
            # Translate to SPARQL
            sparql_query = self.translator.translate(cypher_query)
            
            # Execute against the graph
            graph = current_app.databases[self.database]
            results = []
            
            for hit in graph.query(sparql_query):
                result = hit.asdict() if hasattr(hit, 'asdict') else dict(hit)
                results.append(result)
                
            return results
            
        except Exception as e:
            current_app.logger.error(f"Error executing Cypher query: {e}")
            return []


class CypherQueryPlugin(Plugin):
    """Main plugin class for Cypher query translation."""
    
    def __init__(self):
        super().__init__()
        # Import blueprint here to avoid circular imports
        from .blueprint.cql_blueprint import cql_blueprint
        self.blueprint = cql_blueprint
    
    def init(self):
        """Initialize the plugin with configuration."""
        # Get configuration
        cypher_db = self.app.config.get('CYPHER_DB', 'knowledge')
        cypher_context = self.app.config.get('CYPHER_JSONLD_CONTEXT', {})
        
        # Create and register resolver
        resolver = CypherQueryResolver(cypher_db, cypher_context)
        self.app.add_listener(resolver)
        
        # The blueprint will be registered automatically by the plugin system