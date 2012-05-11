################################################################################
# extended_piston_utils.py
# 
# Created by Greg Bayer <greg@gbayer.com>.
# Open sourced at http://github.com/gregbayer/django-piston-extended-utils
################################################################################

import logging

from piston import utils
from piston.emitters import Emitter
from piston.handler import typemapper
from django.http import HttpRequest
from django.http import HttpResponse


# Response code helper with some corrections & additions from standard the Piston class it extends
class rc_factory(utils.rc_factory):
    """
    Status codes.
    """
    CODES = dict(ALL_OK = ('OK', 200),
                 CREATED = ('Created', 201),
                 DELETED = ('', 204), # 204 says "Don't send a body!"
                 NOT_MODIFIED = ('Not Modified', 304), # There was no new data to return.
                 BAD_REQUEST = ('Bad Request', 400),
                 UNAUTHORIZED = ('Unauthorized', 401), # Authentication credentials were missing or incorrect.
                 FORBIDDEN = ('Forbidden', 403), # The request is understood, but it has been refused.
                 NOT_FOUND = ('Not Found', 404),
                 DUPLICATE_ENTRY = ('Conflict/Duplicate', 409),
                 REQUEST_TIMEOUT = ('Request Timeout', 408),
                 NOT_HERE = ('Gone', 410),
                 INTERNAL_SERVER_ERROR = ('Internal Server Error', 500), # 500 Internal Server Error: Something is broken.
                 NOT_IMPLEMENTED = ('Not Implemented', 501),
                 THROTTLED = ('Throttled', 503), # Also means 'Service Unavailable'
                 )

rc = rc_factory()


class error_type_factory(object):
    """
    Status code, status code msg, exception class
    """
    CODES = dict(
                 FB_TOKEN_EXCEPTION = (rc.BAD_REQUEST, "FBTokenException"),
                 FB_AUTH_EXCEPTION = (rc.BAD_REQUEST, "FBAuthException"),
                 DIRECT_AUTH_EXCEPTION = (rc.BAD_REQUEST, "DirectAuthException"),
                 PARAMETER_VALIDATION_EXCEPTION = (rc.BAD_REQUEST, "ParameterValidationException"),
                 BAD_REQUEST_EXCEPTION = (rc.BAD_REQUEST, "BadRequestException"),
                 )

    def __getattr__(self, attr):
        """
        Returns a fresh `HttpResponse` when getting 
        an "attribute". This is backwards compatible
        with 0.2, which is important.
        """
        try:
            (resp, exception_class) = self.CODES.get(attr)
        except TypeError:
            raise AttributeError(attr)

        return (resp, exception_class)

et = error_type_factory()   


def success_resp(data=None, message=None, headers=None):
    if data:
        if data == [None]:
            data = []
    
    return base_success_resp({'data': data}, message, headers)


def base_success_resp(data=None, message=None, headers=None):
    if not data and not message:
        return None
    
    resp_json = {}
    if data:
        resp_json = data
    if message:
        resp_json['message'] = message
    if headers:
        resp_json['headers'] = headers
    
    return resp_json


def error_resp(message, error_type=None, resp=rc.BAD_REQUEST, status_code=None):
    logging.warn("Status Code " + str(resp.status_code) + ", error_type: " + repr(error_type) + ", message: " + repr(message))
    error_json = {}
    if message and error_type:
        (error_type_resp, error_type) = error_type
        resp = error_type_resp
        error = {}
        error['type'] = error_type
        error['message'] = message
        error_json['error'] = error  
    elif message:
        error = {}
        error['type'] = ''
        error['message'] = message
        error_json['error'] = error
    
    if message or error_type:
        emitter, ct = Emitter.get('json')  #TODO: Make this work for other emitter formats
        srl = emitter(error_json, None, None, None, None)
        rendered_resp = srl.render(HttpRequest())
        final_resp = HttpResponse(rendered_resp, mimetype=ct)
        if status_code:
            final_resp.status_code = status_code
        else:
            final_resp.status_code = resp.status_code
        return final_resp
    else:
        return resp


def base_error_resp(message, error_type=None, resp=rc.BAD_REQUEST, status_code=None):
    logging.warn("Status Code " + str(resp.status_code) + ", error_type: " + repr(error_type) + ", message: " + repr(message))
    error_json = {}
    if message and error_type:
        (error_type_resp, error_type) = error_type
        resp = error_type_resp
        error = {}
        error['type'] = error_type
        error['message'] = message
        error_json['error'] = error
    elif message:
        error = message
    
    if message or error_type:
        emitter, ct = Emitter.get('json')  #TODO: Make this work for other emitter formats
        srl = emitter(error_json, None, None, None, None)
        rendered_resp = srl.render(HttpRequest())
        final_resp = HttpResponse(rendered_resp, mimetype=ct)
        if status_code:
            final_resp.status_code = status_code
        else:
            final_resp.status_code = resp.status_code
        return final_resp
    else:
        return resp


def reformat_form_validation_errors(errors):
#    logging.info("errors: " + repr(errors))
    # Try to flatten key error arrays
    if errors:
        try:
            for (key, value) in errors.items():
                errors[key] = ' '.join(value)
        except:
            logging.exception("Error flattening value arrays for each error key.")
            pass
    return errors


def apply_json_emitter(value_to_emit, handler=None):
    emitter, ct = Emitter.get('json')  #TODO: Make this work for other emitter formats
    handler_fields = None

    if handler:
        handler_fields = handler.fields
    srl = emitter(value_to_emit, typemapper, handler, handler_fields, None)
    json = srl.construct()

    return json


def clean_bool_input(bool_input):
    return_bool = False
    
    if bool_input:
        if type(bool_input) == bool:
            return_bool = bool_input
        else:
            if bool_input.lower() == 'true':
                return_bool = True
    
    return return_bool

