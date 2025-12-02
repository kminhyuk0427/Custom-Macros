import sys
import os

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, application_path)
sys.path.insert(0, os.path.join(application_path, 'modules'))

def main():
    try:
        import config
        from app import macroApp
        
        app = macroApp()
        
        if not app.validate_config(config):
            sys.exit(1)
        
        app.load_config(config)
        app.run()
        
    except KeyboardInterrupt:
        sys.exit(0)
        
    except ImportError:
        sys.exit(1)
        
    except:
        sys.exit(1)

if __name__ == "__main__":
    main()