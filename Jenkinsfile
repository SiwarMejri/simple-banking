stage('Validation des Imports') {
    steps {
        echo "🔍 Validation des imports Python..."
        script {
            def validationResult = sh(
                script: """
                    set -e
                    . ${VENV_DIR}/bin/activate
                    export PYTHONPATH=${WORKSPACE}/src/app
                    
                    # Validation simple des imports
                    python3 -c "
import sys
try:
    from src.app.models.user import UserModel
    from src.app.models.account import AccountModel  
    from src.app.models.transaction import TransactionModel
    print('✅ Import des modèles individuels réussi')
    
    from src.app.models import User, Account, Transaction
    print('✅ Import via __init__.py réussi')
    
    from src.app.main import app
    print('✅ Import de l\\\\'app principale réussi')
    
    print('🎉 Tous les imports fonctionnent')
    sys.exit(0)
except ImportError as e:
    print(f'❌ Erreur: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
                    "
                """,
                returnStatus: true
            )

            if (validationResult != 0) {
                error("❌ Validation des imports échouée")
            } else {
                echo "✅ Tous les imports sont valides"
            }
        }
    }
}
