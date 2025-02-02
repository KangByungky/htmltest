from django.urls import reverse
from django.test import TestCase, TransactionTestCase

from rest_framework.test import APITestCase, APITransactionTestCase
from rest_framework import status

from .models import UploadedCorpus, Task # type: ignore

#Verbose.

TESTSTRING0 = "A test string. Second sentence.\nNext paragraph. Another one.\n\nA paragraph after two newlines."
def get_orig_corpus(teststring=TESTSTRING0):
	return {
		"corpus": {
			"paragraphs": [],
			"paragraph_delimiters": [],
			"original_text": teststring,
			"p_div_locs": [],
			"task_ids": []
		}
	}

"""
### UploadTestCase
1. Upload a string, which goes:
```
A test string. Second sentence.\nNext paragraph. Another one.\n\nA paragraph after two newlines.
```
Since this endpoint requires `"corpus"`,
```json
{
	"corpus": {
		"paragraphs": [],
		"paragraph_delimiters": [],
		"original_text": "A test string. Second sentence.\nNext paragraph. Another one.\n\nA paragraph after two newlines.",
		"p_div_locs": [],
		"task_ids": []
	}
}
```
to `/upload`.
2. The server has to return `"corpus_id"`. Check if it is a valid one by checking `/api/v2/corpuses/<corpus_id>`.
"""
class UploadTestCase(APITestCase):
	def test_upload(self):
		url = reverse("api-upload")
		orignal_text = TESTSTRING0
		data = get_orig_corpus(orignal_text)

		response = self.client.post(url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(UploadedCorpus.objects.count(), 1)

		corpus_id = response.data["corpus_id"]
		corpuses_history = UploadedCorpus.objects.get().corpuses_history["corpuses_history"]
		self.assertEqual(corpuses_history[0]["original_text"], orignal_text)

		#Check the uploaded one
		url = reverse("api-corpuses-pk", args=[corpus_id])
		response = self.client.get(url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		returned_corpuses_history = response.data["corpuses_history"]
		self.assertEqual(returned_corpuses_history, corpuses_history)

"""
### DivideTestCase
1. Set up a data whose only filled is `original_text`.
2. Test `parser/divide`.
3. Test `parser/parse`.

For this test data, with `p_delim`
- For `['\n']`, `7` p's.
- A test string. Second sentence.
- \n
- Next paragraph. Another one.
- \n
- 
- \n
- A paragraph after two newlines.

## These are to be tested in another test code:
- For `['\n']`, `7` p's.
  - A test string. Second sentence.
  - \n
  - Next paragraph. Another one.
  - \n
  - 
  - \n
  - A paragraph after two newlines.
- For `['\n\n']`, `3` p's.
  - A test string. Second sentence.\nNext paragraph. Another one.
  - \n\n
  - A paragraph after two newlines.
- For `['\n\n', 'paragraph']`, `7` p's.
  - A test string. Second sentence.\nNext 
  - paragraph
  - . Another one.
  - \n\n
  - A 
  - paragraph
  -  after two newlines.
"""

class ParserTestCase(APITransactionTestCase):
	def test_divide_parse(self):
		#Upload
		original_text = TESTSTRING0
		url = reverse("api-upload")
		data = get_orig_corpus(original_text)
		response = self.client.post(url, data, format="json")
		corpus_id = response.data["corpus_id"]

		#Test /parse/divide
		url = reverse("api-parser-divide")
		p_delims = ['\n']
		data = {"corpus_id": corpus_id, "divide_options": {"p_delims": p_delims}}

		response = self.client.post(url, data, format="json")
		task_id = response.data["task_id"] #This is a parallel op...

		#Test /tasks/<pk>
		url = reverse("api-tasks-pk", args=[task_id])
		response = self.client.get(url, data, format="json")
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data["target_corpus_id"], corpus_id)
		self.assertIn(response.data["status"], ["RUNNING", "FINISHED"])

		#This snippet assumes that `Task` is parallelized, but works on the sequential code too
		import time
		timeout = 4
		start = time.time()
		while True:
			task = Task.objects.get(task_id=task_id)
			task_status = task.status
			if task_status == "FINISHED":
				break
			elif task_status != "RUNNING":
				raise RuntimeError(f"Unexpected status: {task_status}")

			if time.time() - start > timeout:
				raise RuntimeError("test_divide_one_newline: timeout")
			
		#Check if the UploadedCorpus is updated
		uc = UploadedCorpus.objects.get(corpus_id=corpus_id)
		self.assertEqual(uc.current_task, None)
		corpuses_history = uc.corpuses_history["corpuses_history"]
		self.assertEqual(len(corpuses_history), 2)
		
		last_corpus = corpuses_history[-1]
		self.assertEqual(last_corpus["paragraph_delimiters"], p_delims)
		#self.assertEqual(last_corpus["task_ids"][-1], task_id)
		self.assertEqual(len(last_corpus["paragraphs"]), 7)
		
		p0 = last_corpus["paragraphs"][0]
		self.assertEqual(p0["pstate"], "DIVIDED")
		self.assertEqual(p0["tokens"], [])
		self.assertFalse(p0["is_delimiter"])
		self.assertNotEqual(p0["original_text"], "")
		self.assertIsNotNone(p0["original_text"])

		#Test /parser/parse
		url = reverse("api-parser-parse")
		t_delims = None
		data = {"corpus_id": corpus_id, "parse_options": {"t_delims": t_delims}}

		response = self.client.post(url, data, format="json")
		task_id = response.data["task_id"]

		#Repeating the procedure above.
		timeout = 4
		start = time.time()
		while True:
			task = Task.objects.get(task_id=task_id)
			task_status = task.status
			if task_status == "FINISHED":
				break
			elif task_status != "RUNNING":
				raise RuntimeError(f"Unexpected status: {task_status}")

			if time.time() - start > timeout:
				raise RuntimeError("test_divide_one_newline: timeout")
			
		#Check if the UploadedCorpus is updated
		uc = UploadedCorpus.objects.get(corpus_id=corpus_id)
		self.assertIs(uc.current_task, None)
		corpuses_history = uc.corpuses_history["corpuses_history"]
		self.assertEqual(len(corpuses_history), 3)

		last_corpus = corpuses_history[-1]
		p0 = last_corpus["paragraphs"][0]
		self.assertEqual(p0["pstate"], "PARSED")
		self.assertNotEqual(p0["token_delimiters"], "")
		self.assertIsNotNone(p0["token_delimiters"])

		tokens = p0["tokens"]
		self.assertEqual(len(tokens), 9)
		t0, t1 = tokens[0], tokens[1]

		self.assertFalse(t0["is_delimiter"])
		self.assertTrue(t1["is_delimiter"])
		self.assertIsNotNone(t0["txt"])
