class DomainException(Exception):
    pass


class UserMustHaveAtLeastOneRole(DomainException):
    pass


class RoleNotAssigned(DomainException):
    pass


class RoleAlreadyAssigned(DomainException):
    pass


class DeactivatedUser(DomainException):
    pass


class InsufficientPrivileges(DomainException):
    pass


class EmailAlreadyInUse(DomainException):
    pass


class UsernameAlreadyInUse(DomainException):
    pass


class InvalidCredentials(DomainException):
    pass
