"""
Template handling functionality for the GUI layer.
"""
from flask import render_template, flash, get_flashed_messages

class TemplateHandler:
    def __init__(self, app):
        self.app = app
    
    def render_with_user(self, template, **kwargs):
        """Render a template with common user-related variables."""
        from flask_login import current_user
        kwargs['current_user'] = current_user
        kwargs['messages'] = get_flashed_messages()
        return render_template(template, **kwargs)
    
    def render_with_flash(self, template, message, category='info', **kwargs):
        """Render a template with a flash message."""
        flash(message, category)
        return self.render_with_user(template, **kwargs)
    
    def render_error(self, template, error_message, **kwargs):
        """Render an error template with an error message."""
        return self.render_with_flash(template, error_message, category='error', **kwargs) 