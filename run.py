from app import create_app, db
from app.models.user import User # Assuming User model will be created
from app.models.cylinder import Cylinder
import unittest # Added
from config import Config, TestConfig # Added

app = create_app(Config) # Ensure default app uses Config

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Cylinder': Cylinder}

@app.cli.command("test") # Added
def test(): # Added
    """Runs the unit tests.""" # Added
    loader = unittest.TestLoader() # Added
    tests = loader.discover('tests') # Added
    runner = unittest.TextTestRunner(verbosity=2) # Added
    result = runner.run(tests) # Added
    if result.wasSuccessful(): # Added
        return 0 # Added
    return 1 # Added

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)
