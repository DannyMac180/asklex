from flask import Flask, request, render_template
import os
import pinecone

app = Flask(__name__)
pinecone.init(api_key=os.getenv("PINECONE_API_KEY"),
              environment=os.getenv("PINECONE_ENV"))
index_name = "asklex"

@app.route('/', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form['query']
        results = pinecone.search(index_name, query, k=10)
        return render_template('results.html', results=results)
    return render_template('search.html')

if __name__ == '__main__':
    app.run()