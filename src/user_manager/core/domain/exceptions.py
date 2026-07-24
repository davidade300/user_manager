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
