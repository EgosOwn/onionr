# Onionr Block Spec v2.0.0

# Block Description

Onionr Blocks are the primary means of sharing information in Onionr. Blocks are identified by a single hash value of their entire contents, using SHA3_256.

Blocks contain a JSON metadata section followed by a line break, with the main data section comprising the rest.

In the future, the specification will likely be updated to use flags and MessagePack instead of JSON with english keys.

# Encryption and Signatures

Onionr blocks may be encrypted or signed. In the reference client, this is done with libsodium, for both asymmetric and symmetric encryption.

Unlike many similar projects, blocks may completely be in plaintext, making Onionr suitable for sharing information publicly.

# Metadata Section

The metadata section has the following fields. If a block contains any other field, it must be considered invalid. All metadata fields are technically optional, but many are useful and essentially necessary for most use cases.

## meta

Max byte size (when in escaped json string format): 1000

Meta is a string field which can contain arbitrary sub fields. It is intended for applications and plugins to use it for arbitrary metadata information. If the data section is encrypted or signed, the meta section also is.

Common meta fields, such as 'type' are used by the reference Onionr client to describe the type of a block.

## sig (optional)

Max byte size: 200

Sig is a field for storing public key signatures of the block, typically ed25519. In the reference client, this field is a base64 encoded signature of the meta field combined with the block data. (**Therefore, information outside of the meta and data fields cannot be trusted to be placed there by the signer, although it can still be assured that the particular block has not been modified.**)

Note: the max field size is larger than a EdDSA signature (which is what is typically used) in order to allow other primitives for signing in alternative implementations or future versions.

## signer (optional, necessary if sig is present)

Max byte size: 200

Signer is a field for specifying the public key which signed the block. In the reference client this is a base64 encoded ed25519 public key.

## time (mandatory)

Max byte size: 10

Time is an integer field for specifying the time of which a block was created. The trustworthiness of this field is based on one's trust of the block creator, however blocks with a time field set in the future at the point of block receipt (past a reasonable clock skew) are thrown out by the reference client.

## expire (optional)

Max byte size: 10

Expire is an integer field for specifying the time of which the block creator has indicated that the block should be deleted. The purpose of this is for voluntarily freeing the burden of unwanted blocks on the Onionr network, rather than security/privacy (since blocks could be trivially kept past expiration). Regardless, the reference client deletes blocks after a preset time if the expire field is either not set or longer than the preset time.

## pow (effectively mandatory)

Max byte size: 1000

Pow is a field for placing the nonce found to make a block meet a target proof of work. In theory, a block could meet a target without a random token in this field.

## encryptType (optional)

encryptType is a field to specify the mode of encryption for a block. The values supported by Onionr are 'asym' and 'sym'.
