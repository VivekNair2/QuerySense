import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage
from llama_index.core.tools import FunctionTool

def text_rag(query, uploaded_file=None):
    PERSIST_DIR = "./storage"
    
    if not os.path.exists(PERSIST_DIR) or uploaded_file:
        # Load documents from the uploaded file or the default data folder
        if uploaded_file:
            # Save the uploaded file temporarily
            temp_path = os.path.join(PERSIST_DIR, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Use SimpleDirectoryReader to load data from the uploaded file
            documents = SimpleDirectoryReader(input_files=[temp_path]).load_data()
            os.remove(temp_path)  # Remove the temp file after loading data
        else:
            # Default to loading from the "data" folder if no file is uploaded
            documents = SimpleDirectoryReader("data").load_data()
        
        # Create and persist the index
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist(persist_dir=PERSIST_DIR)
    else:
        # Load the existing index
        storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
        index = load_index_from_storage(storage_context)

    # Perform query on the index
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return response

text_rag_tool = FunctionTool.from_defaults(
    fn=text_rag,
    name="text_rag",
    description="Retrieval Augmented Generation tool to handle text-based PDF queries."
)