## HƯỚNG DẪN INDEXING FILE PDF VÀO ELASTICSEARCH (ES)
*Project hướng dẫn đánh chỉ mục các file pdf vào elasticsearch*

### Yêu cầu cài đặt:
* python 3
* ElasticSearch
* kibana (option)
* cài đặt các thư viện python trong requirements.txt


### Hướng dẫn cài đặt ES và kibana

* Cài đặt ES version 6.8 sử dụng brew, mở terminal và chạy các command sau:
```bash
brew update
brew install elasticsearch@6.8
```

* Cài đặt kibana (Có thể không cần cài đặt)
Chú ý cài kibana version cần tương thích với elasticsearch. Cụ thể cài đặt kibana 6.8.3

```bash
brew update
brew install kibana@6.8
```

**Sau khi cài đặt xong es và kibana. Tắt terminal và mở lại.**     
Kiểm tra đường dẫn đã cài đặt:
```bash
which kibana
which elasticsearch
```

- Kiểm tra version:

```bash
kibana --version
elasticsearch -version

```

### Kiến trúc indexing pdf vào ES

![Kiến trúc mô hình indexing pdf file vào ES](/images/indexing_pdf.png)


### Ingest Attachment Processor Plugin
#### Cài đặt
```bash
sudo /usr/local/bin/elasticsearch-plugin install ingest-attachment
```
Note: trong trường hợp không biết đường dẫn của elasticsearch-plugin. 
Gõ câu lệnh sau để tìm đường dẫn tới nó:
```bash
which elasticsearch
```

elasticsearch-plugin và elasticsearch nằm cùng nơi.

* Ingest Attachment Processor Plugin là gì?
 Nó để cho ES trích xuất các attachments của file trong các format phổ biến
(như **PPT**, **XLS**, **PDF**) bằng cách sử dụng thư viện **Taka** của Apache
để detect và extract text, metadata từ các kiểu khác nhau (PDF, PPT, XLS ...)

#### Attachment Processor in a Pipeline
Tạo 1 attachment pipeline và extract các thông tin đã bị encode.
```bash
curl -XPUT 'ES_HOST:ES_PORT/_ingest/pipeline/attachment?pretty' -H 'Content-Type: application/json' -d '{
 "description" : "Extract attachment information encoded in Base64 with UTF-8 charset",
 "processors" : [
   {
     "attachment" : {
       "field" : "data"
     }
   }
 ]
}'
```

Tiếp theo thử index 1 document:

```bash
curl -XPUT 'ES_HOST:ES_PORT/test_index/test_type/test_id?pipeline=attachment&pretty' -H 'Content-Type: application/json' -d '{
 "data": "UWJveCBlbmFibGVzIGxhdW5jaGluZyBzdXBwb3J0ZWQsIGZ1bGx5LW1hbmFnZWQsIFJFU1RmdWwgRWxhc3RpY3NlYXJjaCBTZXJ2aWNlIGluc3RhbnRseS4g"
}'
```

Sau đó get data đã index:

```bash
curl -XGET 'ES_HOST:ES_PORT/test_index/test_type/test_id?pretty'
```

response trả về:

```
{
 "_index" : "test_index",
 "_type" : "test_type",
 "_id" : "test_id",
 "_version" : 1,
 "found" : true,
 "_source" : {
   "data" : "UWJveCBlbmFibGVzIGxhdW5jaGluZyBzdXBwb3J0ZWQsIGZ1bGx5LW1hbmFnZWQsIFJFU1RmdWwgRWxhc3RpY3NlYXJjaCBTZXJ2aWNlIGluc3RhbnRseS4g",
   "attachment" : {
     "content_type" : "text/plain; charset=ISO-8859-1",
     "language" : "et",
     "content" : "Qbox enables launching supported, fully-managed, RESTful Elasticsearch Service instantly.",
     "content_length" : 91
   }
 }
}
```


### Indexing bằng client (python)

* Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

Theo như mô hình indexing trên hình thì trước tiên parse content từ file PDF.
Sau đó convert nó về dạng base64.

```python
import os
from utils.get_paths import PDF_PATH

# import libraries to help read and create PDF
import PyPDF2
from fpdf import FPDF
import base64
import json
# import the Elasticsearch low-level client library
from elasticsearch import Elasticsearch

# create a new client instance of Elasticsearch
elastic_client = Elasticsearch(hosts=["localhost"])
# create a new PDF object with FPDF
pdf = FPDF()


def get_pdfs(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.pdf' in file:
                files.append(os.path.join(r, file))
    return files


def index_pdf_2_es(path):
    # get the PDF path and read the file
    read_pdf = PyPDF2.PdfFileReader(path, strict=False)
    print(read_pdf)

    # get the read object's meta info
    pdf_meta = read_pdf.getDocumentInfo()

    # get the page numbers
    num = read_pdf.getNumPages()
    print("PDF pages:", num)

    # create a dictionary object for page data
    all_pages = {}

    # put meta data into a dict key
    all_pages["meta"] = {}

    # Use 'iteritems()` instead of 'items()' for Python 2
    for meta, value in pdf_meta.items():
        print(meta, value)
        all_pages["meta"][meta] = value

    # iterate the page numbers
    for page in range(num):
        data = read_pdf.getPage(page)
        # page_mode = read_pdf.getPageMode()

        # extract the page's text
        page_text = data.extractText()

        # put the text data into the dict
        all_pages[page] = page_text
        print("page: ", page)
        print(page_text)

    # create a JSON string from the dictionary
    json_data = json.dumps(all_pages)
    print("\nJSON:", json_data)
    bytes_string = bytes(json_data, 'utf-8')
    print("\nbytes_string:", bytes_string)

    # convert bytes to base64 encoded string
    encoded_pdf = base64.b64encode(bytes_string)
    encoded_pdf = str(encoded_pdf)
    print("\nbase64:", encoded_pdf)

    body_doc = {"data": encoded_pdf}
```


* Tiếp theo cần indexing tới ES:

```
# call the index() method to index the data, if no pass id then id automatically generated
result = elastic_client.index(index="pdf", doc_type="_doc",id=112,  body=body_doc)
print(result)
return encoded_pdf
```


* Query trong ES:
```python

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
```

* Query bằng kibana
```
GET /_search?pretty
{
    "query": {
        "match_all": {}
    }
}
```


* Query bằng terminal
```bash
curl -X GET "localhost:9200/_search?pretty" -H 'Content-Type: application/json' -d'
{
    "query": {
        "match_all": {}
    }
}
'
```

### Give me a star. Thank you!
