"""Marshmallow schemas for auth endpoints."""

from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))


class TokenRefreshSchema(Schema):
    refresh_token = fields.Str(required=True)
