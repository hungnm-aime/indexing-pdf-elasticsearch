
import base64
import json
from elasticsearch import Elasticsearch

elastic_client = Elasticsearch(hosts=["localhost"])


# make another Elasticsearch API request to get the indexed PDF
result = elastic_client.get(index="pdf", doc_type='_doc', id='112')

# print the data to terminal
result_data = result["_source"]["data"]
print ("\nresult_data:", result_data, '-- type:', type(result_data))


# decode the base64 data (use to [:] to slice off
# the 'b and ' in the string)
decoded_pdf = base64.b64decode(result_data[2:-1]).decode("utf-8")
print ("\ndecoded_pdf:", decoded_pdf)

# take decoded string and make into JSON object
json_dict = json.loads(decoded_pdf)
print ("\njson_str:", json_dict, "\nntype:", type(json_dict))