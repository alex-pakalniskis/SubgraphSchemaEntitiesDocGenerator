import requests
from typing import List
import re
import sys

class DocumentationGenerator:
  """Utility to generate Markdown documentation for Subgraph Entities
  
  Parameters:
    ipfs_url: IPFS URL that hosts the schema.graphql file

  Attributes:
    self.schema: GraphQL schema text, split on "type " substring
    self.entities: 
    self.entities_fields: 
    self.markdown: 
    """
  def __init__(self, ipfs_url: str):
    self.ipfs_url = ipfs_url
    self.entities = []
    self.entities_fields = dict()
    self.markdown = "# Subgraph Entities\n"
  
  def get_schema_data(self) -> None:
    """Download the GraphQL schema from IPFS into self.schema instance attribute. The schema defines what data is stored in the subgraph and how to query it via GraphQL.
    """
    r = requests.get(self.ipfs_url)
    self.schema = r.text
  
  def remove_comments_from_schema(self) -> None:
    """Removes comments from graphql.schema"""
    self.schema_no_desc = re.sub('".*?"', '', self.schema)
    self.schema_no_desc = re.sub('#.*?\n', '', self.schema_no_desc)
  
  def get_entities(self) -> None:
    """Parse self.schema GraphQL schema text for entities defined within.
    Stores entities found within GraphQL schema in self.entities instance attribute
    """
    for entry in self.schema_no_desc.split("type "):
      if "@entity" not in entry:
        pass
      elif entry != '':
        self.entities.append(entry.split(" ")[0])
    
 
def get_fields(entity, schema):
    """Parse a GraphQL schema for the fields contained within a given entity
    
    Args:
        entity: GraphQL schema entity
        schema: GraphQL schema
    
    Returns:
        Markdown table of fields, types, and placeholders for description.""" 
    data = schema.split(f"type {entity} ")[1]
    fields = data.split("{")[1].split("}")[0]
    fields = fields.split("\n")
    clean_fields = []
    for f in fields:
        f = f.strip()
        if f != "":
            clean_fields.append(f)
        
    markdown_table = ""

    for cf in clean_fields:
        split = cf.split(": ")
        field = split[0]
        type = split[1].split(" ")[0]


        if "!]!" in type:
            type = type.replace("!]!", f"!](#{type.lower().replace('!', '').replace('[', '').replace(']', '')})")
        elif "!]" in type:
            type = type.replace("!]", f"!](#{type.lower().replace('!', '').replace('[', '').replace(']', '')})")


        if "@derivedFrom" in field:
            pass
        else:
            markdown_table += f"| {field} | {type} | ... | \n"

    return markdown_table

if __name__ == "__main__":
    protocol_name = sys.argv[1]
    protocol_schema = f"https://ipfs.io/ipfs/{sys.argv[2]}"

    prog = DocumentationGenerator(protocol_schema)
    prog.get_schema_data()
    prog.remove_comments_from_schema()
    prog.get_entities()

    markdown = "# Subgraph Entities\n\n"

    for elem in prog.entities:
        markdown += f"* [{elem}](#{elem.lower()})\n"
    markdown += "\n\n"

    for elem in prog.entities:
        markdown += f"## {elem}\n"
        markdown += f"| Field | Type | Description | \n"
        markdown += f"| --- | --- | --- | \n"
        markdown += get_fields(elem, prog.schema_no_desc)
    
    with open(f"{protocol_name}_Subgraph_Entities.md", "w") as f:
        f.write(markdown)
