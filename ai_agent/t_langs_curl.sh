curl -X POST https://api.smith.langchain.com/runs \
 -H "x-api-key: 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" \
 -H "Content-Type: application/json" \
 -d '{
   "name": "Sobhan testing Run",
   "project_name": "lang-hot-20250613",
   "run_type": "chain",
   "inputs": {"input": "test"},
   "outputs": {"output": "success"},
   "extra": {},
   "tags": ["api_test"]
 }'
