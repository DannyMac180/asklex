from flask import Flask, request, render_template
import os
import pinecone
import openai

app = Flask(__name__)
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"),
              environment=os.getenv("PINECONE_ENV"))
index = pinecone.Index('asklex')

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        print(query)

        try:
            embed = openai.Embedding.create(input=query, engine="text-embedding-ada-002")
            query = embed["data"][0]["embedding"]
            results = index.query(query, top_k=5, include_values=False, include_metadata=True)
            print(results)
            return render_template('results.html', results=results)
        except Exception as e:
            print(e)
            return render_template('search.html')

    return render_template('search.html')

if __name__ == '__main__':
    app.run()