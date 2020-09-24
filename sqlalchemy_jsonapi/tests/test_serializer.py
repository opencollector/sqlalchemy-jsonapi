from app import api
from sqlalchemy_jsonapi import JSONAPI
from sqlalchemy_jsonapi.errors import BadRequestError
import uuid
import pytest


def test_include_different_types_same_id(session, comment):
    new_id = uuid.uuid4()
    comment.post.id = new_id
    comment.author.id = new_id
    comment.post_id = new_id
    comment.author_id = new_id
    session.commit()

    r = api.serializer.get_resource(
        session, {'include': 'post,author'}, 'blog-comments', comment.id)
    assert len(r.data['included']) == 2


def test_no_dasherize(session, comment):
    api.serializer = JSONAPI(api.serializer.base, api.serializer.prefix,
                             options={'dasherize': False})

    r = api.serializer.get_resource(session, {}, 'blog_comments', comment.id)
    assert r.data['data']['type'] == 'blog_comments'

    api.serializer = JSONAPI(api.serializer.base, api.serializer.prefix)


def test_extra_keys(session, comment):
    api.serializer = JSONAPI(api.serializer.base, api.serializer.prefix,
                options={'dasherize': False, 'disallow_extra_attributes': True})

    with pytest.raises(BadRequestError):
        api.serializer.patch_resource(session, {'data': {'type': 'blog_comments', 'id': comment.id, 'attributes': {'nonexistent': False}}}, 'blog_comments', comment.id)


def test_field_name_filter(session, comment):
    api.serializer = JSONAPI(api.serializer.base, api.serializer.prefix,
                options={'field_name_filter': lambda x: "$" + x, 'disallow_extra_attributes': True})

    api.serializer.patch_resource(session, {'data': {'type': 'blog-comments', 'id': comment.id, 'attributes': {'$content': 'hey'}}}, 'blog-comments', comment.id)
