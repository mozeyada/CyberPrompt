// MongoDB initialization script
db = db.getSiblingDB('genai_bench');

// Create collections
db.createCollection('prompts');
db.createCollection('runs');
db.createCollection('output_blobs');
db.createCollection('audits');
db.createCollection('baselines');
db.createCollection('source_documents');

// Research indexes for performance
db.prompts.createIndex({"scenario": 1, "metadata.length_bin": 1});
db.prompts.createIndex({"source": 1});
db.prompts.createIndex({"metadata.word_count": 1});
db.prompts.createIndex({"category": 1});

// Source documents indexes
db.source_documents.createIndex({"doc_id": 1}, {"unique": true});
db.source_documents.createIndex({"source_type": 1});
db.source_documents.createIndex({"created_at": -1});

print('Database initialized with research indexes');
