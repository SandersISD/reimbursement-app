"""
Simple test script to verify the application setup.
Run this after installation to check if everything works.
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError as e:
        print(f"❌ Flask import failed: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy imported successfully")
    except ImportError as e:
        print(f"❌ Flask-SQLAlchemy import failed: {e}")
        return False
    
    try:
        import flask_wtf
        print("✅ Flask-WTF imported successfully")
    except ImportError as e:
        print(f"❌ Flask-WTF import failed: {e}")
        return False
    
    try:
        import wtforms
        print("✅ WTForms imported successfully")
    except ImportError as e:
        print(f"❌ WTForms import failed: {e}")
        return False
    
    return True

def test_app_creation():
    """Test if the Flask app can be created."""
    print("\nTesting app creation...")
    
    try:
        from app import create_app
        app = create_app('testing')
        print("✅ Flask app created successfully")
        
        with app.app_context():
            from models import db
            db.create_all()
            print("✅ Database tables created successfully")
        
        return True
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        return False

def test_directories():
    """Test if required directories exist."""
    print("\nTesting directories...")
    
    required_dirs = ['uploads', 'instance', 'templates']
    
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ Directory '{directory}' exists")
        else:
            print(f"❌ Directory '{directory}' missing")
            return False
    
    return True

def test_templates():
    """Test if all required templates exist."""
    print("\nTesting templates...")
    
    required_templates = [
        'templates/base.html',
        'templates/index.html',
        'templates/claim_form.html',
        'templates/item_form.html',
        'templates/confirmation.html',
        'templates/404.html',
        'templates/500.html'
    ]
    
    for template in required_templates:
        if os.path.exists(template):
            print(f"✅ Template '{template}' exists")
        else:
            print(f"❌ Template '{template}' missing")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Reimbursement App Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_directories,
        test_templates,
        test_app_creation
    ]
    
    all_passed = True
    
    for test in tests:
        if not test():
            all_passed = False
            print()
    
    print("\n" + "=" * 40)
    
    if all_passed:
        print("🎉 All tests passed! Your app is ready to run.")
        print("\nNext steps:")
        print("1. Run: python init_db.py")
        print("2. Run: python app.py")
        print("3. Open: http://localhost:5000")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
