import strawberry


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_flavour(self, name: str, info: strawberry.Info) -> bool:
        return True
