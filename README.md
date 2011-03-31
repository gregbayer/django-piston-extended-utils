# About

django-piston-extended-utils is a set of helper functions that extend the django piston response utilities.

* rc_factory (rc) - just like the original with a few more options
* error_type_factory (ec) - error types with related response code (all rc.BAD_REQUEST for now)
* success_resp - generate json response with optional data and message (status_code = 200)
* error_resp - generate json response with optional error type and message
* reformat_form_validation_errors - flatten django form error values to allow them to be emitted properly


# Supported Response Codes

A few more than the original.

    ALL_OK = ('OK', 200)
    CREATED = ('Created', 201)
    DELETED = ('', 204)
    NOT_MODIFIED = ('Not Modified', 304)
    BAD_REQUEST = ('Bad Request', 400)
    UNAUTHORIZED = ('Unauthorized', 401)
    FORBIDDEN = ('Forbidden', 403)
    NOT_FOUND = ('Not Found', 404)
    DUPLICATE_ENTRY = ('Conflict/Duplicate', 409)
    NOT_HERE = ('Gone', 410)
    INTERNAL_SERVER_ERROR = ('Internal Server Error', 500)
    NOT_IMPLEMENTED = ('Not Implemented', 501)
    THROTTLED = ('Throttled', 503)


# Supported error types

These error types help explain why a request was bad.  Modeled after that Facebook API error response format.

    FB_TOKEN_EXCEPTION = (rc.BAD_REQUEST, "FBTokenException")
    FB_AUTH_EXCEPTION = (rc.BAD_REQUEST, "FBAuthException")
    DIRECT_AUTH_EXCEPTION = (rc.BAD_REQUEST, "DirectAuthException")
    PARAMETER_VALIDATION_EXCEPTION = (rc.BAD_REQUEST, "ParameterValidationException")
    BAD_REQUEST_EXCEPTION = (rc.BAD_REQUEST, "BadRequestException")


# Dependencies: 
* [django piston](https://bitbucket.org/jespern/django-piston)


# Extends:  
* [piston.utils](https://bitbucket.org/jespern/django-piston/src/c4b2d21db51a/piston/utils.py)


# Example

\# handlers.py

    class BasicApiTokenHandler(BaseHandler):
        """
        Request an API token. \n
        Required Authentication: HTML Basic Auth
        """
        allowed_methods = ('GET',)
        model = ApiToken
        fields = ('token', 'created')
        
        def read(self, request):
            """
            Returns a valid api token for the authenticated user.
            Creates a new token if necessary.
            
            Headers: \n
            - Requires user's username and password via HTTB Basic Authentication header
            
            Response codes / error messages: \n
            - 200 (OK) --- Returned test data.
            - 401 (Unauthorized) --- HTML Basic Auth is invalid.
            - 500 (Internal Server Error): User is invalid.
            
            Return data: \n
            - API Token (token, created)
            """
            if request.user:
                if not request.user.is_active:
                    return error_resp("This account is inactive.", error_type=et.DIRECT_AUTH_EXCEPTION)
                apiToken = get_api_token(request.user)
                return success_resp(apiToken)
            else:
                return error_resp('User is invalid.', resp=rc.INTERNAL_SERVER_ERROR)

        @classmethod
        def resource_uri(self):
            return ('basic_api_token', [])