from dependency_injector import containers, providers

from app.middleware.auth_middleware import secret_key, algorithm
from app.persistence.repositories.synthetic_data_repository import SyntheticDataRepository
from app.persistence.repositories.task_status_repository import TaskStatusRepository
from app.persistence.repositories.user_repository import UserRepository
from app.use_cases.services.data_service import DataService
from app.use_cases.evaluators.evaluators import Evaluator
from app.use_cases.factories.factories import SynthesizerFactory
from app.use_cases.tasks.data_tasks import DataTask
from app.use_cases.services.task_status_service import TaskStatusService
from app.utils.password_hasher import PasswordHasher
from app.core.config import settings
from app.use_cases.services.jwt_service import JWTService

from app.persistence.repositories.result_repository import ResultRepository
from app.use_cases.services.result_service import ResultService

class AppContainer(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(modules=["app.presentation.controllers.synthetic_data_controller", "app.presentation.controllers.auth_controller"])

    # Repositories
    synthetic_data_repository = providers.Factory(SyntheticDataRepository)
    user_repository = providers.Factory(UserRepository)
    task_repository = providers.Factory(TaskStatusRepository)
    result_repository = providers.Factory(ResultRepository)

    # Services
    synthesizer_factory = providers.Factory(SynthesizerFactory)
    evaluator = providers.Factory(Evaluator)
    task_status_service = providers.Factory(TaskStatusService, task_repository=task_repository)
    result_service = providers.Factory(ResultService, result_repository=result_repository)

    # Tasks
    data_task = providers.Factory(DataTask)

    # Other services
    password_hasher = providers.Singleton(PasswordHasher)
    jwt_service = providers.Singleton(JWTService, secret_key=settings.secret_key, algorithm=settings.algorithm)

    data_service = providers.Factory(
        DataService,
        factory=synthesizer_factory,
        evaluator=evaluator,
        csv_path=settings.csv
    )
