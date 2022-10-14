class IdentitySet(set):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def __contains__(self, ob: 'Identity') -> bool:
        for identity in self:
            if bytes(identity.key) == bytes(ob.key):
                return True
        return False

    def add(self, identity):
        for existing_iden in self:

            if bytes(existing_iden.key) == bytes(identity.key):
                return
        super().add(identity)

    def remove(self, identity):
        remove_idens = []
        for existing_iden in self:
            if bytes(existing_iden.key) == bytes(identity.key):
                remove_idens.append(existing_iden)
        for remove_iden in remove_idens:
            super().remove(remove_iden)


# Set of identites within N-distance trust

identities = IdentitySet()

def serialize_identity_set():
    serialized_idens = []
    for identity in list(identities):
        serialized_idens.append(identity.serialize())
    return serialized_idens

serialize_identity_set.json_compatible = True