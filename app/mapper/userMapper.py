from ..dto import UserDto


def map_to_user_dto(user):
    name = user['name']
    surname = user['surname']
    email = user['email']
    role = user['role']
    return UserDto(name, surname, email, role)
