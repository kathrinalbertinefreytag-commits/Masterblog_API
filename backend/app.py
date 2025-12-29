from flask import Flask, request, jsonify

app = Flask(__name__)

posts = [
    {"id": 1, "title": "Hello", "content": "First post"},
    {"id": 2, "title": "Another", "content": "Second post"}
]


@app.route("/api/posts", methods=["POST"])
def add_post():
    """adding a post to the database"""
    data = request.get_json()

    #validating
    if not data or "title" not in data or "content" not in data:
        return jsonify({"error": "title and content are required"}), 400

    #creating new id
    new_id = max(post["id"] for post in posts) + 1 if posts else 1

    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }

    posts.append(new_post)

    return jsonify(new_post), 201

@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """deletes post with given id"""
    global posts

    # Post suchen
    post = next((p for p in posts if p["id"] == post_id), None)

    if post is None:
        return jsonify({"error": "Post not found"}), 404

    posts = [p for p in posts if p["id"] != post_id]

    return jsonify(post), 200


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """updating post by searching post by id and actualizing the fields bei post"""
    #searching post
    post = None
    for p in posts:
        if p["id"] == post_id:
            post = p
            break

    #if post does not exist
    if post is None:
        return jsonify({"error": "Post not found"}), 404

    #loading JsonData
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    #actualizing given fields
    if "title" in data:
        post["title"] = data["title"]

    if "content" in data:
        post["content"] = data["content"]


    return jsonify(post), 200

from flask import Flask, jsonify, request

app = Flask(__name__)



@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """searching posts by title or content"""
    title_query = request.args.get("title", "").lower()
    content_query = request.args.get("content", "").lower()

    filtered_posts = []
    for post in posts:
        title_match = title_query in post["title"].lower() if title_query else False
        content_match = content_query in post["content"].lower() if content_query else False

        if title_match or content_match:
            filtered_posts.append(post)

    return jsonify(filtered_posts), 200

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/api/posts", methods=["GET"])
def get_posts():
    """sorts posts by title or content"""
    sort_field = request.args.get("sort")       # "title" or "content"
    direction = request.args.get("direction", "asc")  # "asc" oder "desc"?

    sorted_posts = posts.copy()

    if sort_field in ["title", "content"]:
        reverse = True if direction == "desc" else False
        sorted_posts.sort(key=lambda p: p[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
