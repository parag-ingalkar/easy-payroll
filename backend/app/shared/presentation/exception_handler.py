from app.features.auth.presentation.exception_handler import register_auth_exception_handlers


def register_exception_handlers(app) -> None:
    register_auth_exception_handlers(app)
