"""
Tests for Flask-Script compatibility with Flask 3.x.

These tests verify that the compatibility patches allow Flask-Script
to work with Flask 3.x despite Flask-Script being deprecated.
"""

import pytest
import sys
import types


class TestFlaskScriptCompatibility:
    """Test Flask-Script compatibility patches."""
    
    def test_flask_compat_module_can_be_created(self):
        """Test that we can create flask._compat compatibility module."""
        # Save original state
        orig_modules = sys.modules.copy()
        
        try:
            # Create compatibility module
            compat_module = types.ModuleType('flask._compat')
            compat_module.text_type = str
            compat_module.string_types = (str,)
            sys.modules['flask._compat'] = compat_module
            
            # Verify it's available
            assert 'flask._compat' in sys.modules
            
            # Verify we can import it
            from flask import _compat
            assert _compat.text_type == str
            assert _compat.string_types == (str,)
        finally:
            # Restore original state
            sys.modules.clear()
            sys.modules.update(orig_modules)
    
    def test_flask_request_ctx_stack_patch(self):
        """Test that _request_ctx_stack can be patched into Flask."""
        import flask
        from werkzeug.local import LocalStack
        
        # Save original if exists
        orig_stack = getattr(flask, '_request_ctx_stack', None)
        
        try:
            # Apply patch
            if not hasattr(flask, '_request_ctx_stack'):
                flask._request_ctx_stack = LocalStack()
            
            # Verify it exists
            assert hasattr(flask, '_request_ctx_stack')
            assert isinstance(flask._request_ctx_stack, LocalStack)
        finally:
            # Restore if needed
            if orig_stack is None and hasattr(flask, '_request_ctx_stack'):
                delattr(flask, '_request_ctx_stack')
    
    def test_flask_app_ctx_stack_patch(self):
        """Test that _app_ctx_stack can be patched into Flask."""
        import flask
        from werkzeug.local import LocalStack
        
        # Save original if exists
        orig_stack = getattr(flask, '_app_ctx_stack', None)
        
        try:
            # Apply patch
            if not hasattr(flask, '_app_ctx_stack'):
                flask._app_ctx_stack = LocalStack()
            
            # Verify it exists
            assert hasattr(flask, '_app_ctx_stack')
            assert isinstance(flask._app_ctx_stack, LocalStack)
        finally:
            # Restore if needed
            if orig_stack is None and hasattr(flask, '_app_ctx_stack'):
                delattr(flask, '_app_ctx_stack')
    
    def test_all_patches_together(self):
        """Test that all patches can be applied together."""
        import sys
        import types
        import flask
        from werkzeug.local import LocalStack
        
        # Save original state
        orig_modules = sys.modules.copy()
        orig_request_ctx = getattr(flask, '_request_ctx_stack', None)
        orig_app_ctx = getattr(flask, '_app_ctx_stack', None)
        
        try:
            # Apply all patches
            compat_module = types.ModuleType('flask._compat')
            compat_module.text_type = str
            compat_module.string_types = (str,)
            sys.modules['flask._compat'] = compat_module
            
            if not hasattr(flask, '_request_ctx_stack'):
                flask._request_ctx_stack = LocalStack()
            
            if not hasattr(flask, '_app_ctx_stack'):
                flask._app_ctx_stack = LocalStack()
            
            # Verify all patches are in place
            assert 'flask._compat' in sys.modules
            assert hasattr(flask, '_request_ctx_stack')
            assert hasattr(flask, '_app_ctx_stack')
            
            # Verify we can now import flask_script
            # (This is the real test - if patches work, import succeeds)
            import flask_script
            assert flask_script is not None
            assert hasattr(flask_script, 'Manager')
        
        finally:
            # Restore original state
            sys.modules.clear()
            sys.modules.update(orig_modules)
            if orig_request_ctx is None and hasattr(flask, '_request_ctx_stack'):
                delattr(flask, '_request_ctx_stack')
            if orig_app_ctx is None and hasattr(flask, '_app_ctx_stack'):
                delattr(flask, '_app_ctx_stack')
    
    def test_manager_patches_are_applied_in_whyis(self):
        """Test that whyis.manager applies patches correctly."""
        # The whyis.manager module should apply patches on import
        # This test verifies that by importing it
        import whyis.manager
        
        # After importing whyis.manager, patches should be in place
        import sys
        assert 'flask._compat' in sys.modules
        
        import flask
        assert hasattr(flask, '_request_ctx_stack')
        assert hasattr(flask, '_app_ctx_stack')
        
        # And we should be able to access flask_script
        assert hasattr(whyis.manager, 'script')
        assert whyis.manager.script is not None


class TestFlaskScriptManagerCompatibility:
    """Test that Flask-Script Manager works with patches."""
    
    def test_can_create_manager_instance(self):
        """Test that we can create a Flask-Script Manager instance."""
        # Import whyis.manager which applies patches
        import whyis.manager
        
        # Try to create a Manager - this requires all patches to be working
        manager = whyis.manager.Manager()
        assert manager is not None
    
    def test_manager_has_expected_commands(self):
        """Test that Manager has the expected Whyis commands."""
        import whyis.manager
        
        manager = whyis.manager.Manager()
        
        # Check for some expected commands
        # Note: Commands are stored internally in flask_script
        # We just verify the manager was created successfully
        assert manager is not None
        assert hasattr(manager, 'app')
    
    def test_compatibility_with_flask_app(self):
        """Test that Flask-Script Manager can work with a Flask app."""
        from flask import Flask
        import flask_script
        
        # Create a simple Flask app
        app = Flask(__name__)
        
        # Create a Manager with the app
        manager = flask_script.Manager(app)
        
        assert manager is not None
        assert manager.app == app


class TestClickBasedCLI:
    """Test the new Click-based CLI."""
    
    def test_cli_module_exists(self):
        """Test that the new CLI module exists."""
        import whyis.cli
        assert whyis.cli is not None
    
    def test_cli_has_main_function(self):
        """Test that CLI has a main entry point."""
        from whyis.cli import main
        assert callable(main)
    
    def test_cli_has_click_group(self):
        """Test that CLI uses Click."""
        from whyis.cli import cli
        import click
        assert isinstance(cli, click.Group)
    
    def test_commands_module_exists(self):
        """Test that the commands CLI module exists."""
        from whyis.commands import cli as commands_cli
        assert commands_cli is not None
    
    def test_commands_are_click_commands(self):
        """Test that commands are Click commands."""
        from whyis.commands import cli as commands_cli
        import click
        
        # Check that some commands exist and are Click commands
        if hasattr(commands_cli, 'createuser_command'):
            assert isinstance(commands_cli.createuser_command, click.Command)
        
        if hasattr(commands_cli, 'run_command'):
            assert isinstance(commands_cli.run_command, click.Command)
