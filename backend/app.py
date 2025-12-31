from flask import Flask, request
from flask_restx import Api, Resource, fields

app = Flask(__name__)

api = Api(
    app,
    version="1.0",
    title="My API",
    description="Simple Posts API",
    doc="/docs"  # Swagger UI
)

ns = api.namespace("posts", description="Post operations")

# In-memory data
posts = [
    {"id": 1, "title": "Hello", "content": "First post"},
    {"id": 2, "title": "Another", "content": "Second post"}
]

# -------------------- Models --------------------
post_model = api.model(
    "Post",
    {
        "id": fields.Integer(readOnly=True, example=1),
        "title": fields.String(required=True, example="Hello"),
        "content": fields.String(required=True, example="First post"),
    }
)

post_input_model = api.model(
    "PostInput",
    {
        "title": fields.String(required=True),
        "content": fields.String(required=True),
    }
)

post_update_model = api.model(
    "PostUpdate",
    {
        "title": fields.String(),
        "content": fields.String(),
    }
)

error_model = api.model(
    "Error",
    {"error": fields.String(example="Post not found")}
)

# -------------------- /posts --------------------
@ns.route("")
class PostList(Resource):

    @ns.marshal_list_with(post_model)
    @ns.param("sort", "Sort by title or content")
    @ns.param("direction", "asc or desc", default="asc")
    def get(self):
        """Get all posts (optional sorting)"""
        sort_field = request.args.get("sort")
        direction = request.args.get("direction", "asc")

        result = posts.copy()
        if sort_field in ["title", "content"]:
            result.sort(
                key=lambda p: p[sort_field].lower(),
                reverse=(direction == "desc")
            )
        return result

    @ns.expect(post_input_model, validate=True)
    @ns.marshal_with(post_model, code=201)
    def post(self):
        """Create a new post"""
        data = api.payload
        new_id = max(p["id"] for p in posts) + 1 if posts else 1

        new_post = {
            "id": new_id,
            "title": data["title"],
            "content": data["content"]
        }
        posts.append(new_post)
        return new_post, 201


# -------------------- /posts/search --------------------
@ns.route("/search")
class PostSearch(Resource):

    @ns.marshal_list_with(post_model)
    @ns.param("title", "Search by title")
    @ns.param("content", "Search by content")
    def get(self):
        """Search posts"""
        title_query = request.args.get("title", "").lower()
        content_query = request.args.get("content", "").lower()

        return [
            p for p in posts
            if (title_query and title_query in p["title"].lower())
            or (content_query and content_query in p["content"].lower())
        ]


# -------------------- /posts/<id> --------------------
@ns.route("/<int:post_id>")
@ns.response(404, "Post not found", error_model)
class PostItem(Resource):

    @ns.marshal_with(post_model)
    def delete(self, post_id):
        """Delete a post"""
        global posts
        post = next((p for p in posts if p["id"] == post_id), None)
        if not post:
            api.abort(404, "Post not found")

        posts = [p for p in posts if p["id"] != post_id]
        return post

    @ns.expect(post_update_model, validate=True)
    @ns.marshal_with(post_model)
    def put(self, post_id):
        """Update a post"""
        post = next((p for p in posts if p["id"] == post_id), None)
        if not post:
            api.abort(404, "Post not found")

        data = api.payload
        post.update({k: v for k, v in data.items() if v is not None})
        return post


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(debug=True, port=5001)
