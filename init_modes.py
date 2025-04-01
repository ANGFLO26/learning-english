from app import app, db, LearningMode

def init_learning_modes():
    # Define the three learning modes
    modes = [
        {
            'name': 'Listen & Write',
            'description': 'Listen to the word and write its meaning'
        },
        {
            'name': 'View & Pronounce',
            'description': 'View the word and practice pronunciation'
        },
        {
            'name': 'Test Knowledge',
            'description': 'Test your understanding with exercises'
        }
    ]
    
    # Create modes if they don't exist
    with app.app_context():
        for mode_data in modes:
            mode = LearningMode.query.filter_by(name=mode_data['name']).first()
            if not mode:
                mode = LearningMode(**mode_data)
                db.session.add(mode)
        
        try:
            db.session.commit()
            print("Learning modes initialized successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Error initializing modes: {str(e)}")

if __name__ == '__main__':
    init_learning_modes() 