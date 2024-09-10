from dependency_injector import containers, providers

from app.middleware.auth_middleware import secret_key, algorithm
from app.persistence.repositories.synthetic_data_repository import SyntheticDataRepository
from app.persistence.repositories.user_repository import UserRepository
from app.use_cases.services.data_services import DataService
from app.use_cases.evaluators.evaluators import Evaluator
from app.use_cases.factories.factories import SynthesizerFactory
from app.utils.password_hasher import PasswordHasher
from app.core.config import settings
from app.use_cases.services.jwt_service import JWTService


class AppContainer(containers.DeclarativeContainer):
    """Dependency Injection Container"""

    wiring_config = containers.WiringConfiguration(modules=["app.presentation.controllers.auth_controller", "app.presentation.controllers.synthetic_data_controller"])

    # Repositories
    synthetic_data_repository = providers.Factory(SyntheticDataRepository)
    user_repository = providers.Factory(UserRepository)

    # Services
    synthesizer_factory = providers.Factory(SynthesizerFactory)
    evaluator = providers.Factory(Evaluator)

    # Services that are Singleton ( to be asked )
    password_hasher = providers.Singleton(PasswordHasher)
    jwt_service = providers.Singleton(JWTService, secret_key= settings.secret_key, algorithm=settings.algorithm)

    # Data Service
    data_service = providers.Factory(
        DataService,
        factory=synthesizer_factory,
        evaluator=evaluator,
        csv_path=settings.csv
    )
