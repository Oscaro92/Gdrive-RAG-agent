# * import libraries
import os, uuid, json, shutil
from pathlib import Path
from decouple import config
from langchain.chat_models import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

# * import tools
from gdrive import Gdrive

gdrive = Gdrive()
BASE_DIR = Path(__file__).resolve().parent


class AgentGDrive():
    def __init__(self):
        temperature = 0.0
        model = "gpt-4o-mini"
        os.environ["OPENAI_API_KEY"] = config('OPENAI_API_KEY')

        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


    def load(self, path:str)->list[Document]:
        '''
        Load file in Google Drive

        :param path: parent path
        :return: list of files (Document)
        '''

        docs = []

        files = gdrive.getPDFFiles(path)

        for file in files:
            docs.append(Document(page_content=file['page_content'], metadata=file['metadata']))

        return docs


    def saveDoc(self, docs: list):
        '''
        vector & save docs in ChromaDB. Add or update the document

        :param docs: list of documents
        :return: void
        '''

        if os.path.exists("chroma"):
            shutil.rmtree("chroma")

        db = Chroma(persist_directory="chroma", embedding_function=self.embeddings)

        # Add or Update the documents.
        existing_items = db.get(include=[])
        existing_ids = set(existing_items["ids"])
        print(f"Number of existing documents in DB: {len(existing_ids)}")

        if len(docs):
            print(f"👉 Adding new documents: {len(docs)}")
            new_chunk_ids = [chunk.metadata["id"] for chunk in docs]
            db.add_documents(docs, ids=new_chunk_ids)
            db.persist()
        else:
            print("✅ No new documents to add")


    def similarity(self, query:str)->list:
        '''
        get doc with similarity score

        :param query: user request
        :return: list of similarities
        '''

        db = Chroma(persist_directory="chroma", embedding_function=self.embeddings)
        results = db.similarity_search_with_relevance_scores(query)

        result_filter = [result for result in results if result[1] >= 0.20]

        return result_filter


    def chat(self, docs: list, query: str)->str:
        '''
        get response of LLM

        :param docs: list of docs similar
        :param query: user request
        :return: chatGPT response
        '''

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "Tu es un assistant qui a les documents suivant :  {docs}. \n Dans chaque document il y a la variable page_content avec la contenu du document, metadatas avec la source/ l'url et le title du document, et page qui indique le nombre de page du document\n"
                    "A partir des données des documents tu dois répondre aux questions posés.",
                ),
                ("human", "{query}"),
            ]
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "docs": docs,
                "query": query,
            }
        )

        return response.content